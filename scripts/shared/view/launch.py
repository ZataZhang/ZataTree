"""``just view`` 的客户端入口：复用既有实例，或起一个再打开。

``just view`` 默认落在**改动视图**——日常用的正是「看一眼改了什么」，文件视图由
``--files`` 显式选择。生命周期逻辑只有这一份实现，``just diff`` 只是转发到同一入口
的薄别名。三条路径共用同一份登记（仓库根的 ``.env.view-state``）：

- **打开路径**：读登记 → 三项新鲜度校验（进程存活 / 端口可连 / 仓库一致）→ 命中就
  拼 URL 直接打开并立刻返回，不重启进程；任一校验失败即判定陈旧，清理登记后转入
  启动路径。
- **启动路径**：选端口（显式 ``--port`` → 登记值 → 8791 → 系统空闲端口）→ 以新会话
  拉起服务并把日志写进 ``logs/`` → 轮询首个只读接口直到成功（不使用固定 ``sleep``）
  → 写登记 → 打开浏览器。
- **回收路径**：``--stop`` 读登记 → 终止进程 → 清理登记。结束实例走进程信号，不新增
  任何 HTTP 写路由——只读是硬边界，不为运维便利开第一个写口子。
"""

from __future__ import annotations

import argparse
import os
import signal
import socket
import sys
import time
from pathlib import Path
from typing import NamedTuple, TextIO
from urllib.parse import urlencode

import instance

#: 没有登记值也没有显式 ``--port`` 时优先尝试的端口；与后端 8000 / 管理前端 5173 /
#: 前台 3000 三个默认端口不重叠，被占用则继续退让。
DEFAULT_VIEWER_PORT = 8791

#: 服务日志落在被 gitignore 覆盖的 ``logs/`` 下，排障入口之一。
SERVICE_LOG_RELATIVE_PATH = Path("logs") / "view-viewer.log"

#: 界面视图取值，与静态页读取的 ``view`` 查询参数一致。默认进改动视图：``just view``
#: 的日常用法就是「看一眼改了什么」，文件视图由 ``--files`` 显式选择。
FILES_VIEW = "files"
DIFF_VIEW = "diff"

_READY_TIMEOUT_SECONDS = 5.0
_READY_POLL_INTERVAL_SECONDS = 0.02
_REQUEST_TIMEOUT_SECONDS = 1.0
_STOP_TIMEOUT_SECONDS = 5.0
_STOP_POLL_INTERVAL_SECONDS = 0.05


class ViewerLaunchError(RuntimeError):
    """客户端入口无法完成本次调用。"""


class LaunchRequest(NamedTuple):
    """一次 ``just view`` 调用的解析结果。

    与 :class:`instance.ViewInstanceRecord` 同理，用 ``NamedTuple`` 而不是 dataclass：
    本模块每次 ``just view`` 都要在 150ms 的复用命中预算里被 import 一次。

    Attributes:
        requested_path (str): 直达的文件或目录（仓库相对路径），空串表示仓库根。
        view (str): 初始视图，``files`` 或 ``diff``；默认 ``diff``。
        requested_port (int | None): 显式 ``--port``；未给时为 ``None``。
        idle_timeout_seconds (float): 空闲回收时限；非正数表示关闭自动回收。
        no_reuse (bool): 强制新起实例，不复用既有实例。
        no_open (bool): 只打印 URL，不打开浏览器。
        stop (bool): 回收本仓库的常驻实例。
    """

    requested_path: str
    view: str
    requested_port: int | None
    idle_timeout_seconds: float
    no_reuse: bool
    no_open: bool
    stop: bool = False


def main(argv: list[str] | None = None) -> int:
    """执行一次 ``just view`` 调用。

    Args:
        argv (list[str] | None): 命令行参数；``None`` 时取 ``sys.argv[1:]``。

    Returns:
        int: 进程退出码。
    """
    try:
        return _run_launch_request(_parse_arguments(argv))
    except ViewerLaunchError as launch_error:
        print(f"错误：{launch_error}", file=sys.stderr)
        return 1


def _run_launch_request(launch_request: LaunchRequest) -> int:
    """按解析结果走打开、启动或回收路径。

    Args:
        launch_request (LaunchRequest): 本次调用的解析结果。

    Returns:
        int: 进程退出码。
    """
    repository_root = instance.resolve_repository_root()
    if launch_request.stop:
        return _stop_resident_instance(repository_root)

    remembered_instance = instance.read_instance_record(repository_root)
    if remembered_instance is not None and not launch_request.no_reuse:
        if _is_instance_reusable(remembered_instance, repository_root):
            return _open_resident_instance(remembered_instance, launch_request)
        print(
            f"登记项已陈旧（pid {remembered_instance.process_id}，"
            f"端口 {remembered_instance.port}），重新起服务。"
        )
        instance.clear_instance_record(
            repository_root, expected_process_id=remembered_instance.process_id
        )

    return _start_new_instance(
        repository_root,
        launch_request,
        remembered_port=remembered_instance.port if remembered_instance else None,
    )


def _parse_arguments(argv: list[str] | None) -> LaunchRequest:
    """解析命令行参数。

    Args:
        argv (list[str] | None): 命令行参数。

    Returns:
        LaunchRequest: 解析结果。
    """
    argument_parser = argparse.ArgumentParser(
        prog="just view",
        description="打开本机只读文件与改动查看器（只读，不写入被查看的仓库）。",
    )
    argument_parser.add_argument(
        "path",
        nargs="?",
        default="",
        help="打开后直达的文件或目录（仓库相对路径）",
    )
    view_selection_group = argument_parser.add_mutually_exclusive_group()
    view_selection_group.add_argument(
        "--files",
        action="store_true",
        help="进入文件视图（默认进入改动视图）",
    )
    view_selection_group.add_argument(
        "--diff",
        action="store_true",
        help="进入改动视图（默认视图）",
    )
    argument_parser.add_argument("--port", type=int, default=None, help="指定监听端口")
    argument_parser.add_argument(
        "--idle-timeout",
        type=float,
        default=None,
        help="空闲回收时限（秒），0 表示关闭自动回收",
    )
    argument_parser.add_argument(
        "--no-reuse",
        action="store_true",
        help="强制新起一个实例，不复用既有实例",
    )
    argument_parser.add_argument(
        "--no-open",
        action="store_true",
        help="只打印 URL，不打开浏览器",
    )
    argument_parser.add_argument(
        "--stop",
        action="store_true",
        help="回收本仓库的常驻查看器实例，不打开界面",
    )
    parsed_arguments = argument_parser.parse_args(argv)

    return LaunchRequest(
        requested_path=parsed_arguments.path,
        view=FILES_VIEW if parsed_arguments.files else DIFF_VIEW,
        requested_port=parsed_arguments.port,
        idle_timeout_seconds=(
            instance.DEFAULT_IDLE_TIMEOUT_SECONDS
            if parsed_arguments.idle_timeout is None
            else parsed_arguments.idle_timeout
        ),
        no_reuse=parsed_arguments.no_reuse,
        no_open=parsed_arguments.no_open,
        stop=parsed_arguments.stop,
    )


def _is_instance_reusable(
    instance_record: instance.ViewInstanceRecord | None,
    repository_root: Path,
) -> bool:
    """三项新鲜度校验：仓库一致、进程存活、端口可连。

    三项缺一不可——单看进程存活会撞上进程号复用，单看端口可连会撞上端口被别的进程
    占用；仓库一致这一项则让同一台机器上的多个派生项目互不串台。

    Args:
        instance_record (instance.ViewInstanceRecord | None): 登记记录。
        repository_root (Path): 本次调用的仓库根。

    Returns:
        bool: 登记项是否指向一个可用于复用的活实例。
    """
    if instance_record is None:
        return False
    if instance_record.repository_root != repository_root:
        return False
    if not _is_process_alive(instance_record.process_id):
        return False
    return _is_port_connectable(instance_record.port)


def _is_process_alive(process_id: int) -> bool:
    """判断进程号是否仍存活。

    Args:
        process_id (int): 待探测的进程号。

    Returns:
        bool: 进程存活且属于当前用户时为 ``True``。
    """
    try:
        os.kill(process_id, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # 进程存在但不属于当前用户：不可能是我们起出来的服务，按不新鲜处理。
        return False
    return True


def _is_port_connectable(port: int) -> bool:
    """判断回环地址上的端口是否可连接。

    Args:
        port (int): 端口号。

    Returns:
        bool: 能建立 TCP 连接时为 ``True``。
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe_socket:
        probe_socket.settimeout(_REQUEST_TIMEOUT_SECONDS)
        return probe_socket.connect_ex((instance.LOOPBACK_HOST, port)) == 0


def _is_port_available(port: int) -> bool:
    """判断端口能否被本机回环绑定。

    与服务的绑定口径保持一致（都得能独占绑定），因此端口被本实例或任何别的进程占着
    都判为不可用。

    Args:
        port (int): 端口号。

    Returns:
        bool: 能独占绑定时为 ``True``。
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe_socket:
        try:
            probe_socket.bind((instance.LOOPBACK_HOST, port))
        except OSError:
            return False
    return True


def _select_port(*, requested_port: int | None, remembered_port: int | None) -> int:
    """按「显式端口 → 登记值 → 默认端口 → 系统空闲端口」选一个可用端口。

    Args:
        requested_port (int | None): 显式 ``--port``。
        remembered_port (int | None): 陈旧登记里记下的端口。

    Returns:
        int: 可用的端口号。

    Raises:
        ViewerLaunchError: 显式指定的端口已被占用。
    """
    if requested_port is not None:
        if not _is_port_available(requested_port):
            raise ViewerLaunchError(f"端口 {requested_port} 已被占用，请换一个或省略 --port。")
        return requested_port

    for candidate_port in (remembered_port, DEFAULT_VIEWER_PORT):
        if candidate_port is not None and _is_port_available(candidate_port):
            return candidate_port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as reservation_socket:
        reservation_socket.bind((instance.LOOPBACK_HOST, 0))
        return int(reservation_socket.getsockname()[1])


def _start_new_instance(
    repository_root: Path,
    launch_request: LaunchRequest,
    *,
    remembered_port: int | None,
) -> int:
    """拉起一个新实例、登记它，并打开界面。

    Args:
        repository_root (Path): 仓库根绝对路径。
        launch_request (LaunchRequest): 本次调用的解析结果。
        remembered_port (int | None): 陈旧登记里记下的端口，作为端口选择的首选。

    Returns:
        int: 进程退出码。
    """
    selected_port = _select_port(
        requested_port=launch_request.requested_port,
        remembered_port=remembered_port,
    )
    service_log_handle = _open_service_log(repository_root)
    try:
        service_process_id = _spawn_server_process(
            repository_root=repository_root,
            port=selected_port,
            idle_timeout_seconds=launch_request.idle_timeout_seconds,
            service_log_handle=service_log_handle,
        )
        is_ready = _wait_until_ready(port=selected_port, service_process_id=service_process_id)
    finally:
        service_log_handle.close()

    if not is_ready:
        # 起不来的实例不能留成孤儿：超过时限仍未就绪时主动收掉这一次拉起的进程。
        if _is_process_alive(service_process_id):
            os.kill(service_process_id, signal.SIGTERM)
        raise ViewerLaunchError(
            f"查看器服务在 {_READY_TIMEOUT_SECONDS:.0f} 秒内未就绪"
            f"（pid {service_process_id}，端口 {selected_port}）。"
            f"服务日志：{SERVICE_LOG_RELATIVE_PATH.as_posix()}"
        )

    instance.write_instance_record(
        instance.ViewInstanceRecord(
            process_id=service_process_id,
            port=selected_port,
            repository_root=repository_root,
            started_at_iso=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        )
    )
    return _open_viewer_in_browser(
        _build_viewer_url(port=selected_port, launch_request=launch_request),
        report=f"已启动查看器实例（pid {service_process_id}，端口 {selected_port}）",
        no_open=launch_request.no_open,
    )


def _open_resident_instance(
    instance_record: instance.ViewInstanceRecord,
    launch_request: LaunchRequest,
) -> int:
    """复用既有实例：拼 URL 直接打开，不重启进程。

    Args:
        instance_record (instance.ViewInstanceRecord): 命中的登记记录。
        launch_request (LaunchRequest): 本次调用的解析结果。

    Returns:
        int: 进程退出码。
    """
    return _open_viewer_in_browser(
        _build_viewer_url(port=instance_record.port, launch_request=launch_request),
        report=f"复用既有实例（pid {instance_record.process_id}，端口 {instance_record.port}）",
        no_open=launch_request.no_open,
    )


def _stop_resident_instance(repository_root: Path) -> int:
    """回收本仓库的常驻实例：读登记 → 终止进程 → 清理登记。

    回收不经过任何 HTTP 写路由——服务端保持严格只读。

    Args:
        repository_root (Path): 仓库根绝对路径。

    Returns:
        int: 进程退出码，回收本身始终视为成功。
    """
    instance_record = instance.read_instance_record(repository_root)
    if instance_record is None:
        print("没有登记在案的查看器实例，无需回收。")
        return 0

    if _is_process_alive(instance_record.process_id):
        os.kill(instance_record.process_id, signal.SIGTERM)
        is_port_closed = _wait_until_port_is_closed(instance_record.port)
        print(
            f"已停止查看器实例（pid {instance_record.process_id}，端口 {instance_record.port}）。"
        )
        if not is_port_closed:
            print(
                f"警告：端口 {instance_record.port} 仍在监听，请手工检查该进程。",
                file=sys.stderr,
            )
    else:
        print(f"登记项已陈旧（pid {instance_record.process_id} 已退出），只清理登记。")

    instance.clear_instance_record(repository_root, expected_process_id=instance_record.process_id)
    return 0


def _wait_until_port_is_closed(port: int) -> bool:
    """等待端口停止监听。

    Args:
        port (int): 端口号。

    Returns:
        bool: 在超时前不再被监听时为 ``True``。
    """
    deadline_monotonic = time.monotonic() + _STOP_TIMEOUT_SECONDS
    while time.monotonic() < deadline_monotonic:
        if not _is_port_connectable(port):
            return True
        time.sleep(_STOP_POLL_INTERVAL_SECONDS)
    return False


def _open_service_log(repository_root: Path) -> TextIO:
    """以追加方式打开服务日志，交给子进程当标准输出与标准错误。

    Args:
        repository_root (Path): 仓库根绝对路径。

    Returns:
        TextIO: 已打开且可写文本的日志句柄，调用方负责关闭。
    """
    service_log_path = repository_root / SERVICE_LOG_RELATIVE_PATH
    service_log_path.parent.mkdir(parents=True, exist_ok=True)
    return service_log_path.open("a", encoding="utf-8")


def _spawn_server_process(
    *,
    repository_root: Path,
    port: int,
    idle_timeout_seconds: float,
    service_log_handle: TextIO,
) -> int:
    """以新会话拉起服务进程。

    新会话让服务脱离当前终端的进程组：关掉终端或按下 Ctrl-C 都不会顺手带走常驻实例，
    回收只走空闲时限或 ``--stop`` 这两条明确路径。

    Args:
        repository_root (Path): 仓库根绝对路径。
        port (int): 监听端口。
        idle_timeout_seconds (float): 空闲回收时限。
        service_log_handle (TextIO): 子进程标准输出与标准错误的目标。

    Returns:
        int: 服务进程号。
    """
    import subprocess

    server_script_path = Path(__file__).resolve().parent / "server.py"
    service_process = subprocess.Popen(
        [
            sys.executable,
            str(server_script_path),
            "--repo-root",
            str(repository_root),
            "--port",
            str(port),
            "--idle-timeout",
            str(idle_timeout_seconds),
        ],
        stdin=subprocess.DEVNULL,
        stdout=service_log_handle,
        stderr=service_log_handle,
        start_new_session=True,
        close_fds=True,
    )
    return service_process.pid


def _wait_until_ready(*, port: int, service_process_id: int) -> bool:
    """轮询首个只读接口直到成功，不使用固定 ``sleep``。

    Args:
        port (int): 服务端口。
        service_process_id (int): 服务进程号。

    Returns:
        bool: 在超时前拿到成功应答时为 ``True``。
    """
    deadline_monotonic = time.monotonic() + _READY_TIMEOUT_SECONDS
    while time.monotonic() < deadline_monotonic:
        if not _is_process_alive(service_process_id):
            return False
        if _probe_info_endpoint(port):
            return True
        time.sleep(_READY_POLL_INTERVAL_SECONDS)
    return False


def _probe_info_endpoint(port: int) -> bool:
    """请求一次 ``/api/info``，成功即认为服务已就绪。

    Args:
        port (int): 服务端口。

    Returns:
        bool: 应答状态码为 200 时为 ``True``。
    """
    import http.client

    connection = http.client.HTTPConnection(
        instance.LOOPBACK_HOST, port, timeout=_REQUEST_TIMEOUT_SECONDS
    )
    try:
        connection.request("GET", "/api/info")
        response = connection.getresponse()
        response.read()
        return response.status == 200
    except OSError:
        return False
    finally:
        connection.close()


def _build_viewer_url(*, port: int, launch_request: LaunchRequest) -> str:
    """拼出界面 URL，把本次调用的初始视图与直达路径带过去。

    改动视图的分区（已暂存 / 未暂存 / 未跟踪）不由命令行指定：界面一律三段全列，直达路径
    的归属在列表加载完之后解析（见 ``assets/viewer.js`` 的 ``resolveSectionForPath``）。

    Args:
        port (int): 服务端口。
        launch_request (LaunchRequest): 本次调用的解析结果。

    Returns:
        str: 指向本机回环实例的 URL。
    """
    query_fields = {"view": launch_request.view}
    if launch_request.requested_path:
        query_fields["path"] = launch_request.requested_path
    return f"http://{instance.LOOPBACK_HOST}:{port}/?{urlencode(query_fields)}"


def _open_viewer_in_browser(url: str, *, report: str, no_open: bool) -> int:
    """打印实例信息与 URL，并按需把 URL 交给系统默认浏览器。

    Args:
        url (str): 界面 URL。
        report (str): 一行实例说明，供人与证据读取进程号与端口。
        no_open (bool): 只打印不打开。

    Returns:
        int: 进程退出码。
    """
    print(f"{report}\n打开：{url}")
    if not no_open:
        _hand_off_url_to_system_opener(url)
    return 0


def _hand_off_url_to_system_opener(url: str) -> None:
    """把 URL 递给系统打开器后立即返回，不等它跑完。

    刻意不用 ``webbrowser.open_new_tab``：CPython 3.13 的 macOS 实现走 ``osascript``
    并同步等它退出，本机实测阻塞 400–700ms。``just view`` 的复用命中路径总共只有
    150ms 预算，等一个与自己无关的 AppleScript 进程退出会把「秒开」直接吃掉。这里
    只做「把 URL 交给系统打开器」这一件事，各平台选的打开器与 ``webbrowser`` 一致。

    Args:
        url (str): 界面 URL。
    """
    if sys.platform == "win32":
        # Windows 上的系统关联打开器，等价于在资源管理器里双击该 URL。
        os.startfile(url)  # noqa: S606
        return

    import subprocess

    opener_command = ["open", url] if sys.platform == "darwin" else ["xdg-open", url]
    subprocess.Popen(
        opener_command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


if __name__ == "__main__":
    sys.exit(main())
