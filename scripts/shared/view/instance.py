"""查看器常驻实例的登记与仓库定位。

``just view`` 的「秒开」来自复用既有实例，而复用判定完全落在这份登记上：登记
记录实例的进程号、端口、仓库根与启动时间，客户端入口据此做三项新鲜度校验
（进程存活 / 端口可连 / 仓库一致），服务端在空闲回收时据此清理自己那一条记录。

登记文件是仓库根的 ``.env.view-state``，被 ``.gitignore`` 的 ``.env*`` 规则覆盖，
每个 worktree 天然独立——与既有的 ``.env.run-state`` 同构，不引入新的目录约定。
它的字段集合是客户端与服务的共同契约，只在 ``docs/guides/file-viewer.md`` 与
本文件里维护。

本模块刻意只依赖标准库里的轻量部分：客户端入口的「秒开」路径会 import 它，任何
在这里拖进来的重依赖（例如 ``http.server``）都会直接落在复用命中的耗时预算上。
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

#: 实例登记文件名，落在仓库根，按 worktree 独立。
REGISTRY_FILE_NAME = ".env.view-state"

#: 查看器服务只绑本机回环地址：不监听任何对外网卡，也不做局域网共享与鉴权。
LOOPBACK_HOST = "127.0.0.1"

#: 空闲回收时限默认值（秒），可由 ``just view --idle-timeout`` 覆盖；``0`` 关闭自动回收。
DEFAULT_IDLE_TIMEOUT_SECONDS = 1800.0

_GIT_MARKER_NAME = ".git"

_PID_FIELD_NAME = "VIEW_PID"
_PORT_FIELD_NAME = "VIEW_PORT"
_REPOSITORY_ROOT_FIELD_NAME = "VIEW_REPO_ROOT"
_STARTED_AT_FIELD_NAME = "VIEW_STARTED_AT"

_INSTANCE_FIELD_NAMES = (
    _PID_FIELD_NAME,
    _PORT_FIELD_NAME,
    _REPOSITORY_ROOT_FIELD_NAME,
    _STARTED_AT_FIELD_NAME,
)


class ViewInstanceRecord(NamedTuple):
    """一条常驻查看器实例的登记记录。

    刻意用 ``NamedTuple`` 而不是 ``@dataclass(frozen=True)``：``dataclasses`` 会连带
    拉进 ``inspect``，本机实测约 20ms，而本模块每次 ``just view`` 都要在 150ms 的复用
    命中预算里被 import 一次。``workspace.py`` / ``server.py`` 不在那条路径上，那里仍
    按仓库惯例用 dataclass。

    Attributes:
        process_id (int): 服务进程号，``just view --stop`` 据此投递终止信号。
        port (int): 服务监听的本机回环端口。
        repository_root (Path): 实例所服务的仓库根绝对路径，用于判定登记是否属于
            当前仓库（同一台机器上并存多个派生项目时的主要判据）。
        started_at_iso (str): 实例启动时刻的 ISO-8601 字符串，仅供排障阅读。
    """

    process_id: int
    port: int
    repository_root: Path
    started_at_iso: str


def resolve_repository_root(start_directory: Path | None = None) -> Path:
    """解析当前所在的 Git 仓库根目录。

    先按「向上查找 ``.git`` 标记」定位：纯文件系统调用，而 ``just view`` 的复用命中
    路径有 150ms 预算，每次 fork 一个 ``git rev-parse`` 要花掉其中五分之一。找不到
    标记时才退回 git 自己的判定，把 ``GIT_DIR`` 之类的特例交给权威实现。

    Args:
        start_directory (Path | None): 查询起点目录，默认使用当前工作目录。

    Returns:
        Path: 已 ``resolve()`` 的仓库根绝对路径。

    Raises:
        RuntimeError: 起点不在任何 Git 仓库内。
    """
    search_directory = (start_directory or Path.cwd()).resolve()
    for candidate_directory in (search_directory, *search_directory.parents):
        if (candidate_directory / _GIT_MARKER_NAME).exists():
            return candidate_directory
    return _resolve_repository_root_with_git(search_directory)


def _resolve_repository_root_with_git(search_directory: Path) -> Path:
    """用 ``git rev-parse --show-toplevel`` 兜底定位仓库根。

    ``subprocess`` 只在这条兜底路径上按需 import：它在复用命中路径上必然用不到，而
    模块级 import 要为每次调用都付一次开销。

    Args:
        search_directory (Path): 查询起点目录。

    Returns:
        Path: 仓库根绝对路径。

    Raises:
        RuntimeError: ``git`` 判定失败。
    """
    import subprocess

    completed_process = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=str(search_directory),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed_process.returncode != 0:
        raise RuntimeError(
            "不在 Git 仓库内，无法定位查看器的工作目录："
            f"{completed_process.stderr.strip() or 'git rev-parse 失败'}"
        )
    return Path(completed_process.stdout.strip()).resolve()


def resolve_registry_path(repository_root: Path) -> Path:
    """给出某个仓库的实例登记文件路径。

    Args:
        repository_root (Path): 仓库根绝对路径。

    Returns:
        Path: 登记文件路径（不保证存在）。
    """
    return repository_root / REGISTRY_FILE_NAME


def read_instance_record(repository_root: Path) -> ViewInstanceRecord | None:
    """读取实例登记，返回 ``None`` 表示没有可用登记。

    登记文件不存在、内容缺失字段、或字段值无法解析时都返回 ``None``——调用方
    的下一步是「判定陈旧并重新起服务」，而不是把半截登记当成实例。

    Args:
        repository_root (Path): 仓库根绝对路径。

    Returns:
        ViewInstanceRecord | None: 解析成功的登记记录。
    """
    registry_path = resolve_registry_path(repository_root)
    try:
        registry_text = registry_path.read_text(encoding="utf-8")
    except OSError:
        return None

    parsed_field_values: dict[str, str] = {}
    for raw_line in registry_text.splitlines():
        stripped_line = raw_line.strip()
        if not stripped_line or stripped_line.startswith("#") or "=" not in stripped_line:
            continue
        field_name, _, field_value = stripped_line.partition("=")
        parsed_field_values[field_name.strip()] = field_value.strip()

    if any(field_name not in parsed_field_values for field_name in _INSTANCE_FIELD_NAMES):
        return None

    try:
        recorded_process_id = int(parsed_field_values[_PID_FIELD_NAME])
        recorded_port = int(parsed_field_values[_PORT_FIELD_NAME])
    except ValueError:
        return None

    return ViewInstanceRecord(
        process_id=recorded_process_id,
        port=recorded_port,
        repository_root=Path(parsed_field_values[_REPOSITORY_ROOT_FIELD_NAME]).resolve(),
        started_at_iso=parsed_field_values[_STARTED_AT_FIELD_NAME],
    )


def write_instance_record(instance_record: ViewInstanceRecord) -> None:
    """把实例登记写入仓库根的登记文件。

    Args:
        instance_record (ViewInstanceRecord): 待写入的登记记录。
    """
    registry_path = resolve_registry_path(instance_record.repository_root)
    registry_path.write_text(
        "\n".join(
            (
                f"{_PID_FIELD_NAME}={instance_record.process_id}",
                f"{_PORT_FIELD_NAME}={instance_record.port}",
                f"{_REPOSITORY_ROOT_FIELD_NAME}={instance_record.repository_root}",
                f"{_STARTED_AT_FIELD_NAME}={instance_record.started_at_iso}",
                "",
            )
        ),
        encoding="utf-8",
    )


def clear_instance_record(repository_root: Path, *, expected_process_id: int | None = None) -> bool:
    """删除实例登记文件。

    Args:
        repository_root (Path): 仓库根绝对路径。
        expected_process_id (int | None): 只在该进程号仍登记在案时删除。服务端空闲
            回收走这条约束——期间可能有 ``--no-reuse`` 起的更新实例接管了同一份
            登记，回收方不得顺手抹掉别人的记录。

    Returns:
        bool: 是否真的删除了登记文件。
    """
    if expected_process_id is not None:
        recorded_instance = read_instance_record(repository_root)
        if recorded_instance is None or recorded_instance.process_id != expected_process_id:
            return False

    registry_path = resolve_registry_path(repository_root)
    try:
        registry_path.unlink()
    except FileNotFoundError:
        return False
    return True
