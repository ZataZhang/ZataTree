"""只读读取的公共契约：应答信封、拒绝应答、``git`` 调用失败的错误类型，以及路径越界断言。

查看器的每个读取用例（文件树、正文、改动、diff、预览、`/raw/`）都长在同一套词汇上：返回
一个 :class:`WorkspacePayload`，拒绝时用 :func:`build_refusal_payload`，而任何来自界面的
路径都必须先过 :func:`resolve_repository_path`。这些词汇与「具体读什么」无关，因此单独放在
这里——否则每加一种读取都要把它们复制一遍，或者把模块撑到没人愿意读。

**边界只有这一处**：路径先 ``resolve()`` 再断言仍在仓库根之下，符号链接指向仓库外时只有
解析后才会暴露；拒绝信息里绝不带绝对路径，否则「越界被拒绝」本身就成了仓库外路径的探测口。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class WorkspaceCommandError(RuntimeError):
    """一次 ``git`` 调用失败（非零退出）。读取路径与那唯一一个写路径共用它。"""


@dataclass(frozen=True)
class WorkspacePayload:
    """一个只读接口的应答：HTTP 状态码加 JSON 载荷。

    Attributes:
        status_code (int): 应答的 HTTP 状态码。
        payload (dict[str, object]): 应答正文，会被序列化成 JSON。
    """

    status_code: int
    payload: dict[str, object]


#: 路径越界时的拒绝文案。三个读取入口（正文、diff、预览）共用一份：分别各写一句时
#: 任何一处漏更新都会让「越界」在不同接口上说法不一。
OUTSIDE_REPOSITORY_REFUSAL_MESSAGE = "拒绝：该路径越出仓库范围，只读查看器不读取仓库外的文件。"


def resolve_repository_path(repository_root: Path, requested_path: str) -> Path | None:
    """把请求路径解析成仓库内的绝对路径，越界时返回 ``None``。

    先 ``resolve()`` 再断言：符号链接指向仓库外时只有解析后才会暴露，这一步是路径
    逃逸防护的关键顺序，不能颠倒成「先断言再解析」。

    Args:
        repository_root (Path): 仓库根绝对路径。
        requested_path (str): 界面传来的仓库相对路径；空串表示仓库根。

    Returns:
        Path | None: 位于仓库内的绝对路径；越界、绝对路径或解析失败时为 ``None``。
    """
    if not requested_path:
        return repository_root
    requested_relative_path = Path(requested_path)
    if requested_relative_path.is_absolute():
        return None
    try:
        resolved_path = (repository_root / requested_relative_path).resolve()
    except (OSError, ValueError):
        # 路径里带 NUL 字节时 resolve() 抛的是 ValueError 而不是 OSError；漏掉它会让
        # 异常穿透到 HTTP 层，畸形请求变成「连接被丢弃 + 日志 traceback」而不是拒绝应答。
        return None
    if resolved_path == repository_root or resolved_path.is_relative_to(repository_root):
        return resolved_path
    return None


def build_refusal_payload(status_code: int, message: str) -> WorkspacePayload:
    """构造一条拒绝应答。

    拒绝信息里绝不带绝对路径，否则「路径越界被拒绝」本身就成了仓库外路径的探测口
    与信息泄漏面。

    Args:
        status_code (int): 应答的 HTTP 状态码。
        message (str): 面向使用者的中文说明。

    Returns:
        WorkspacePayload: 拒绝应答。
    """
    return WorkspacePayload(status_code=status_code, payload={"error": message})
