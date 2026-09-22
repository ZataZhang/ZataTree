"""仓库工作区的快照：文件树、文件正文、改动列表、单文件 diff、两种预览，以及暂存。

查看器的全部内容都从这里出。读操作占绝大多数：所有列目录、看正文、算 diff 的 ``git`` 调用都是
查询（``ls-files`` / ``diff`` / ``rev-parse`` / ``cat-file``），所有文件访问都是读取。

**这个模块里只有一处写操作**：:func:`stage_changes` 与 :func:`stage_all_changes`（``git add``），
供界面上「改动」那一段的加号使用。它能做的只有「把工作区里这些改动记进索引」——不改内容、不提交、
不丢弃、不取消暂存。这条边界由用户拍板从「完全不写」放宽为一个受控写口（2026-09-22），因此
``docs/guides/file-viewer.md`` 的「它只能看」那一节与守卫测试里的相应条目都已同步改写；再要开新
的写口之前请先读那两处，别把它当成「顺手就能加」。
特别地，未跟踪文件的改动**不**靠 ``git add -N`` 取得：那一条会写索引，而我们读它靠的是
``git diff --no-index -- /dev/null <文件>``。

改动视图按 `git status` 的三段口径划分，每段的数据源都是真实 ``git``，且与终端逐项一致：

- 已暂存：``git diff --cached``（HEAD ↔ 索引）。
- 未暂存：``git diff``（索引 ↔ 工作区）。
- 未跟踪：``git ls-files --others --exclude-standard`` 列出文件；点开某个文件时才用
  ``git diff --no-index -- /dev/null <文件>`` 求它的逐行 diff。

界面显示的文件集合与增删统计不做二次推断，必须与同参数的终端输出逐项一致。唯一**不向界面
提供**的是未跟踪文件的 ``+N -M``：``git`` 的列表类命令都不报这个数，逐文件取一次在未跟踪
文件多时会让页面卡住（实测 800 个文件约 7 秒）。界面上那两列留空，并在分区上标出
``stats_available=false``；不提供与二进制是两件事，不共用同一个空值。

未跟踪一段沿用文件树的目录剪枝（见 :data:`_PRUNED_DIRECTORY_NAMES`）：派生项目忘了把
依赖目录写进 ``.gitignore`` 时，整棵依赖树既不该进文件树，也不该淹没改动列表。

重命名是这条口径上唯一的例外，而且必须例外：``git diff <rev> -- <新路径>`` 会把旧路径
排除出候选，配对随即失效，同一个文件被降级成「新增」且正文整篇算成新增行。所以单文件
diff 先在不带 pathspec 的完整 diff 上查出旧路径，再把新旧两条路径一起交给 ``git``
（见 :func:`_lookup_rename_source`）。界面上显示的仍是新路径，与终端 ``--name-only``
一致；旧路径只作为「重命名自何处」的出处。

预览有两条独立的路，都**默认不生效**，只在界面上被显式要求时才出力：

- Markdown：:func:`build_markdown_payload` 按需渲染成 HTML 片段（``/api/markdown``），
  文件视图打开 ``.md`` 先看到的仍是源码。片段里的相对引用会被改写成能真正取到字节的地址
  （见 :func:`_build_markdown_reference_url`）——预览是内联进查看器页面（``/``）的，
  照着页面根解析只会得到 404。
- HTML：:func:`build_raw_file_payload` 把文件字节原样供出（``/raw/``），由界面在新标签页
  里打开——查看器不做 HTML 内联渲染。
- 图片改动的旧新对比：:func:`build_diff_payload` 的 ``image_comparison`` 给出两版各自的
  ``/raw/`` 地址（历史版本走 ``?rev=``，见 :mod:`revisions`），界面并排显示。

正文渲染（语法高亮与 Markdown）在 :mod:`rendering` 里，从 git 对象库按版本读字节在
:mod:`revisions` 里；本模块把读文件、判形态、算改动串起来，并把结果整理成界面要的载荷。

``/api/file`` 的应答里，``preview`` 说明**文本文件**支持哪种预览（由
:func:`resolve_preview_descriptor` 按后缀判定），``kind: "image"`` 加 ``url`` 则直接告诉界面
「这个文件是图片，去这个地址取」。后缀判定只写在服务端这一处，界面不复制任何后缀表。

所有对外路径参数先经 :func:`resolve_repository_path` 解析成绝对路径并断言仍在仓库根
之下，越界一律拒绝，且拒绝信息不回声任何绝对路径。改动分区取值是封闭枚举，任何取值都
不会作为参数流进 ``git``。
"""

from __future__ import annotations

import posixpath
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import quote

import rendering
import revisions
from workspace_read import (
    OUTSIDE_REPOSITORY_REFUSAL_MESSAGE,
    WorkspaceCommandError,
    WorkspacePayload,
    build_refusal_payload,
    resolve_repository_path,
)

#: 改动视图的三个分区。字典的插入顺序即界面上的展示顺序：先看已暂存，再看未暂存，
#: 最后是未跟踪——未跟踪恒为「新增」，排在最后不打断前两段之间的对照。
_SECTION_LABELS: dict[str, str] = {
    "staged": "已暂存",
    "unstaged": "未暂存",
    "untracked": "未跟踪",
}

#: 前两个分区的 ``git diff`` 参数前缀；未跟踪那一段走 ``--no-index``，不在表里。
_SECTION_DIFF_ARGUMENT_PREFIXES: dict[str, tuple[str, ...]] = {
    "staged": ("diff", "--cached"),
    "unstaged": ("diff",),
}

#: 未跟踪文件的路径与 ``/dev/null`` 相比，因此它整篇都是新增行。
_UNTRACKED_DIFF_LEFT_PATH = "/dev/null"

#: ``git diff --no-index`` 在「两边有差异」时退出码为 ``1``（同 ``diff`` 语义），而那正是
#: 我们要的正常结果；``0`` 表示两边一致，``>1`` 才是真的出错。把它按成功接纳，否则每个
#: 有内容的未跟踪文件都会让 :func:`_run_git` 抛错。
_DIFF_NO_INDEX_EXIT_CODES = frozenset({0, 1})

#: 文件正文的渲染上限；超过即返回明确标记而不是正文。
MAX_FILE_BYTES = 256 * 1024
MAX_FILE_BYTES_LABEL = "256 KiB"

#: 单文件 diff 的行数上限，避免超大改动把响应撑爆。
MAX_DIFF_ROWS = 4000

_BINARY_SNIFF_BYTES = 8192

#: ``/raw/`` 路由前缀。服务端据此分发，本模块据此拼 URL——同一个常量，两处引用，
#: 拼出来的地址不可能与服务端的匹配口径分岔。
RAW_ROUTE_PREFIX = "/raw/"

#: ``/raw/`` 上指定历史版本的查询参数名。服务端从它取值，本模块用它拼 URL，同样是
#: 一个常量两处引用。
RAW_REVISION_QUERY_PARAMETER = "rev"

#: Markdown 里 ``.md`` 相对链接的去向：查看器文件视图的直达链接前缀。``view`` 与 ``path``
#: 是界面自己的查询参数约定（见 ``assets/viewer.js`` 的 ``applyInitialQueryParameters``），
#: 指到 ``/raw/`` 只会得到一屏原始 markdown 文本，指到这里点一下就能在查看器里读它。
_VIEWER_FILES_VIEW_URL_PREFIX = "/?view=files&path="

#: 后缀 → 预览形态。**只看后缀，不做内容嗅探**：让「这个文件预览成什么」随正文漂移，
#: 排障时无从解释（与词法器解析同一口径）。
_MARKDOWN_SUFFIXES = frozenset({".md", ".markdown"})
_HTML_SUFFIXES = frozenset({".html", ".htm"})

#: 后缀 → 位图图片。命中即 ``kind: "image"``，由浏览器自己去 ``/raw/`` 取字节渲染。
#:
#: 只收 :data:`_RAW_CONTENT_TYPES_BY_SUFFIX` 里以 ``image/`` 开头的位图，**刻意不含
#: ``.svg``**：SVG 是可编辑的文本，源码视图对它更有用；它在 ``/raw/`` 里仍带
#: ``image/svg+xml``，供 HTML 文档按原样引用。两份表必须对得上——图片预览拿到的
#: Content-Type 不是 ``image/*`` 时浏览器会拒渲染，守卫测试里有一条专门钉这个。
_IMAGE_SUFFIXES = frozenset({".gif", ".ico", ".jpeg", ".jpg", ".png", ".webp"})

#: ``/raw/`` 应答的 Content-Type。只收 HTML 文档自己能引到的资源类型：样式、脚本、
#: 图片、字体、JSON。表外一律 :data:`_DEFAULT_RAW_CONTENT_TYPE`，配合服务端发回的
#: ``X-Content-Type-Options: nosniff``，浏览器不会把表外文件按内容嗅探成 HTML。
_RAW_CONTENT_TYPES_BY_SUFFIX: dict[str, str] = {
    ".css": "text/css; charset=utf-8",
    ".gif": "image/gif",
    ".htm": "text/html; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".ico": "image/vnd.microsoft.icon",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
}
_DEFAULT_RAW_CONTENT_TYPE = "application/octet-stream"

#: 工作区那侧的代号。它不是 :mod:`revisions` 里的版本——工作区在磁盘上，不在 git 对象库
#: 里，所以不进那个封闭枚举；但在「旧新两版各自取自哪里」这张表里，它与两个版本并列。
_WORKTREE_SIDE = "worktree"

#: 改动分区的旧新两侧分别取自哪里。已暂存比的是 HEAD ↔ 索引，未暂存比的是索引 ↔ 工作区；
#: 未跟踪还没有进过索引，因此**没有旧侧**。这张表是「改动里的旧新对比到底在比什么」的
#: 唯一出处，界面上的标签也从它推出来。
_SIDES_BY_SECTION: dict[str, tuple[str | None, str]] = {
    "staged": (revisions.HEAD_REVISION, revisions.INDEX_REVISION),
    "unstaged": (revisions.INDEX_REVISION, _WORKTREE_SIDE),
    "untracked": (None, _WORKTREE_SIDE),
}

#: 各侧在界面上叫什么。标签只描述**取自哪里**，不带「旧 / 新」字样——同一份索引在已暂存
#: 分区里是新侧、在未暂存分区里是旧侧，用「旧版本 / 新版本」当标签会在两个分区里各错一次。
_SIDE_LABEL_BY_SOURCE: dict[str, str] = {
    revisions.HEAD_REVISION: "HEAD 版本",
    revisions.INDEX_REVISION: "索引版本",
    _WORKTREE_SIDE: "工作区版本",
}

#: 暂存动作的取值（封闭枚举）。``path`` 只暂存一个路径，``all`` 暂存工作区里全部改动——
#: 与「改动」那一段列出来的东西逐项对应。不在表里的取值一律拒绝，绝不作为参数流进 git。
STAGE_SCOPE_PATH = "path"
STAGE_SCOPE_ALL = "all"
KNOWN_STAGE_SCOPES = frozenset({STAGE_SCOPE_PATH, STAGE_SCOPE_ALL})

#: 文件树不展示的目录名，只作用于**未跟踪**文件。`git ls-files` 已经不吃被 gitignore
#: 的目录，这里再挡一层是为了派生项目没把依赖目录写进 `.gitignore` 时不至于把整棵依赖
#: 树搬进文件树。
#:
#: 刻意不收 `build` / `dist` / `site` 这类既可能是构建产物、也可能是真实源码目录的名字
#: ——本仓库的 `scripts/build/` 就是源码。构建产物由 `.gitignore` 负责，那是「这不是源码」
#: 的权威信号。
_PRUNED_DIRECTORY_NAMES = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".next",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "coverage",
        "node_modules",
        "site-packages",
        "venv",
    }
)

_HUNK_HEADER_PATTERN = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")

_BINARY_DIFF_PREFIX = "Binary files "

_DIFF_METADATA_PREFIXES = (
    "diff --git ",
    "index ",
    "--- ",
    "+++ ",
    "new file mode ",
    "deleted file mode ",
    "old mode ",
    "new mode ",
    "similarity index ",
    "rename from ",
    "rename to ",
    _BINARY_DIFF_PREFIX,
    "\\ No newline at end of file",
)


def build_info_payload(repository_root: Path) -> WorkspacePayload:
    """给出界面启动所需的仓库元信息。

    Args:
        repository_root (Path): 仓库根绝对路径。

    Returns:
        WorkspacePayload: 含仓库名、当前分支与渲染上限的应答。
    """
    return WorkspacePayload(
        status_code=200,
        payload={
            "repo_name": repository_root.name,
            "branch": _read_current_branch_name(repository_root),
            "limits": {
                "max_file_bytes": MAX_FILE_BYTES,
                "max_file_label": MAX_FILE_BYTES_LABEL,
            },
        },
    )


def build_tree_payload(repository_root: Path) -> WorkspacePayload:
    """列出文件树要展示的全部仓库内路径。

    Returns:
        WorkspacePayload: 含扁平路径列表与文件数的应答；前端据此自行组装成树。
    """
    file_paths = collect_viewable_file_paths(repository_root)
    return WorkspacePayload(
        status_code=200, payload={"paths": file_paths, "count": len(file_paths)}
    )


def collect_viewable_file_paths(repository_root: Path) -> list[str]:
    """列出受版本控制与未跟踪（且未被忽略）的全部文件路径。

    受控文件一律照收：被提交进版本库的就是有意的源码，哪怕它的目录名看起来像构建产物
    ——本仓库的 ``scripts/build/`` 正是这种情形，按目录名剪枝会把它整棵藏掉。目录名剪枝
    只作用在**未跟踪**文件上，挡的是派生项目忘了把依赖目录写进 ``.gitignore`` 时把整棵
    依赖树搬进文件树。

    Args:
        repository_root (Path): 仓库根绝对路径。

    Returns:
        list[str]: 已排序的仓库相对路径（POSIX 分隔符）。
    """
    tracked_paths = {
        candidate_path
        for candidate_path in _run_git(repository_root, "ls-files", "-z", "--cached").split("\0")
        if candidate_path
    }
    return sorted(tracked_paths | set(_collect_untracked_file_paths(repository_root)))


def _collect_untracked_file_paths(repository_root: Path) -> list[str]:
    """列出未跟踪、未被忽略且不落在剪枝目录下的文件路径。

    文件树与改动视图的「未跟踪」一段共用这一份口径：两处若各列各的，同一个文件会在
    文件树里被剪掉、却在改动列表里冒出来。

    Args:
        repository_root (Path): 仓库根绝对路径。

    Returns:
        list[str]: 已排序的仓库相对路径。
    """
    return sorted(
        candidate_path
        for candidate_path in _run_git(
            repository_root, "ls-files", "-z", "--others", "--exclude-standard"
        ).split("\0")
        if candidate_path and not _is_pruned_path(candidate_path)
    )


def build_file_payload(repository_root: Path, requested_path: str) -> WorkspacePayload:
    """读取单个文件并按图片、可渲染、二进制、超限四种形态给出应答。

    Args:
        repository_root (Path): 仓库根绝对路径。
        requested_path (str): 界面传来的仓库相对路径。

    Returns:
        WorkspacePayload: 图片应答（``kind: "image"`` + ``url``）、正文应答（带行号渲染
            所需的逐行 HTML，另带 ``preview`` 说明该文本文件支持哪种预览）或明确的形态
            标记（二进制 / 超限）。
    """
    resolved_path = resolve_repository_path(repository_root, requested_path)
    if resolved_path is None:
        return build_refusal_payload(403, OUTSIDE_REPOSITORY_REFUSAL_MESSAGE)

    normalized_relative_path = Path(requested_path).as_posix() if requested_path else ""
    if resolved_path.is_dir():
        return build_refusal_payload(
            400, f"拒绝：{normalized_relative_path or '.'} 是一个目录，请选择一个文件。"
        )
    if not resolved_path.is_file():
        return build_refusal_payload(404, f"未找到文件：{normalized_relative_path}")

    file_byte_count = resolved_path.stat().st_size
    # 图片在读字节之前就返回，因此**不受** 256 KiB 那条上限约束：字节是浏览器拿 URL 自己去
    # 取的，服务端不读、也就没有可省的开销。截图动辄超过 256 KiB，而超限的图片恰恰是最该
    # 能预览的那一类。
    if Path(normalized_relative_path).suffix.lower() in _IMAGE_SUFFIXES:
        return WorkspacePayload(
            status_code=200,
            payload={
                "path": normalized_relative_path,
                "kind": "image",
                "url": build_raw_file_url(normalized_relative_path),
                "size": file_byte_count,
                "size_label": format_size_label(file_byte_count),
            },
        )
    if file_byte_count > MAX_FILE_BYTES:
        return WorkspacePayload(
            status_code=200,
            payload={
                "path": normalized_relative_path,
                "kind": "oversize",
                "size": file_byte_count,
                "size_label": format_size_label(file_byte_count),
                "limit_label": MAX_FILE_BYTES_LABEL,
                "note": f"文件为 {format_size_label(file_byte_count)}，超过 "
                f"{MAX_FILE_BYTES_LABEL} 的渲染上限，未读取正文。",
            },
        )

    raw_file_bytes = resolved_path.read_bytes()
    if b"\0" in raw_file_bytes[:_BINARY_SNIFF_BYTES]:
        return WorkspacePayload(
            status_code=200,
            payload={
                "path": normalized_relative_path,
                "kind": "binary",
                "size": file_byte_count,
                "size_label": format_size_label(file_byte_count),
                "note": "二进制文件，不渲染正文。",
            },
        )

    source_text = raw_file_bytes.decode("utf-8", errors="replace")
    highlighted_source = rendering.highlight_source_lines(source_text, normalized_relative_path)
    return WorkspacePayload(
        status_code=200,
        payload={
            "path": normalized_relative_path,
            "kind": "text",
            "language": highlighted_source.language_label,
            "size": file_byte_count,
            "size_label": format_size_label(file_byte_count),
            "line_count": len(highlighted_source.rendered_lines),
            "highlighted": highlighted_source.is_highlighted,
            "lines": highlighted_source.rendered_lines,
            "preview": resolve_preview_descriptor(normalized_relative_path),
        },
    )


def resolve_preview_descriptor(relative_path: str) -> dict[str, str] | None:
    """给出某个文件支持的预览方式；不支持预览时为 ``None``。

    界面靠这一位决定在内容区头部摆什么控件，而不是自己按后缀判一遍：后缀表只写在
    这里，两处分头维护时新增一种可预览的格式必然漏掉其中一边。

    Args:
        relative_path (str): 仓库相对路径。

    Returns:
        dict[str, str] | None: ``{"mode": "markdown"}``、``{"mode": "external",
            "url": "/raw/..."}``，或 ``None``。
    """
    file_suffix = Path(relative_path).suffix.lower()
    if file_suffix in _MARKDOWN_SUFFIXES:
        return {"mode": "markdown"}
    if file_suffix in _HTML_SUFFIXES:
        return {"mode": "external", "url": build_raw_file_url(relative_path)}
    return None


def build_raw_file_url(relative_path: str, revision_name: str | None = None) -> str:
    """把仓库相对路径拼成 ``/raw/`` 路由下的 URL。

    逐段编码而不是整串 ``quote``：路径分隔符必须保持字面 ``/``，否则 ``/raw/`` 之后
    会被当成一个巨大的文件名，而文件名里的 ``%2F`` 解码回来也不是目录层级。

    Args:
        relative_path (str): 仓库相对路径（POSIX 分隔符）。
        revision_name (str | None): 要取的历史版本；``None`` 表示工作区当前版本。

    Returns:
        str: 编码后的 ``/raw/`` URL。
    """
    encoded_segments = [quote(path_segment, safe="") for path_segment in relative_path.split("/")]
    raw_file_url = f"{RAW_ROUTE_PREFIX}{'/'.join(encoded_segments)}"
    if revision_name is None:
        return raw_file_url
    return f"{raw_file_url}?{RAW_REVISION_QUERY_PARAMETER}={quote(revision_name, safe='')}"


def _build_markdown_reference_url(attribute_name: str, repository_relative_path: str) -> str:
    """决定 Markdown 正文里一个相对引用最终指向的地址。

    ``src`` 一律指向 ``/raw/``（图片要的是字节）。``href`` 指向另一份 Markdown 时走查看器的
    直达链接，其余照旧指向 ``/raw/``——判断依据只有后缀，与 :func:`resolve_preview_descriptor`
    同一口径。

    Args:
        attribute_name (str): 被改写的属性名，``src`` 或 ``href``。
        repository_relative_path (str): 已解析好的仓库相对路径（POSIX 分隔符）。

    Returns:
        str: 该引用最终指向的地址。
    """
    if (
        attribute_name == "href"
        and PurePosixPath(repository_relative_path).suffix.lower() in _MARKDOWN_SUFFIXES
    ):
        return f"{_VIEWER_FILES_VIEW_URL_PREFIX}{quote(repository_relative_path, safe='')}"
    return build_raw_file_url(repository_relative_path)


def build_markdown_payload(repository_root: Path, requested_path: str) -> WorkspacePayload:
    """把单个 Markdown 文件渲染成 HTML 片段，供界面的「预览」开关按需取回。

    按需而不是随 :func:`build_file_payload` 一起返回：文件视图打开 ``.md`` 先看到的是
    源码，每次打开都顺带渲染会让正文应答白白胖一倍，而多数时候那份 HTML 没人看。

    Args:
        repository_root (Path): 仓库根绝对路径。
        requested_path (str): 界面传来的仓库相对路径。

    Returns:
        WorkspacePayload: ``{"format": "markdown", "html": ...}``；路径越界、不是
            Markdown 文件、文件缺失、超出渲染上限或渲染依赖缺失时为拒绝应答。
    """
    resolved_path = resolve_repository_path(repository_root, requested_path)
    if resolved_path is None:
        return build_refusal_payload(403, OUTSIDE_REPOSITORY_REFUSAL_MESSAGE)

    normalized_relative_path = Path(requested_path).as_posix() if requested_path else ""
    if Path(normalized_relative_path).suffix.lower() not in _MARKDOWN_SUFFIXES:
        return build_refusal_payload(
            400,
            f"拒绝：{normalized_relative_path or '.'} 不是 Markdown 文件，没有可渲染的预览。",
        )
    if not resolved_path.is_file():
        return build_refusal_payload(404, f"未找到文件：{normalized_relative_path}")
    # 上限与正文渲染同一口径：超限文件在正文侧本来就走 oversize 分支，预览侧再放一次
    # 就等于绕开了那条上限。
    if resolved_path.stat().st_size > MAX_FILE_BYTES:
        return build_refusal_payload(
            400,
            f"拒绝：文件超过 {MAX_FILE_BYTES_LABEL} 的渲染上限，请用本地编辑器打开。",
        )

    rendered_html = rendering.render_markdown_document(
        resolved_path.read_bytes().decode("utf-8", errors="replace")
    )
    if rendered_html is None:
        return build_refusal_payload(
            503, "服务端未安装 Markdown 渲染依赖，无法生成预览，请阅读源码。"
        )
    # 正文里的相对引用是相对**这个文件所在目录**写的，而预览片段会被内联进查看器页面
    # （`/`），不改写的话图片与站内链接全部指向页面根。口径见 rendering.rebase_relative_references。
    return WorkspacePayload(
        status_code=200,
        payload={
            "format": "markdown",
            "html": rendering.rebase_relative_references(
                rendered_html,
                posixpath.dirname(normalized_relative_path),
                _build_markdown_reference_url,
            ),
        },
    )


@dataclass(frozen=True)
class RawFilePayload:
    """一个原始文件字节应答，供 ``/raw/`` 路由原样返回。

    Attributes:
        status_code (int): 应答的 HTTP 状态码。
        content_type (str): 应答的 ``Content-Type``。
        body_bytes (bytes): 应答正文。
    """

    status_code: int
    content_type: str
    body_bytes: bytes


def build_raw_file_payload(
    repository_root: Path, requested_path: str
) -> RawFilePayload | WorkspacePayload:
    """按仓库相对路径原样返回文件字节，供 HTML 文件在自己的标签页里打开。

    ``/raw/`` 是唯一一条**保持路径原样**的路由，而且必须保持：HTML 文档里的相对引用
    （``./a.css``、``../img/i.png``）要能解析回同一路由、真的加载出来。替代的防护是
    照旧走 :func:`resolve_repository_path` 的解析与越界断言——保持原样指的是 URL，
    不是边界。

    Args:
        repository_root (Path): 仓库根绝对路径。
        requested_path (str): 已解码的仓库相对路径。

    Returns:
        RawFilePayload | WorkspacePayload: 命中时为原始字节应答；路径越界、指向目录或
            文件缺失时为 JSON 拒绝应答。
    """
    resolved_path = resolve_repository_path(repository_root, requested_path)
    if resolved_path is None:
        return build_refusal_payload(403, OUTSIDE_REPOSITORY_REFUSAL_MESSAGE)

    normalized_relative_path = Path(requested_path).as_posix() if requested_path else ""
    if resolved_path.is_dir():
        return build_refusal_payload(
            400, f"拒绝：{normalized_relative_path or '.'} 是一个目录，请选择一个文件。"
        )
    if not resolved_path.is_file():
        return build_refusal_payload(404, f"未找到文件：{normalized_relative_path}")

    return RawFilePayload(
        status_code=200,
        content_type=resolve_raw_content_type(normalized_relative_path),
        body_bytes=resolved_path.read_bytes(),
    )


def resolve_raw_content_type(relative_path: str) -> str:
    """按后缀给出 ``/raw/`` 应答的 Content-Type，表外一律二进制流。"""
    return _RAW_CONTENT_TYPES_BY_SUFFIX.get(
        Path(relative_path).suffix.lower(), _DEFAULT_RAW_CONTENT_TYPE
    )


def build_revision_file_payload(
    repository_root: Path, requested_path: str, revision_name: str
) -> RawFilePayload | WorkspacePayload:
    """按 git 版本（HEAD / 索引）返回文件的原始字节。

    改动视图对图片改动要在同一页里给出旧新两版，而工作区只存在新侧；旧侧只能从对象库读
    （见 :mod:`revisions`）。**按版本读与读工作区走同一条边界**：路径照旧先经
    :func:`resolve_repository_path` 解析并断言仍在仓库根之下，不因为换了数据来源就松一格。

    Args:
        repository_root (Path): 仓库根绝对路径。
        requested_path (str): 界面传来的仓库相对路径。
        revision_name (str): :data:`revisions.KNOWN_REVISIONS` 里的取值。

    Returns:
        RawFilePayload | WorkspacePayload: 命中时为原始字节应答；版本取值不在封闭枚举里、
            路径越界、指向目录、或该版本里没有这个文件时为 JSON 拒绝应答。
    """
    if not revisions.is_known_revision(revision_name):
        return build_refusal_payload(
            400,
            f"拒绝：{revision_name} 不是可用的版本，"
            f"请选择「{'」「'.join(sorted(revisions.KNOWN_REVISIONS))}」。",
        )

    resolved_path = resolve_repository_path(repository_root, requested_path)
    if resolved_path is None:
        return build_refusal_payload(403, OUTSIDE_REPOSITORY_REFUSAL_MESSAGE)

    normalized_relative_path = Path(requested_path).as_posix() if requested_path else ""
    if resolved_path.is_dir():
        return build_refusal_payload(
            400, f"拒绝：{normalized_relative_path or '.'} 是一个目录，请选择一个文件。"
        )

    blob_bytes = revisions.read_blob_bytes(
        repository_root, revision_name=revision_name, relative_path=normalized_relative_path
    )
    if blob_bytes is None:
        return build_refusal_payload(404, f"该版本里没有这个文件：{normalized_relative_path}")
    return RawFilePayload(
        status_code=200,
        content_type=resolve_raw_content_type(normalized_relative_path),
        body_bytes=blob_bytes,
    )


def stage_changes(repository_root: Path, requested_path: str) -> WorkspacePayload:
    """把单个路径的当前状态加进索引（``git add``）——查看器唯一的写操作。

    查看器从「只能看」变成「只能看 + 只能暂存」：这一个动作是它被允许对仓库做的**全部**改变。
    它不改文件内容、不提交、不丢弃、不取消暂存，也不碰索引之外的东西。之所以只开这一个口子，
    是因为界面上「把这一处改动收进索引」是最高频的下一步动作；其余写操作（提交、撤销暂存、
    丢弃改动）都留在用户惯用的工具里。

    路径先经 :func:`resolve_repository_path` 断言仍在仓库根之下，再作为 ``--`` 之后的单个
    argv 元素交给 git，因此以 ``-`` 开头的路径不会被当成选项。

    Args:
        repository_root (Path): 仓库根绝对路径。
        requested_path (str): 界面传来的仓库相对路径。

    Returns:
        WorkspacePayload: 成功时是 ``{"scope": "path", "path": ...}``；路径越界或 git 拒绝
            （例如路径已不存在）时为拒绝应答，后者按 :class:`WorkspaceCommandError` 冒泡。
    """
    resolved_path = resolve_repository_path(repository_root, requested_path)
    if resolved_path is None:
        return build_refusal_payload(403, OUTSIDE_REPOSITORY_REFUSAL_MESSAGE)

    normalized_relative_path = Path(requested_path).as_posix() if requested_path else ""
    if not normalized_relative_path:
        return build_refusal_payload(400, "拒绝：暂存需要给出一个仓库内的路径。")
    _run_git(repository_root, "add", "--", normalized_relative_path)
    return WorkspacePayload(
        status_code=200,
        payload={"scope": STAGE_SCOPE_PATH, "path": normalized_relative_path},
    )


def stage_all_changes(repository_root: Path) -> WorkspacePayload:
    """把工作区里全部改动加进索引（``git add -A``）——界面「改动」那一段的「全部暂存」。

    ``-A`` 正好对应「改动」那一段列出的东西：已改的、已删的、以及未被忽略的新文件都在内，
    被忽略的文件永远不进索引。它不会漏掉删除，也不会把工作区里已暂存之后又改过的内容留在索引外。

    Args:
        repository_root (Path): 仓库根绝对路径。

    Returns:
        WorkspacePayload: 成功时是 ``{"scope": "all"}``；git 拒绝时按
            :class:`WorkspaceCommandError` 冒泡。
    """
    _run_git(repository_root, "add", "-A")
    return WorkspacePayload(status_code=200, payload={"scope": STAGE_SCOPE_ALL})


def build_changes_payload(repository_root: Path) -> WorkspacePayload:
    """给出三个分区各自的改动文件集合与增删统计。

    Args:
        repository_root (Path): 仓库根绝对路径。

    Returns:
        WorkspacePayload: 三个分区（已暂存 / 未暂存 / 未跟踪）的文件列表、分区合计与
            三区合计。空分区同样返回，界面据此显示「已暂存 0」。

    界面上把后两段合并成一段「Changes」显示（见 ``docs/guides/file-viewer.md``），但这里仍按
    三段给：三段的 git 口径不同（HEAD↔索引 / 索引↔工作区 / 未跟踪），单文件 diff 与暂存动作
    都要知道自己面对的是哪一种，合并只发生在显示层。
    """
    sections: list[dict[str, object]] = []
    for section_name, section_label in _SECTION_LABELS.items():
        if section_name in _SECTION_DIFF_ARGUMENT_PREFIXES:
            changed_files = _collect_index_section_files(repository_root, section_name)
            has_stats = True
        else:
            # 未跟踪那一段只列文件、不给 +N -M。git 的列表类命令都不为未跟踪文件报统计，
            # 唯一口径是逐个文件跑一次 ``--no-index --numstat``；本机实测每个文件约 8ms，
            # 800 个未跟踪文件要 7 秒左右（并发跑到 8 路也只降到 4 秒，瓶颈在进程创建），
            # 页面会像卡死。逐行 diff 仍由 ``--no-index`` 在点击时才取一次。
            #
            # ``add`` / ``del`` 留 ``None`` 表示「本轮不提供」，由 ``has_stats`` 与另外两段
            # 区分开——**不提供**与**二进制**在界面上是两件事，不能共用同一个 ``None``。
            changed_files = [
                {"path": untracked_path, "status": "A", "add": None, "del": None}
                for untracked_path in _collect_untracked_file_paths(repository_root)
            ]
            has_stats = False
        sections.append(
            {
                "section": section_name,
                "label": section_label,
                "stats_available": has_stats,
                "files": changed_files,
                "totals": _total_changed_files(changed_files),
            }
        )

    all_files = [entry for section in sections for entry in section["files"]]
    return WorkspacePayload(
        status_code=200,
        payload={
            "sections": sections,
            "totals": _total_changed_files(all_files),
        },
    )


def _collect_index_section_files(
    repository_root: Path, section_name: str
) -> list[dict[str, object]]:
    """列出「已暂存」或「未暂存」分区下的改动文件。

    两个分区只差一个 ``--cached``，因此共用这条实现：分别各写一份会让口径悄悄分岔。

    Args:
        repository_root (Path): 仓库根绝对路径。
        section_name (str): ``staged`` 或 ``unstaged``。

    Returns:
        list[dict[str, object]]: 已按路径排序的改动文件条目。
    """
    section_arguments = _SECTION_DIFF_ARGUMENT_PREFIXES[section_name]
    status_entry_by_path = _parse_status_entries(
        _run_git(repository_root, *section_arguments, "--name-status", "-z")
    )
    numstat_by_path = _parse_numstat_entries(
        _run_git(repository_root, *section_arguments, "--numstat", "-z")
    )

    changed_files: list[dict[str, object]] = []
    for changed_path in sorted(status_entry_by_path):
        added_count, deleted_count = numstat_by_path.get(changed_path, (None, None))
        changed_files.append(
            {
                "path": changed_path,
                "status": status_entry_by_path[changed_path][0],
                "add": added_count,
                "del": deleted_count,
            }
        )
    return changed_files


def _total_changed_files(
    changed_files: list[dict[str, object]],
) -> dict[str, int]:
    """把一组改动文件条目汇总成文件数与增删合计。"""
    return {
        "files": len(changed_files),
        "add": sum(entry["add"] or 0 for entry in changed_files),
        "del": sum(entry["del"] or 0 for entry in changed_files),
    }


def build_diff_payload(
    repository_root: Path, requested_path: str, section_name: str
) -> WorkspacePayload:
    """给出单个文件在某个改动分区下的逐行改动。

    Args:
        repository_root (Path): 仓库根绝对路径。
        requested_path (str): 界面传来的仓库相对路径。
        section_name (str): 改动分区取值，必须是 :data:`_SECTION_LABELS` 的键之一。

    Returns:
        WorkspacePayload: 逐行 diff 应答；路径越界、文件不存在或分区取值不可用时为
            拒绝应答。正文含 ``rename_from``：该文件是重命名而来时给出旧路径，否则为
            ``None``。
    """
    section_label = _SECTION_LABELS.get(section_name)
    if section_label is None:
        return build_refusal_payload(
            400,
            f"拒绝：{section_name} 不是可用的改动分区，"
            f"请选择「{'」「'.join(_SECTION_LABELS.values())}」。",
        )

    resolved_path = resolve_repository_path(repository_root, requested_path)
    if resolved_path is None:
        return build_refusal_payload(403, OUTSIDE_REPOSITORY_REFUSAL_MESSAGE)

    normalized_relative_path = Path(requested_path).as_posix()
    if section_name == "untracked":
        # 未跟踪文件没有可配对的旧路径，也没有索引侧可以比较；它整篇对着 /dev/null 求
        # diff。文件已被删除时提前拒绝，否则 git 的非零退出会变成 500 而不是明确应答。
        if not resolved_path.is_file():
            return build_refusal_payload(404, f"未找到文件：{normalized_relative_path}")
        rename_source = None
        diff_text = _run_git(
            repository_root,
            "diff",
            "--no-index",
            "--",
            _UNTRACKED_DIFF_LEFT_PATH,
            normalized_relative_path,
            allowed_exit_codes=_DIFF_NO_INDEX_EXIT_CODES,
        )
    else:
        section_arguments = _SECTION_DIFF_ARGUMENT_PREFIXES[section_name]
        rename_source = _lookup_rename_source(
            repository_root, section_arguments, normalized_relative_path
        )
        # 重命名必须连旧路径一起作为 pathspec 交给 git，配对才成立；只给新路径会让同一个
        # 文件降级成「新增」，正文整篇算成新增行。
        diff_pathspecs = (
            [rename_source, normalized_relative_path]
            if rename_source
            else [normalized_relative_path]
        )
        diff_text = _run_git(repository_root, *section_arguments, "-M", "--", *diff_pathspecs)

    parsed_diff = _parse_unified_diff_rows(diff_text)
    return WorkspacePayload(
        status_code=200,
        payload={
            "path": normalized_relative_path,
            "section": section_name,
            "section_label": section_label,
            "rename_from": rename_source,
            "rows": parsed_diff.rows,
            "truncated": parsed_diff.is_truncated,
            "binary": parsed_diff.is_binary,
            "empty": not parsed_diff.rows,
            # 图片改动没有逐行内容可看，但两版画面本身是可比的；其余二进制（压缩包、
            # 可执行文件）没有可比画面，这里给 ``None``，界面照旧只说「无逐行改动」。
            #
            # 必须同时要求 git 判定「这是一处二进制改动」：该路径不在本分区时 diff 是空的，
            # 但两版的 blob 照样存在（工作区文件在磁盘上、索引条目也在），只看后缀会为一条
            # 并不存在的改动凑出一对图。
            "image_comparison": _build_image_comparison(
                repository_root,
                _ImageComparisonRequest(
                    section_name=section_name,
                    new_side_path=normalized_relative_path,
                    old_side_path=rename_source or normalized_relative_path,
                    is_binary_change=parsed_diff.is_binary,
                ),
            ),
        },
    )


@dataclass(frozen=True)
class _ImageComparisonRequest:
    """一次图片对比的输入。

    Attributes:
        section_name (str): 改动分区取值。
        new_side_path (str): 新侧路径，也是界面上显示的那个路径。
        old_side_path (str): 旧侧路径。重命名时是旧路径——旧版本里那个位置存的是旧路径
            的图画，按新路径去取只会取不到，然后把「重命名」说成「新增」。
        is_binary_change (bool): git 是否把这次改动判成二进制改动。
    """

    section_name: str
    new_side_path: str
    old_side_path: str
    is_binary_change: bool


def _build_image_comparison(
    repository_root: Path, comparison_request: _ImageComparisonRequest
) -> dict[str, object] | None:
    """给出图片改动旧新两版的地址与大小；不是图片、或一版都取不到时返回 ``None``。

    后缀判定在最前面短路，因此**文本文件一次 git 调用都不会多**。

    Args:
        repository_root (Path): 仓库根绝对路径。
        comparison_request (_ImageComparisonRequest): 本次对比的路径、分区与二进制标记。

    Returns:
        dict[str, object] | None: ``{"panes": [...], "note": str}``。``panes`` 是取得到的
            那些版本（0–2 个，按旧→新排列），``note`` 解释缺的那一版为什么缺；不是图片、
            本分区里没有这一处改动、或一版都取不到时为 ``None``。
    """
    if not comparison_request.is_binary_change:
        return None
    if Path(comparison_request.new_side_path).suffix.lower() not in _IMAGE_SUFFIXES:
        return None

    old_side_source, new_side_source = _SIDES_BY_SECTION[comparison_request.section_name]
    if old_side_source is None and not _is_untracked_file(
        repository_root, comparison_request.new_side_path
    ):
        # 未跟踪这一段只有旧侧为空，而「未跟踪」是这一段的**成员资格**，不是「文件碰巧没有
        # 索引条目」：拿一个已跟踪的路径来问这一段，会在界面上得到一句「还没有进过索引」的
        # 假话。宁可什么都不给。
        return None
    old_pane = (
        _build_image_pane(
            repository_root,
            comparison_request.old_side_path,
            old_side_source,
            _build_side_label(old_side_source, comparison_request),
        )
        if old_side_source is not None
        else None
    )
    new_pane = _build_image_pane(
        repository_root,
        comparison_request.new_side_path,
        new_side_source,
        _SIDE_LABEL_BY_SOURCE[new_side_source],
    )
    panes = [pane for pane in (old_pane, new_pane) if pane is not None]
    if not panes:
        return None
    return {
        "panes": panes,
        "note": _explain_missing_image_sides(old_side_source, old_pane, new_pane),
    }


def _build_side_label(side_source: str, comparison_request: _ImageComparisonRequest) -> str:
    """拼出旧侧的标签；重命名时把旧路径一并写出来。

    重命名的那一版图画存在**旧路径**上，标签只写「HEAD 版本」会让人以为界面上显示的路径
    就是它，而新路径在那一版里根本不存在。
    """
    side_label = _SIDE_LABEL_BY_SOURCE[side_source]
    if comparison_request.old_side_path == comparison_request.new_side_path:
        return side_label
    return f"{side_label}（{comparison_request.old_side_path}）"


def _is_untracked_file(repository_root: Path, normalized_relative_path: str) -> bool:
    """判断这个路径是不是真的未跟踪，口径与改动列表的未跟踪那一段一致（含目录剪枝）。

    Args:
        repository_root (Path): 仓库根绝对路径。
        normalized_relative_path (str): 仓库相对路径。

    Returns:
        bool: 是否属于未跟踪且未被忽略、且不在剪枝目录下的文件。
    """
    if _is_pruned_path(normalized_relative_path):
        return False
    listed_output = _run_git(
        repository_root,
        "ls-files",
        "-z",
        "--others",
        "--exclude-standard",
        "--",
        normalized_relative_path,
    )
    return bool(listed_output.strip("\0"))


def _build_image_pane(
    repository_root: Path, side_path: str, side_source: str, side_label: str
) -> dict[str, object] | None:
    """给出某一版的图片地址、大小与标签；那一版里没有这个文件时返回 ``None``。

    工作区那侧走的是「解析路径 + 读磁盘」，与 ``/raw/`` 的默认分支同一份口径；历史版本那侧
    从对象库读大小（不读字节——界面只是把地址交给浏览器，服务端不必把图片读进内存）。

    Args:
        repository_root (Path): 仓库根绝对路径。
        side_path (str): 这一版里该文件的路径（重命名时旧侧是旧路径）。
        side_source (str): 取自 :data:`_SIDES_BY_SECTION` 的来源取值。
        side_label (str): 界面上显示给这一版的标签。

    Returns:
        dict[str, object] | None: ``{"label", "url", "size_label"}``，或 ``None``。
    """
    if side_source == _WORKTREE_SIDE:
        worktree_path = resolve_repository_path(repository_root, side_path)
        if worktree_path is None or not worktree_path.is_file():
            return None
        size_bytes = worktree_path.stat().st_size
        raw_file_url = build_raw_file_url(side_path)
    else:
        size_bytes = revisions.read_blob_size(
            repository_root,
            revision_name=side_source,
            relative_path=side_path,
        )
        if size_bytes is None:
            return None
        raw_file_url = build_raw_file_url(side_path, revision_name=side_source)
    return {
        "label": side_label,
        "url": raw_file_url,
        "size_label": format_size_label(size_bytes),
    }


def _explain_missing_image_sides(
    old_side_source: str | None,
    old_pane: dict[str, object] | None,
    new_pane: dict[str, object] | None,
) -> str:
    """写清缺的那一版为什么缺。

    单张图配一个「某某版本」的标签，读者没法判断是「那一版没有这个文件」还是「界面懒得
    给」；这一句把结论直说，且只说服务端确知的事。
    """
    missing_side_notes: list[str] = []
    if old_side_source is None:
        missing_side_notes.append("未跟踪文件还没有进过索引，只有工作区这一版可比。")
    elif old_pane is None:
        missing_side_notes.append(
            f"「{_SIDE_LABEL_BY_SOURCE[old_side_source]}」里没有这个文件——这次改动新增了它。"
        )
    if new_pane is None:
        missing_side_notes.append("这次改动删除了它，新的一版里没有这个文件。")
    return "".join(missing_side_notes)


def format_size_label(byte_count: int) -> str:
    """把字节数渲染成人类可读的大小标签。

    Args:
        byte_count (int): 字节数。

    Returns:
        str: 形如 ``512 B`` / ``1.5 KB`` / ``2.3 MB`` 的标签。
    """
    if byte_count < 1024:
        return f"{byte_count} B"
    if byte_count < 1024 * 1024:
        return f"{byte_count / 1024:.1f} KB"
    return f"{byte_count / (1024 * 1024):.1f} MB"


def _is_pruned_path(relative_path: str) -> bool:
    """判断路径是否位于文件树不展示的目录下。"""
    return any(
        path_segment in _PRUNED_DIRECTORY_NAMES for path_segment in relative_path.split("/")[:-1]
    )


def _read_current_branch_name(repository_root: Path) -> str:
    """读取当前检出的分支名；分离头指针时回退为短提交号。"""
    branch_output = _run_git(repository_root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    if branch_output and branch_output != "HEAD":
        return branch_output
    return _run_git(repository_root, "rev-parse", "--short", "HEAD").strip()


def _parse_status_entries(status_output: str) -> dict[str, tuple[str, str | None]]:
    """解析 ``git diff --name-status -z``，返回 新路径 -> (状态字母, 重命名来源)。

    重命名与复制条目带两个路径（旧、新）。键取新路径——终端 ``--name-only`` 在同一次
    diff 上也只列新路径，两边必须逐项一致。旧路径单独留在值里，是因为单文件 diff 需要
    它才能把配对还原（见 :func:`_lookup_rename_source`）；非重命名条目该位为 ``None``。
    """
    output_tokens = status_output.split("\0")
    status_entry_by_path: dict[str, tuple[str, str | None]] = {}
    token_index = 0
    while token_index < len(output_tokens):
        status_token = output_tokens[token_index]
        token_index += 1
        if not status_token:
            continue
        is_rename_or_copy = status_token[0] in {"R", "C"}
        source_path = (
            output_tokens[token_index]
            if is_rename_or_copy and token_index < len(output_tokens) and output_tokens[token_index]
            else None
        )
        path_token_index = token_index + 1 if is_rename_or_copy else token_index
        token_index = path_token_index + 1
        if path_token_index < len(output_tokens) and output_tokens[path_token_index]:
            status_entry_by_path[output_tokens[path_token_index]] = (
                status_token[0],
                source_path,
            )
    return status_entry_by_path


def _lookup_rename_source(
    repository_root: Path, section_arguments: tuple[str, ...], changed_path: str
) -> str | None:
    """查出 ``changed_path`` 是否由某条旧路径重命名而来，是则返回该旧路径。

    必须在**不带 pathspec 的完整 diff** 上查：``git diff <rev> -- <新路径>`` 把旧路径
    排除出候选，同一个文件会被降级成「新增」，查不到任何配对。

    Args:
        repository_root (Path): 仓库根绝对路径。
        section_arguments (tuple[str, ...]): 该分区的 ``git diff`` 参数前缀。
        changed_path (str): 仓库相对的新路径。

    Returns:
        str | None: 重命名来源的仓库相对路径；不是重命名时为 ``None``。
    """
    status_entry_by_path = _parse_status_entries(
        _run_git(repository_root, *section_arguments, "--name-status", "-z")
    )
    status_entry = status_entry_by_path.get(changed_path)
    return status_entry[1] if status_entry else None


def _parse_numstat_entries(numstat_output: str) -> dict[str, tuple[int | None, int | None]]:
    """解析 ``git diff --numstat -z``，返回 新路径 -> (新增行数, 删除行数)。

    二进制文件的计数字段是 ``-``，按 ``None`` 保留：界面据此显示「二进制」而不是
    假装有 0 行改动。
    """
    output_tokens = numstat_output.split("\0")
    counts_by_path: dict[str, tuple[int | None, int | None]] = {}
    token_index = 0
    while token_index < len(output_tokens):
        statistics_token = output_tokens[token_index]
        token_index += 1
        if not statistics_token:
            continue
        added_field, _, remainder_field = statistics_token.partition("\t")
        deleted_field, _, path_field = remainder_field.partition("\t")
        if path_field:
            # 普通条目：统计字段与路径同占一个 token。
            changed_path = path_field
        elif token_index + 1 < len(output_tokens):
            # 重命名条目：统计字段自成一个 token，其后的旧路径与新路径各占一个；与
            # ``--name-status -z`` 一样只取新路径，才能和终端 ``--name-only`` 对齐。
            changed_path = output_tokens[token_index + 1]
            token_index += 2
        else:
            continue
        counts_by_path[changed_path] = (
            _parse_count_field(added_field),
            _parse_count_field(deleted_field),
        )
    return counts_by_path


def _parse_count_field(raw_count_field: str) -> int | None:
    """把 numstat 的计数字段转成整数；二进制文件的 ``-`` 返回 ``None``。"""
    return int(raw_count_field) if raw_count_field.isdigit() else None


@dataclass(frozen=True)
class _ParsedDiff:
    """一份 unified diff 解析后的结果。

    Attributes:
        rows (list[dict[str, object]]): 逐行结构。
        is_truncated (bool): 是否因超出行数上限被截断。
        is_binary (bool): git 是否判定为二进制。二进制 diff 没有任何逐行内容，只留一行
            ``Binary files ... differ``；不单独记这一位，「没有改动」与「改动是二进制的」
            就会被界面说成同一件事。
    """

    rows: list[dict[str, object]]
    is_truncated: bool
    is_binary: bool


def _parse_unified_diff_rows(diff_text: str) -> _ParsedDiff:
    """把 unified diff 文本解析成带新旧行号的逐行结构。

    Args:
        diff_text (str): ``git diff`` 的原始输出。

    Returns:
        _ParsedDiff: 逐行结构、截断标记与二进制标记。
    """
    diff_rows: list[dict[str, object]] = []
    old_line_number = 0
    new_line_number = 0
    is_truncated = False
    is_binary = False
    for diff_line in diff_text.splitlines():
        if len(diff_rows) >= MAX_DIFF_ROWS:
            is_truncated = True
            break
        if diff_line.startswith(_BINARY_DIFF_PREFIX):
            is_binary = True
            continue
        hunk_match = _HUNK_HEADER_PATTERN.match(diff_line)
        if hunk_match:
            old_line_number = int(hunk_match.group(1))
            new_line_number = int(hunk_match.group(2))
            diff_rows.append(
                {
                    "kind": "hunk",
                    "old_no": None,
                    "new_no": None,
                    "text": diff_line,
                }
            )
            continue
        if any(diff_line.startswith(prefix) for prefix in _DIFF_METADATA_PREFIXES):
            continue
        if diff_line.startswith("+"):
            diff_rows.append(
                {"kind": "add", "old_no": None, "new_no": new_line_number, "text": diff_line[1:]}
            )
            new_line_number += 1
        elif diff_line.startswith("-"):
            diff_rows.append(
                {"kind": "del", "old_no": old_line_number, "new_no": None, "text": diff_line[1:]}
            )
            old_line_number += 1
        elif diff_line.startswith(" "):
            diff_rows.append(
                {
                    "kind": "ctx",
                    "old_no": old_line_number,
                    "new_no": new_line_number,
                    "text": diff_line[1:],
                }
            )
            old_line_number += 1
            new_line_number += 1
    return _ParsedDiff(rows=diff_rows, is_truncated=is_truncated, is_binary=is_binary)


def _run_git(
    repository_root: Path,
    *git_arguments: str,
    allowed_exit_codes: frozenset[int] = frozenset({0}),
) -> str:
    """在仓库根执行一次 ``git`` 命令并返回标准输出。

    读路径用的都是查询，写路径只有 ``git add``（见 :func:`stage_changes`）；两者共用这个
    入口，因此这里不假设调用方是只读的——边界由「哪些子命令被调用」决定，而不是由这个函数。

    Args:
        repository_root (Path): 仓库根绝对路径。
        *git_arguments (str): 传给 ``git`` 的参数（不含 ``git`` 本身）。
        allowed_exit_codes (frozenset[int]): 视为成功的退出码。默认只认 ``0``；``git
            diff --no-index`` 这类「有差异即退出 1」的子命令由调用方显式放宽。

    Returns:
        str: 命令的标准输出。

    Raises:
        WorkspaceCommandError: ``git`` 的退出码不在 ``allowed_exit_codes`` 里。
    """
    completed_process = subprocess.run(
        ["git", "--no-pager", *git_arguments],
        cwd=repository_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed_process.returncode not in allowed_exit_codes:
        raise WorkspaceCommandError(
            f"git {' '.join(git_arguments)} 执行失败：{completed_process.stderr.strip()}"
        )
    return completed_process.stdout
