"""仓库工作区的只读快照：文件树、文件正文、改动列表与单文件 diff。

查看器的全部内容都从这里出，而且**只读**：所有 ``git`` 调用都是查询
（``ls-files`` / ``diff`` / ``rev-parse`` / ``for-each-ref``），所有文件访问都是读取。
这里不存在任何写路径——只读是硬边界，不是「本期先不做」。

改动视图的数据源固定为真实 ``git``，口径与终端逐项一致：工作区基线是
``git diff HEAD``，分支基线是 ``git diff <分支>...HEAD``（取合并基点）。界面显示的
文件集合与增删统计不做二次推断，必须与同参数的终端输出逐项一致。

重命名是这条口径上唯一的例外，而且必须例外：``git diff <rev> -- <新路径>`` 会把旧路径
排除出候选，配对随即失效，同一个文件被降级成「新增」且正文整篇算成新增行。所以单文件
diff 先在不带 pathspec 的完整 diff 上查出旧路径，再把新旧两条路径一起交给 ``git``
（见 :func:`_lookup_rename_source`）。界面上显示的仍是新路径，与终端 ``--name-only``
一致；旧路径只作为「重命名自何处」的出处。

所有对外路径参数先经 :func:`resolve_repository_path` 解析成绝对路径并断言仍在仓库根
之下，越界一律拒绝，且拒绝信息不回声任何绝对路径。
"""

from __future__ import annotations

import html
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

#: 改动视图中「当前工作区」这条基线的取值，其余取值是本地分支名。
WORKTREE_BASELINE = "worktree"
WORKTREE_BASELINE_LABEL = "工作区改动"

#: 文件正文的渲染上限；超过即返回明确标记而不是正文。
MAX_FILE_BYTES = 256 * 1024
MAX_FILE_BYTES_LABEL = "256 KiB"

#: 单文件 diff 的行数上限，避免超大改动把响应撑爆。
MAX_DIFF_ROWS = 4000

_BINARY_SNIFF_BYTES = 8192

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

#: Pygments 认不出来的仓库惯用文件名，映射到显式指定的词法器别名与展示标签。
#:
#: 只放「按扩展名判不出来、但语义有明确最近邻」的名字，不放任何仓库专属路径。标签
#: 刻意写明是近似匹配：``justfile.shared`` 用 Makefile 词法器高亮，界面若只写
#: 「Makefile」会让人以为渲染错了语言。
#:
#: - ``justfile`` / ``justfile.shared``：Pygments 2.x 没有 Just 词法器，而 just 的
#:   配方语法与 Make 同源（``target:`` 加缩进 recipe）。按 Make 渲染仍能正确着色
#:   注释、目标名与内嵌 shell，比整篇纯文本更接近真实语义。
#: - ``uv.lock``：内容就是 TOML，Pygments 只按 ``*.toml`` 匹配扩展名。
_FALLBACK_LEXERS_BY_FILENAME: dict[str, tuple[str, str]] = {
    "justfile": ("make", "Just（Makefile 词法器近似）"),
    "justfile.shared": ("make", "Just（Makefile 词法器近似）"),
    "uv.lock": ("toml", "TOML"),
}

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
    "Binary files ",
    "\\ No newline at end of file",
)
_SPAN_TAG_PATTERN = re.compile(r"</?span[^>]*>")
_SPAN_CLASS_PATTERN = re.compile(r'class="([^"]*)"')


class WorkspaceReadError(RuntimeError):
    """读取仓库工作区失败，例如 ``git`` 调用非零退出。"""


@dataclass(frozen=True)
class WorkspacePayload:
    """一个只读接口的应答：HTTP 状态码加 JSON 载荷。

    Attributes:
        status_code (int): 应答的 HTTP 状态码。
        payload (dict[str, object]): 应答正文，会被序列化成 JSON。
    """

    status_code: int
    payload: dict[str, object]


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


def build_info_payload(repository_root: Path) -> WorkspacePayload:
    """给出界面启动所需的仓库元信息。

    Args:
        repository_root (Path): 仓库根绝对路径。

    Returns:
        WorkspacePayload: 含仓库名、当前分支、可选基线与渲染上限的应答。
    """
    baseline_options: list[dict[str, str]] = [
        {"value": WORKTREE_BASELINE, "label": WORKTREE_BASELINE_LABEL}
    ]
    baseline_options.extend(
        {"value": branch_name, "label": branch_name}
        for branch_name in _collect_local_branch_names(repository_root)
    )
    return WorkspacePayload(
        status_code=200,
        payload={
            "repo_name": repository_root.name,
            "branch": _read_current_branch_name(repository_root),
            "baselines": baseline_options,
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
    untracked_paths = {
        candidate_path
        for candidate_path in _run_git(
            repository_root, "ls-files", "-z", "--others", "--exclude-standard"
        ).split("\0")
        if candidate_path and not _is_pruned_path(candidate_path)
    }
    return sorted(tracked_paths | untracked_paths)


def build_file_payload(repository_root: Path, requested_path: str) -> WorkspacePayload:
    """读取单个文件并按可渲染、二进制、超限三种形态给出应答。

    Args:
        repository_root (Path): 仓库根绝对路径。
        requested_path (str): 界面传来的仓库相对路径。

    Returns:
        WorkspacePayload: 正文应答（带行号渲染所需的逐行 HTML）或明确的形态标记。
    """
    resolved_path = resolve_repository_path(repository_root, requested_path)
    if resolved_path is None:
        return build_refusal_payload(
            403, "拒绝：该路径越出仓库范围，只读查看器不读取仓库外的文件。"
        )

    normalized_relative_path = Path(requested_path).as_posix() if requested_path else ""
    if resolved_path.is_dir():
        return build_refusal_payload(
            400, f"拒绝：{normalized_relative_path or '.'} 是一个目录，请选择一个文件。"
        )
    if not resolved_path.is_file():
        return build_refusal_payload(404, f"未找到文件：{normalized_relative_path}")

    file_byte_count = resolved_path.stat().st_size
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
    highlighted_source = highlight_source_lines(source_text, normalized_relative_path)
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
        },
    )


def build_changes_payload(repository_root: Path, baseline: str) -> WorkspacePayload:
    """给出某条基线下改动文件的集合与增删统计。

    Args:
        repository_root (Path): 仓库根绝对路径。
        baseline (str): ``worktree`` 或一条本地分支名。

    Returns:
        WorkspacePayload: 改动文件列表与合计；基线不被接受时为拒绝应答。
    """
    revision_spec = _build_change_revision_spec(repository_root, baseline)
    if revision_spec is None:
        return build_refusal_payload(
            400, f"拒绝：{baseline} 不是可用的比较基线，请选择「工作区改动」或一条本地分支。"
        )

    status_entry_by_path = _parse_status_entries(
        _run_git(repository_root, "diff", "--name-status", "-z", revision_spec)
    )
    numstat_by_path = _parse_numstat_entries(
        _run_git(repository_root, "diff", "--numstat", "-z", revision_spec)
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

    return WorkspacePayload(
        status_code=200,
        payload={
            "base": baseline,
            "base_label": _describe_baseline(baseline),
            "base_ref": revision_spec,
            "files": changed_files,
            "totals": {
                "files": len(changed_files),
                "add": sum(entry["add"] or 0 for entry in changed_files),
                "del": sum(entry["del"] or 0 for entry in changed_files),
            },
        },
    )


def build_diff_payload(
    repository_root: Path, requested_path: str, baseline: str
) -> WorkspacePayload:
    """给出单个文件在某条基线下的逐行改动。

    Args:
        repository_root (Path): 仓库根绝对路径。
        requested_path (str): 界面传来的仓库相对路径。
        baseline (str): ``worktree`` 或一条本地分支名。

    Returns:
        WorkspacePayload: 逐行 diff 应答；路径越界或基线不可用时为拒绝应答。正文含
        ``rename_from``：该文件是重命名而来时给出旧路径，否则为 ``None``。
    """
    resolved_path = resolve_repository_path(repository_root, requested_path)
    if resolved_path is None:
        return build_refusal_payload(
            403, "拒绝：该路径越出仓库范围，只读查看器不读取仓库外的文件。"
        )

    revision_spec = _build_change_revision_spec(repository_root, baseline)
    if revision_spec is None:
        return build_refusal_payload(
            400, f"拒绝：{baseline} 不是可用的比较基线，请选择「工作区改动」或一条本地分支。"
        )

    normalized_relative_path = Path(requested_path).as_posix()
    rename_source = _lookup_rename_source(repository_root, revision_spec, normalized_relative_path)
    # 重命名必须连旧路径一起作为 pathspec 交给 git，配对才成立；只给新路径会让同一个
    # 文件降级成「新增」，正文整篇算成新增行。
    diff_pathspecs = (
        [rename_source, normalized_relative_path] if rename_source else [normalized_relative_path]
    )
    diff_text = _run_git(repository_root, "diff", "-M", revision_spec, "--", *diff_pathspecs)
    diff_rows, is_truncated = _parse_unified_diff_rows(diff_text)
    return WorkspacePayload(
        status_code=200,
        payload={
            "path": normalized_relative_path,
            "base": baseline,
            "base_label": _describe_baseline(baseline),
            "base_ref": revision_spec,
            "rename_from": rename_source,
            "rows": diff_rows,
            "truncated": is_truncated,
            "empty": not diff_rows,
        },
    )


@dataclass(frozen=True)
class HighlightedSource:
    """文件正文的渲染结果。

    Attributes:
        rendered_lines (list[str]): 逐行 HTML；未高亮时是转义后的纯文本行。
        language_label (str): 语言标签，展示在内容区头部。
        is_highlighted (bool): 是否真的做了语法高亮。
    """

    rendered_lines: list[str]
    language_label: str
    is_highlighted: bool


@dataclass(frozen=True)
class _ResolvedSourceLexer:
    """按文件名解析出的词法器，附带展示给界面的语言标签。

    两个值总是一起出现：标签描述的是「用哪个词法器渲染的」，分开传会让调用方有机会
    拿词法器名字直接当标签用，而回退匹配时那个名字是错的。
    """

    lexer: object
    language_label: str


def highlight_source_lines(source_text: str, relative_path: str) -> HighlightedSource:
    """把源码渲染成逐行 HTML，可用时带语法高亮。

    Pygments 不保证 token span 在行边界闭合（多行字符串与注释会跨行），直接按换行
    切会把标签切坏，因此这里把整段源码渲染完再切行，并在每行末尾补上仍未闭合的
    ``</span>``、在下一行开头按栈里记录的 class 重新打开。

    Pygments 是显式声明的 dev 依赖，但这里仍按「缺失即降级」处理：派生项目做
    ``uv sync --no-dev`` 时高亮消失，查看器功能不缺失。

    Args:
        source_text (str): 已解码的文件正文。
        relative_path (str): 仓库相对路径，用于按文件名推断语言。

    Returns:
        HighlightedSource: 逐行 HTML 与语言标签。
    """
    try:
        from pygments import highlight as render_highlight
        from pygments.formatters import HtmlFormatter
    except ImportError:
        return _build_plain_text_source(source_text, "纯文本（未安装语法高亮依赖）")

    resolved_source = _resolve_lexer_for_relative_path(relative_path, source_text)
    if resolved_source is None:
        return _build_plain_text_source(source_text, "纯文本")

    highlighted_html = render_highlight(
        source_text, resolved_source.lexer, HtmlFormatter(nowrap=True)
    )
    return HighlightedSource(
        rendered_lines=_split_highlighted_lines(highlighted_html),
        language_label=resolved_source.language_label,
        is_highlighted=True,
    )


def _resolve_lexer_for_relative_path(
    relative_path: str, source_text: str
) -> _ResolvedSourceLexer | None:
    """按文件名解析词法器，认不出来时走显式的回退表。

    刻意不做基于内容的 ``guess_lexer``：那会让「这个文件渲染成什么语言」随正文内容
    漂移，排障时无法解释。

    Args:
        relative_path (str): 仓库相对路径。
        source_text (str): 已解码的文件正文，供 Pygments 消解同扩展名的歧义。

    Returns:
        _ResolvedSourceLexer | None: 词法器与展示标签；文件名与回退表都解析不出时为
            ``None``。
    """
    from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
    from pygments.util import ClassNotFound

    try:
        matched_lexer = get_lexer_for_filename(relative_path, source_text, stripnl=False)
    except ClassNotFound:
        fallback_lexer_alias, fallback_label = _FALLBACK_LEXERS_BY_FILENAME.get(
            Path(relative_path).name, (None, "")
        )
        if fallback_lexer_alias is None:
            return None
        try:
            matched_lexer = get_lexer_by_name(fallback_lexer_alias, stripnl=False)
        except ClassNotFound:
            return None
        return _ResolvedSourceLexer(lexer=matched_lexer, language_label=fallback_label)

    return _ResolvedSourceLexer(lexer=matched_lexer, language_label=matched_lexer.name)


def _build_plain_text_source(source_text: str, language_label: str) -> HighlightedSource:
    """无高亮时的降级渲染：转义后的纯文本行，行数与高亮路径保持一致。"""
    return HighlightedSource(
        rendered_lines=[
            _escape_source_line(source_line) for source_line in _split_source_lines(source_text)
        ],
        language_label=language_label,
        is_highlighted=False,
    )


def prewarm_highlighting() -> None:
    """在后台预热 Pygments 的导入与词法解析，使首屏不为这段导入付费。

    典型耗时 100–150ms，正好落在冷启动预算里；预热失败不影响功能，只是首个文件
    请求会自己付这段开销。
    """
    highlight_source_lines("prewarm = True\n", "view_prewarm.py")


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


def _split_source_lines(source_text: str) -> list[str]:
    """按 ``wc -l`` 语义切分正文，末尾换行不产生额外空行。"""
    source_lines = source_text.split("\n")
    if source_lines and source_lines[-1] == "":
        source_lines.pop()
    return source_lines


def _escape_source_line(source_line: str) -> str:
    """把一行源码转义成可直接放进 HTML 的纯文本。"""
    return html.escape(source_line, quote=True)


def _split_highlighted_lines(highlighted_html: str) -> list[str]:
    """把整段高亮 HTML 切成逐行 HTML，使每行自身标签平衡。

    Pygments 输出对换行敏感但不在行边界闭合 token span，因此逐行切分时要把跨行的
    span 在行尾闭合、在下一行行首按原 class 重开，行内既有标签的位置保持原样。

    Args:
        highlighted_html (str): ``HtmlFormatter(nowrap=True)`` 的整段输出。

    Returns:
        list[str]: 逐行 HTML，长度与 ``wc -l`` 语义一致。
    """
    rendered_lines: list[str] = []
    open_span_classes: list[str] = []
    for raw_html_line in highlighted_html.split("\n"):
        reopened_prefix = "".join(
            f'<span class="{span_class}">' for span_class in open_span_classes
        )
        scanned_parts: list[str] = []
        scan_cursor = 0
        for span_match in _SPAN_TAG_PATTERN.finditer(raw_html_line):
            scanned_parts.append(raw_html_line[scan_cursor : span_match.start()])
            scan_cursor = span_match.end()
            span_tag_text = span_match.group(0)
            if span_tag_text.startswith("</"):
                if open_span_classes:
                    open_span_classes.pop()
            else:
                class_match = _SPAN_CLASS_PATTERN.search(span_tag_text)
                open_span_classes.append(class_match.group(1) if class_match else "")
            scanned_parts.append(span_tag_text)
        scanned_parts.append(raw_html_line[scan_cursor:])
        closing_suffix = "</span>" * len(open_span_classes)
        rendered_lines.append(reopened_prefix + "".join(scanned_parts) + closing_suffix)

    if rendered_lines and rendered_lines[-1] == "":
        rendered_lines.pop()
    return rendered_lines


def _is_pruned_path(relative_path: str) -> bool:
    """判断路径是否位于文件树不展示的目录下。"""
    return any(
        path_segment in _PRUNED_DIRECTORY_NAMES for path_segment in relative_path.split("/")[:-1]
    )


def _collect_local_branch_names(repository_root: Path) -> list[str]:
    """列出本地分支名，作为改动视图的可选基线。"""
    branch_output = _run_git(
        repository_root, "for-each-ref", "--format=%(refname:short)", "refs/heads"
    )
    return sorted(branch_name for branch_name in branch_output.splitlines() if branch_name.strip())


def _read_current_branch_name(repository_root: Path) -> str:
    """读取当前检出的分支名；分离头指针时回退为短提交号。"""
    branch_output = _run_git(repository_root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    if branch_output and branch_output != "HEAD":
        return branch_output
    return _run_git(repository_root, "rev-parse", "--short", "HEAD").strip()


def _build_change_revision_spec(repository_root: Path, baseline: str) -> str | None:
    """把界面上的基线取值翻译成 ``git diff`` 的版本号参数。

    只接受「工作区」与本地分支两种取值：版本号会作为位置参数交给 ``git``，若放任
    任意字符串通过，``--output=...`` 这类以 ``-`` 开头的内容会被当成 git 选项解析。

    Args:
        repository_root (Path): 仓库根绝对路径。
        baseline (str): 界面上的基线取值。

    Returns:
        str | None: ``HEAD`` 或 ``<分支>...HEAD``；取值不可用时为 ``None``。
    """
    if baseline == WORKTREE_BASELINE:
        return "HEAD"
    if baseline in _collect_local_branch_names(repository_root):
        return f"{baseline}...HEAD"
    return None


def _describe_baseline(baseline: str) -> str:
    """给出基线的人类可读标签，与界面选择器的显示保持一致。"""
    return WORKTREE_BASELINE_LABEL if baseline == WORKTREE_BASELINE else baseline


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
    repository_root: Path, revision_spec: str, changed_path: str
) -> str | None:
    """查出 ``changed_path`` 是否由某条旧路径重命名而来，是则返回该旧路径。

    必须在**不带 pathspec 的完整 diff** 上查：``git diff <rev> -- <新路径>`` 把旧路径
    排除出候选，同一个文件会被降级成「新增」，查不到任何配对。

    Args:
        repository_root (Path): 仓库根绝对路径。
        revision_spec (str): 已校验的 ``git diff`` 版本号参数。
        changed_path (str): 仓库相对的新路径。

    Returns:
        str | None: 重命名来源的仓库相对路径；不是重命名时为 ``None``。
    """
    status_entry_by_path = _parse_status_entries(
        _run_git(repository_root, "diff", "--name-status", "-z", revision_spec)
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


def _parse_unified_diff_rows(diff_text: str) -> tuple[list[dict[str, object]], bool]:
    """把 unified diff 文本解析成带新旧行号的逐行结构。

    Args:
        diff_text (str): ``git diff`` 的原始输出。

    Returns:
        tuple[list[dict[str, object]], bool]: 逐行结构与是否因超出行数上限被截断。
    """
    diff_rows: list[dict[str, object]] = []
    old_line_number = 0
    new_line_number = 0
    is_truncated = False
    for diff_line in diff_text.splitlines():
        if len(diff_rows) >= MAX_DIFF_ROWS:
            is_truncated = True
            break
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
    return diff_rows, is_truncated


def _run_git(repository_root: Path, *git_arguments: str) -> str:
    """在仓库根执行一次只读 ``git`` 查询并返回标准输出。

    Args:
        repository_root (Path): 仓库根绝对路径。
        *git_arguments (str): 传给 ``git`` 的参数（不含 ``git`` 本身）。

    Returns:
        str: 命令的标准输出。

    Raises:
        WorkspaceReadError: ``git`` 非零退出。
    """
    completed_process = subprocess.run(
        ["git", "--no-pager", *git_arguments],
        cwd=repository_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed_process.returncode != 0:
        raise WorkspaceReadError(
            f"git {' '.join(git_arguments)} 执行失败：{completed_process.stderr.strip()}"
        )
    return completed_process.stdout
