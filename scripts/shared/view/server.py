"""本机文件与改动查看器的服务端实现。

由 ``scripts/shared/view/launch.py`` 以子进程方式拉起，不作为包被 import。服务只绑
本机回环地址、路由白名单固定；所有路径参数在 :mod:`workspace` 里解析成绝对路径后断言仍在
仓库根之下。

**写边界**：除「暂存」外，服务对被查看仓库不执行任何写操作。唯一的写入口是
``POST /api/stage``（:meth:`ViewerRequestHandler.do_POST`），它只做 ``git add``；其余写方法
（PUT / DELETE / PATCH）仍然一律 405。它要求 ``Content-Type: application/json``：跨站表单式
POST 是「简单请求」，浏览器会直接发出去，而 JSON 类型会强制预检、预检又必然失败，于是「某个
网页在你不知情时改动你的索引」这条路径被封住。要开新的写口之前，请先读
``docs/guides/file-viewer.md`` 的「它只能看」那一节——那条边界是用户拍板收窄过的。

空闲回收：服务按「最后一次请求时间」计时，超过时限即优雅退出并清理登记文件。页面
刻意不做心跳轮询，因此「关掉标签页」即等同于进入空闲——这是自动回收路径成立的前提，
给这个页面加轮询会让自动回收静默失效。细节见 ``docs/guides/file-viewer.md``。
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

import instance
import rendering
import workspace
import workspace_read

#: 服务只绑本机回环地址，常量与客户端入口共用同一份定义。
VIEWER_HOST = instance.LOOPBACK_HOST

_ASSETS_DIRECTORY_PATH = Path(__file__).resolve().parent / "assets"
_ASSET_ROUTE_PREFIX = "/assets/"

_STATIC_CONTENT_TYPES_BY_FILENAME = {
    "index.html": "text/html; charset=utf-8",
    "viewer.css": "text/css; charset=utf-8",
    "viewer.js": "application/javascript; charset=utf-8",
}

_READ_METHOD_HANDLER_PREFIX = "do_"

#: 唯一的写入口：方法名与实际路由。写口只有一个、且只做暂存——见
#: :meth:`ViewerRequestHandler.do_POST`。
_WRITE_METHOD_HANDLER_NAME = "do_POST"
_STAGE_ROUTE_PATH = "/api/stage"

#: 写请求体的长度上限。暂存请求只有一个小对象，超出它的都不是本服务的正常调用；不设上限的话，
#: 一句 ``Content-Length: 10GB`` 就足以让服务端在读取时分配内存。
_MAX_WRITE_BODY_BYTES = 64 * 1024

_IDLE_CHECK_INTERVAL_SECONDS = 5.0
_MIN_IDLE_CHECK_INTERVAL_SECONDS = 0.1
_SERVE_POLL_INTERVAL_SECONDS = 0.2


@dataclass(frozen=True)
class ServerConfiguration:
    """一次服务进程的启动配置。

    Attributes:
        repository_root (Path): 被查看仓库的根绝对路径。
        port (int): 监听端口，由客户端入口选定。
        idle_timeout_seconds (float): 空闲回收时限；非正数表示关闭自动回收。
    """

    repository_root: Path
    port: int
    idle_timeout_seconds: float


class ViewerHTTPServer(ThreadingHTTPServer):
    """只读查看器服务：绑定回环地址并持有空闲计时状态。

    Attributes:
        configuration (ServerConfiguration): 本次启动配置。
    """

    # 请求线程是守护线程：退出时不必等浏览器持有的 keep-alive 连接自行断开。
    daemon_threads = True
    # 端口被占用时明确失败，不做地址复用——复用会让新旧实例静默抢同一个端口。
    allow_reuse_address = False

    def __init__(
        self,
        configuration: ServerConfiguration,
        request_handler_class: type[BaseHTTPRequestHandler],
    ) -> None:
        """绑定回环地址并初始化空闲计时。

        Args:
            configuration (ServerConfiguration): 本次启动配置。
            request_handler_class (type[BaseHTTPRequestHandler]): 请求处理器类。
        """
        self.configuration = configuration
        self._activity_lock = threading.Lock()
        self._last_request_monotonic = time.monotonic()
        super().__init__((VIEWER_HOST, configuration.port), request_handler_class)

    @property
    def repository_root(self) -> Path:
        """本实例所服务的仓库根绝对路径。"""
        return self.configuration.repository_root

    def mark_request_served(self) -> None:
        """刷新空闲计时的起点；被拒绝的请求同样算「有请求」。"""
        with self._activity_lock:
            self._last_request_monotonic = time.monotonic()

    def seconds_since_last_request(self) -> float:
        """给出距离最近一次请求经过的秒数。"""
        with self._activity_lock:
            return time.monotonic() - self._last_request_monotonic


class ViewerRequestHandler(BaseHTTPRequestHandler):
    """只读查看器的请求处理器：白名单路由，且只放行读取方法。"""

    server: ViewerHTTPServer

    server_version = "LocalViewServer/1.0"
    sys_version = ""
    # HTTP/1.1 让浏览器复用连接：文件树一次要发若干请求，省掉重复握手。
    protocol_version = "HTTP/1.1"

    def __getattr__(self, attribute_name: str) -> object:
        """把 ``do_<方法>`` 名字解析成对应的处理器：``POST`` 走写口，其余一律拒绝。

        这里刻意不逐个定义写方法（PUT / DELETE / PATCH）对应的处理器名字：写边界的可审查性
        依赖「除暂存之外服务端根本不存在写方法处理入口」这一事实，逐个定义同名方法会让
        「``scripts/shared/view/`` 下搜不到写方法处理器」这类静态断言失去判别力。
        ``http.server`` 的分发正是 ``hasattr(self, "do_" + command)`` 加 ``getattr``，因此按
        前缀返回同一个拒绝处理器即可覆盖其余非读取方法。

        Args:
            attribute_name (str): 被查找的属性名。

        Returns:
            object: 写入口（``POST``）或非读取方法的拒绝处理器。

        Raises:
            AttributeError: 属性名不带 ``do_`` 前缀且确实不存在。
        """
        if attribute_name == _WRITE_METHOD_HANDLER_NAME:
            return self.do_POST
        if attribute_name.startswith(_READ_METHOD_HANDLER_PREFIX):
            return self._refuse_non_read_method
        raise AttributeError(attribute_name)

    def do_GET(self) -> None:  # noqa: N802 - http.server 靠 do_<METHOD> 这个名字分发
        """唯一的读取入口：先刷新空闲计时，再按路由白名单分发。"""
        self.server.mark_request_served()
        try:
            self._dispatch_read_request()
        except workspace.WorkspaceCommandError as read_error:
            self._send_json_payload(500, {"error": f"读取仓库失败：{read_error}"})

    def do_POST(self) -> None:  # noqa: N802 - http.server 靠 do_<METHOD> 这个名字分发
        """唯一的写入口：只做暂存，且只接受 JSON 请求体。

        要求 ``Content-Type: application/json`` 不是为了讲究，而是这里唯一说得通的防线：
        跨站表单式 POST 属于「简单请求」，浏览器会直接发出去（恶意页面读不到响应，但**副作用
        已经发生**）。JSON 类型会强制浏览器先发预检，而本服务不返回任何 CORS 头，预检必然
        失败——于是「某个网页在你不知情时把仓库文件加进索引」这条路径被封住。非 JSON 一律
        415，绝不「宽容地」处理。
        """
        self.server.mark_request_served()
        try:
            self._dispatch_write_request()
        except workspace.WorkspaceCommandError as write_error:
            self._send_json_payload(500, {"error": f"暂存失败：{write_error}"})

    def _refuse_non_read_method(self) -> None:
        """拒绝除暂存之外的写方法：本服务只提供「读」与「暂存」两类操作。"""
        self.server.mark_request_served()
        self._send_json_payload(
            405,
            {
                "error": "拒绝：本服务只接受 GET 请求与暂存用的 POST，"
                "不提供提交、撤销暂存或丢弃改动接口。",
                "method": self.command,
            },
        )

    def _dispatch_read_request(self) -> None:
        """按固定白名单分发读取路由；白名单之外一律 404。"""
        parsed_request_target = urlsplit(self.path)
        route_path = parsed_request_target.path
        query_parameters = parse_qs(parsed_request_target.query)
        repository_root = self.server.repository_root

        if route_path == "/":
            self._serve_static_asset("index.html")
        elif route_path.startswith(_ASSET_ROUTE_PREFIX):
            self._serve_static_asset(route_path.removeprefix(_ASSET_ROUTE_PREFIX))
        elif route_path == "/api/info":
            self._serve_workspace_payload(workspace.build_info_payload(repository_root))
        elif route_path == "/api/tree":
            self._serve_workspace_payload(workspace.build_tree_payload(repository_root))
        elif route_path == "/api/file":
            self._serve_workspace_payload(
                workspace.build_file_payload(
                    repository_root,
                    self._read_query_parameter(query_parameters, "path"),
                )
            )
        elif route_path == "/api/changes":
            self._serve_workspace_payload(workspace.build_changes_payload(repository_root))
        elif route_path == "/api/diff":
            self._serve_workspace_payload(
                workspace.build_diff_payload(
                    repository_root,
                    self._read_query_parameter(query_parameters, "path"),
                    self._read_query_parameter(query_parameters, "section"),
                )
            )
        elif route_path == "/api/markdown":
            self._serve_workspace_payload(
                workspace.build_markdown_payload(
                    repository_root,
                    self._read_query_parameter(query_parameters, "path"),
                )
            )
        elif route_path.startswith(workspace.RAW_ROUTE_PREFIX):
            self._serve_raw_file(
                route_path.removeprefix(workspace.RAW_ROUTE_PREFIX),
                self._read_query_parameter(
                    query_parameters, workspace.RAW_REVISION_QUERY_PARAMETER
                ),
            )
        else:
            # 不回声请求路径：未知路由的应答里没有任何来自请求的可控内容。
            self._send_json_payload(404, {"error": "未知路由：本服务只提供白名单内的只读接口。"})

    def _dispatch_write_request(self) -> None:
        """按固定白名单分发写路由；白名单之外一律 405。

        写路由只有一条：``POST /api/stage``，请求体是一个 JSON 对象，``scope`` 取值是封闭枚举
        （``path`` 或 ``all``）。范围取值由服务端映射成具体命令，任何取值都不会作为参数流进
        ``git``——与改动分区同一条口径。
        """
        if urlsplit(self.path).path != _STAGE_ROUTE_PATH:
            self._refuse_non_read_method()
            return

        stage_request, failure_payload = self._read_stage_request_body()
        if failure_payload is not None:
            self._send_json_payload(failure_payload.status_code, failure_payload.payload)
            return

        scope = stage_request.get("scope")
        repository_root = self.server.repository_root
        if scope == workspace.STAGE_SCOPE_ALL:
            self._serve_workspace_payload(workspace.stage_all_changes(repository_root))
            return
        if scope == workspace.STAGE_SCOPE_PATH:
            requested_path = stage_request.get("path")
            if not isinstance(requested_path, str):
                self._send_json_payload(
                    400, {"error": "拒绝：scope 为 path 时必须给出字符串 path。"}
                )
                return
            self._serve_workspace_payload(workspace.stage_changes(repository_root, requested_path))
            return
        self._send_json_payload(
            400,
            {
                "error": "拒绝：scope 不是可用的暂存范围，"
                f"请选择「{'」「'.join(sorted(workspace.KNOWN_STAGE_SCOPES))}」。"
            },
        )

    def _read_stage_request_body(
        self,
    ) -> tuple[dict[str, object], workspace_read.WorkspacePayload | None]:
        """读取并校验写请求的 JSON 对象体。

        两道门槛都是必须的，而不是讲究：**类型必须是 JSON**（跨站表单式 POST 是「简单请求」，
        浏览器会直接发出，而 JSON 会强制预检、预检必然失败），**长度设上限**（一句话就能让服务
        端在读取时分配内存）。

        Returns:
            tuple[dict[str, object], WorkspacePayload | None]: 解析出的对象，以及失败时的拒绝
                应答（成功时为 ``None``）。
        """
        content_type = self.headers.get("Content-Type", "")
        if content_type.split(";")[0].strip().lower() != "application/json":
            return {}, workspace_read.build_refusal_payload(
                415,
                "拒绝：暂存只接受 application/json 请求体"
                "（跨站表单式 POST 会被浏览器直接发出，因此这里用类型强制预检）。",
            )

        try:
            content_length = int(self.headers.get("Content-Length") or "0")
        except ValueError:
            return {}, workspace_read.build_refusal_payload(400, "拒绝：Content-Length 不合法。")
        if content_length <= 0:
            return {}, workspace_read.build_refusal_payload(400, "拒绝：请求体为空。")
        if content_length > _MAX_WRITE_BODY_BYTES:
            # 刻意不读这段正文，因此这条连接必须关掉：HTTP/1.1 连接要被复用，留着一段没读完的
            # 正文会让下一次请求读到它的残余。
            self.close_connection = True
            return {}, workspace_read.build_refusal_payload(
                413, f"拒绝：请求体超过 {_MAX_WRITE_BODY_BYTES} 字节的上限。"
            )

        try:
            parsed_body = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {}, workspace_read.build_refusal_payload(400, "拒绝：请求体不是合法的 JSON。")
        if not isinstance(parsed_body, dict):
            return {}, workspace_read.build_refusal_payload(400, "拒绝：请求体必须是 JSON 对象。")
        return parsed_body, None

    def _read_query_parameter(
        self,
        query_parameters: dict[str, list[str]],
        parameter_name: str,
    ) -> str:
        """取单个查询参数；缺失或重复给出时取第一个。"""
        parameter_values = query_parameters.get(parameter_name)
        return parameter_values[0] if parameter_values else ""

    def _serve_workspace_payload(self, workspace_payload: workspace_read.WorkspacePayload) -> None:
        """返回一个工作区读取结果。"""
        self._send_json_payload(workspace_payload.status_code, workspace_payload.payload)

    def _serve_static_asset(self, asset_name: str) -> None:
        """按固定文件名白名单返回静态资源。

        资源名来自请求路径，因此这里用白名单而不是拼接路径：没有可以拼接的路径，就
        没有可以逃逸的路径。查看器自身只有这三个固定资源，所以白名单足够；仓库内
        文件的按路径取用走另一条路由（见 :meth:`_serve_raw_file`），那里的防护是
        解析成绝对路径之后再断言。
        """
        content_type = _STATIC_CONTENT_TYPES_BY_FILENAME.get(asset_name)
        if content_type is None:
            self._send_json_payload(404, {"error": "未知的静态资源。"})
            return

        asset_bytes = (_ASSETS_DIRECTORY_PATH / asset_name).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(asset_bytes)))
        # 本地开发工具不缓存：改了页面就应该立刻看到。
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(asset_bytes)

    def _serve_raw_file(self, encoded_relative_path: str, revision_name: str) -> None:
        """返回仓库内的原始文件字节，供 HTML 文件在新标签页里加载、供图片在内容区显示。

        这是唯一一条保持路径原样的路由，而且必须保持：HTML 文档里的相对引用要能解析
        回同一路由、真的加载出来。替代的防护是 ``resolve()`` 之后再断言仍在仓库根之下
        （见 :func:`workspace.resolve_repository_path`），越界一律拒绝。路径段先解码再
        交给解析器——带 ``%00`` 之类的畸形输入解码后同样落在那条断言上，而不是穿透成
        无应答。

        ``revision_name`` 为空表示工作区当前版本（默认）；给了则是 HEAD / 索引里的历史
        版本，供改动视图做旧新对比。取值是封闭枚举，两种来源走的是同一条边界断言。

        Args:
            encoded_relative_path (str): ``/raw/`` 之后、尚未解码的路径。
            revision_name (str): 历史版本取值；空串表示工作区当前版本。
        """
        decoded_relative_path = unquote(encoded_relative_path)
        raw_file_result = (
            workspace.build_revision_file_payload(
                self.server.repository_root, decoded_relative_path, revision_name
            )
            if revision_name
            else workspace.build_raw_file_payload(
                self.server.repository_root, decoded_relative_path
            )
        )
        if isinstance(raw_file_result, workspace_read.WorkspacePayload):
            self._send_json_payload(raw_file_result.status_code, raw_file_result.payload)
            return

        self.send_response(raw_file_result.status_code)
        self.send_header("Content-Type", raw_file_result.content_type)
        self.send_header("Content-Length", str(len(raw_file_result.body_bytes)))
        # 表外后缀是二进制流。不声明 nosniff 时浏览器会按内容嗅探，把一个 .txt 当 HTML
        # 执行——即使它从来没有以 text/html 供出过。
        self.send_header("X-Content-Type-Options", "nosniff")
        # 与其它读取路径一致：本地开发工具不缓存，改了文件就应该立刻看到。
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw_file_result.body_bytes)

    def _send_json_payload(self, status_code: int, payload: dict[str, object]) -> None:
        """返回一条 JSON 应答。"""
        response_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(response_bytes)


def run_server(configuration: ServerConfiguration) -> int:
    """启动服务并阻塞到退出，退出前清理本实例的登记记录。

    Args:
        configuration (ServerConfiguration): 本次启动配置。

    Returns:
        int: 进程退出码；端口无法绑定时为 ``1``。
    """
    try:
        viewer_server = ViewerHTTPServer(configuration, ViewerRequestHandler)
    except OSError as bind_error:
        print(
            f"查看器服务无法绑定 {VIEWER_HOST}:{configuration.port}：{bind_error}",
            file=sys.stderr,
            flush=True,
        )
        return 1

    _register_termination_signal_handlers(viewer_server)
    _start_highlight_prewarm_thread()
    _start_idle_reaper_thread(viewer_server)
    print(
        f"查看器服务已监听 http://{VIEWER_HOST}:{configuration.port}/"
        f"（仓库 {configuration.repository_root.name}，"
        f"空闲时限 {configuration.idle_timeout_seconds:.0f} 秒）",
        file=sys.stderr,
        flush=True,
    )

    try:
        viewer_server.serve_forever(poll_interval=_SERVE_POLL_INTERVAL_SECONDS)
    finally:
        viewer_server.server_close()
        instance.clear_instance_record(
            configuration.repository_root,
            expected_process_id=os.getpid(),
        )
    return 0


def _register_termination_signal_handlers(viewer_server: ViewerHTTPServer) -> None:
    """把 SIGINT / SIGTERM 接到优雅退出上，让登记清理在两条路径都成立。

    处理器必须把 ``shutdown()`` 交给另一个线程：信号处理器跑在主线程里，而主线程
    此刻正阻塞在 ``serve_forever()``，直接调用等于自己等自己。

    Args:
        viewer_server (ViewerHTTPServer): 待停止的服务实例。
    """

    def handle_termination_signal(_signal_number: int, _stack_frame: object) -> None:
        threading.Thread(target=viewer_server.shutdown, daemon=True).start()

    signal.signal(signal.SIGINT, handle_termination_signal)
    signal.signal(signal.SIGTERM, handle_termination_signal)


def _start_highlight_prewarm_thread() -> threading.Thread:
    """在后台线程预热语法高亮，使首个文件请求不为这段导入付费。

    Returns:
        threading.Thread: 已启动的预热线程。
    """
    prewarm_thread = threading.Thread(
        target=rendering.prewarm_highlighting,
        daemon=True,
        name="view-highlight-prewarm",
    )
    prewarm_thread.start()
    return prewarm_thread


def _start_idle_reaper_thread(viewer_server: ViewerHTTPServer) -> threading.Thread | None:
    """启动空闲回收线程；时限非正数时关闭该行为。

    Args:
        viewer_server (ViewerHTTPServer): 被监视的服务实例。

    Returns:
        threading.Thread | None: 已启动的回收线程；关闭自动回收时为 ``None``。
    """
    idle_timeout_seconds = viewer_server.configuration.idle_timeout_seconds
    if idle_timeout_seconds <= 0:
        return None
    check_interval_seconds = max(
        _MIN_IDLE_CHECK_INTERVAL_SECONDS,
        min(_IDLE_CHECK_INTERVAL_SECONDS, idle_timeout_seconds / 4),
    )

    def reap_when_idle() -> None:
        while True:
            time.sleep(check_interval_seconds)
            idle_seconds = viewer_server.seconds_since_last_request()
            if idle_seconds >= idle_timeout_seconds:
                print(
                    f"查看器已闲置 {idle_seconds:.0f} 秒（上限 "
                    f"{idle_timeout_seconds:.0f} 秒），退出并清理登记。",
                    file=sys.stderr,
                    flush=True,
                )
                viewer_server.shutdown()
                return

    idle_reaper_thread = threading.Thread(
        target=reap_when_idle,
        daemon=True,
        name="view-idle-reaper",
    )
    idle_reaper_thread.start()
    return idle_reaper_thread


def main(argv: list[str] | None = None) -> int:
    """解析命令行参数并运行服务。

    Args:
        argv (list[str] | None): 命令行参数；``None`` 时取 ``sys.argv[1:]``。

    Returns:
        int: 进程退出码。
    """
    argument_parser = argparse.ArgumentParser(
        description="本机只读文件与改动查看器服务。由 `just view` 拉起，通常不直接使用。",
    )
    argument_parser.add_argument("--repo-root", required=True, help="被查看仓库的根目录")
    argument_parser.add_argument("--port", type=int, required=True, help="监听端口")
    argument_parser.add_argument(
        "--idle-timeout",
        type=float,
        default=instance.DEFAULT_IDLE_TIMEOUT_SECONDS,
        help="空闲回收时限（秒），0 表示关闭自动回收",
    )
    parsed_arguments = argument_parser.parse_args(argv)

    return run_server(
        ServerConfiguration(
            repository_root=Path(parsed_arguments.repo_root).resolve(),
            port=parsed_arguments.port,
            idle_timeout_seconds=parsed_arguments.idle_timeout,
        )
    )


if __name__ == "__main__":
    sys.exit(main())
