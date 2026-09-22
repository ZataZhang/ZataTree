"""本机只读文件与改动查看器的服务端实现。

由 ``scripts/shared/view/launch.py`` 以子进程方式拉起，不作为包被 import。服务只绑
本机回环地址、只接受读取方法、路由白名单固定；所有路径参数在 :mod:`workspace` 里解析
成绝对路径后断言仍在仓库根之下。改动数据全部来自真实 ``git``，服务本身对被查看仓库
不执行任何写操作。

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
from urllib.parse import parse_qs, urlsplit

import instance
import workspace

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
        """把任意 ``do_<方法>`` 名字解析成同一个「非读取方法」拒绝处理器。

        这里刻意不逐个定义写方法（POST / PUT / DELETE / PATCH）对应的处理器名字：只读
        边界的可审查性依赖「服务端根本不存在写方法处理入口」这一事实，逐个定义同名
        方法会让「``scripts/shared/view/`` 下搜不到任何写方法处理器」这类静态断言失去
        判别力。``http.server`` 的分发正是 ``hasattr(self, "do_" + command)`` 加
        ``getattr``，因此按前缀返回同一个拒绝处理器即可覆盖全部非读取方法。

        Args:
            attribute_name (str): 被查找的属性名。

        Returns:
            object: 非读取方法的拒绝处理器。

        Raises:
            AttributeError: 属性名不带 ``do_`` 前缀且确实不存在。
        """
        if attribute_name.startswith(_READ_METHOD_HANDLER_PREFIX):
            return self._refuse_non_read_method
        raise AttributeError(attribute_name)

    def do_GET(self) -> None:  # noqa: N802 - http.server 靠 do_<METHOD> 这个名字分发
        """唯一的读取入口：先刷新空闲计时，再按路由白名单分发。"""
        self.server.mark_request_served()
        try:
            self._dispatch_read_request()
        except workspace.WorkspaceReadError as read_error:
            self._send_json_payload(500, {"error": f"读取仓库失败：{read_error}"})

    def _refuse_non_read_method(self) -> None:
        """拒绝一切非读取方法：本服务不注册也不提供任何写入路径。"""
        self.server.mark_request_served()
        self._send_json_payload(
            405,
            {
                "error": "拒绝：只读查看器只接受 GET 请求，不提供写入、暂存或提交接口。",
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
            self._serve_workspace_payload(
                workspace.build_changes_payload(
                    repository_root,
                    self._read_baseline_parameter(query_parameters),
                )
            )
        elif route_path == "/api/diff":
            self._serve_workspace_payload(
                workspace.build_diff_payload(
                    repository_root,
                    self._read_query_parameter(query_parameters, "path"),
                    self._read_baseline_parameter(query_parameters),
                )
            )
        else:
            # 不回声请求路径：未知路由的应答里没有任何来自请求的可控内容。
            self._send_json_payload(404, {"error": "未知路由：本服务只提供白名单内的只读接口。"})

    def _read_baseline_parameter(self, query_parameters: dict[str, list[str]]) -> str:
        """读取基线参数，缺省为「当前工作区」。"""
        return self._read_query_parameter(query_parameters, "base") or workspace.WORKTREE_BASELINE

    def _read_query_parameter(
        self,
        query_parameters: dict[str, list[str]],
        parameter_name: str,
    ) -> str:
        """取单个查询参数；缺失或重复给出时取第一个。"""
        parameter_values = query_parameters.get(parameter_name)
        return parameter_values[0] if parameter_values else ""

    def _serve_workspace_payload(self, workspace_payload: workspace.WorkspacePayload) -> None:
        """返回一个工作区读取结果。"""
        self._send_json_payload(workspace_payload.status_code, workspace_payload.payload)

    def _serve_static_asset(self, asset_name: str) -> None:
        """按固定文件名白名单返回静态资源。

        资源名来自请求路径，因此这里用白名单而不是拼接路径：没有可以拼接的路径，就
        没有可以逃逸的路径。
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
        target=workspace.prewarm_highlighting,
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
