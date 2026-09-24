"""把正文渲染成界面能直接铺的行级 HTML：语法高亮与 Markdown 预览。

这里只做「正文 → HTML」这一件事，不碰文件系统、不调 ``git``：输入是已解码的字符串，
输出是逐行 HTML 或整段 HTML 片段。读文件、判二进制、按后缀决定用哪种渲染都在
:mod:`workspace` 里，所以本模块可以被单独测、也可以被换掉。

Markdown 渲染完之后还会过一道 :func:`rebase_relative_references`：正文里的相对引用在
浏览器眼里是相对**查看器页面**（``/``）的，得改写成能真正取到字节的地址；至于那个地址长
什么样（``/raw/`` 还是查看器的直达链接）由调用方给的回调决定，本模块不认识任何路由。

两个渲染器都按「缺失即降级」处理显式声明的 dev 依赖（``pygments`` / ``markdown``）：派生
项目做 ``uv sync --no-dev`` 时高亮与预览消失，查看器其余功能不缺失。import 必须留在函数
里——``launch.py`` 的 import 闭包只能含标准库加同目录兄弟模块（见
``tests/guards/shared/test_view_launch_entry.py``），提到模块顶层会让 ``just view`` 在
``-S`` 下直接起不来。
"""

from __future__ import annotations

import html
import posixpath
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

#: Markdown 预览启用的扩展：围栏代码、表格、以及列表缩进不按 4 空格误判为代码块。
#: 刻意不启用 ``codehilite``——那会引入第二套 Pygments 产出，与 :func:`highlight_source_lines`
#: 的行级高亮 CSS 抢同一批短类名。
_MARKDOWN_EXTENSIONS = ("fenced_code", "tables", "sane_lists")

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

_SPAN_TAG_PATTERN = re.compile(r"</?span[^>]*>")
_SPAN_CLASS_PATTERN = re.compile(r'class="([^"]*)"')

#: 标签级扫描：先切出一个标签本身，再只在标签文本内部改属性。正文内容（包括作者原样写的
#: ``src="…"`` 说明文字）与代码块因此天然在视野之外——markdown 会把代码里的引号转义成
#: ``&quot;``，属性正则也就匹配不到那里。引号里的 ``>`` 不会把标签提前截断。
_MARKUP_TAG_PATTERN = re.compile(r"<[a-zA-Z][a-zA-Z0-9-]*(?:[^>\"']|\"[^\"]*\"|'[^']*')*>")

#: 标签里要改写的属性：``src`` 与 ``href``。只认带引号的取值——不带引号的裸值在 markdown
#: 产出里不出现，真遇到了留着原样比猜边界强。
_REFERENCE_ATTRIBUTE_PATTERN = re.compile(r"(\b(src|href)\s*=\s*)(?:\"([^\"]*)\"|'([^']*)')")

#: 带 scheme 的引用（``http:`` / ``https:`` / ``data:`` / ``mailto:`` …）不是仓库里的文件，
#: 一个都不重写。
_ABSOLUTE_REFERENCE_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")

#: ``fenced_code`` 为 mermaid 围栏产出的确切形态。`class` 取值由 python-markdown 的
#: ``lang_prefix`` 决定（默认 ``language-``），这里跟着默认值走——改前缀要一起改。
_MERMAID_FENCE_PATTERN = re.compile(
    r'<pre><code class="language-mermaid">(?P<source>.*?)</code></pre>', re.DOTALL
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


def render_markdown_document(source_text: str) -> str | None:
    """把 Markdown 正文渲染成 HTML 片段。

    ``markdown`` 按 :func:`highlight_source_lines` 里 pygments 同一条口径处理：显式声明
    的 dev 依赖，但缺失即降级——派生项目做 ``uv sync --no-dev`` 时预览入口不出现，源码
    高亮照旧。

    正文里的 raw HTML 不做清洗。查看器绑在回环上、只有读与暂存两种能力，预览又是用户主动
    点开的一次；这里刻意不做清洗——清洗过的结果已经不是文件本身。

    mermaid 围栏会改成 :func:`_turn_mermaid_fences_into_diagram_blocks` 认得的形态，图
    由浏览器的 mermaid.js 画；服务端不认识 mermaid，也就没有语法可校验。

    Args:
        source_text (str): 已解码的 Markdown 正文。

    Returns:
        str | None: 渲染后的 HTML 片段；依赖缺失时为 ``None``。
    """
    try:
        import markdown
    except ImportError:
        return None
    return _turn_mermaid_fences_into_diagram_blocks(
        markdown.markdown(source_text, extensions=list(_MARKDOWN_EXTENSIONS))
    )


def _turn_mermaid_fences_into_diagram_blocks(rendered_html: str) -> str:
    """把 mermaid 围栏换成 ``<pre class="mermaid">``，交给页面里的 mermaid.js 去画。

    刻意不做成 python-markdown 的 treeprocessor：``fenced_code`` 造出的 ``pre``/``code``
    在 preprocessor 阶段就进了 ``htmlStash``，treeprocessor 根本看不到那棵子树。这里改成
    在渲染完成的片段上做一次定点替换，只认 ``fenced_code`` 自己产出的那个确切形态——代码块
    正文已被转义，里面不可能出现 ``</code></pre>``，因此非贪婪匹配必定停在该围栏的结尾。

    围栏正文**原样留在 ``<pre>`` 里**（仍是转义后的文本）：mermaid 读的是 ``textContent``，
    ``&gt;`` 在浏览器里解回来还是 ``>``。页面拿不到 mermaid、或图本身渲染失败时，留在那里的
    就是一个普通代码块——降级方向与其它预览一致。

    Args:
        rendered_html (str): :func:`render_markdown_document` 里 python-markdown 的产出。

    Returns:
        str: 围栏已替换的 HTML 片段。
    """
    return _MERMAID_FENCE_PATTERN.sub(
        lambda fence_match: f'<pre class="mermaid">{fence_match.group("source")}</pre>',
        rendered_html,
    )


def rebase_relative_references(
    html_fragment: str,
    base_directory: str,
    build_reference_url: Callable[[str, str], str],
) -> str:
    """把 HTML 片段里的相对引用改写成调用方给的可取用地址。

    markdown 渲染出来的 ``<img src="images/a.png">`` 是相对**文档所在目录**写的，但预览片段
    是内联进查看器页面（``/``）的，浏览器于是按页面根解析成 ``/images/a.png``——那上面没有
    仓库文件，图片必然加载失败。这里把每个相对引用先解析成仓库相对路径，再交给调用方拼成真
    正能取到字节的地址。

    只改标签里的 ``src`` / ``href`` 属性，不动正文文本、不动代码块（见模块级
    :data:`_MARKUP_TAG_PATTERN` 的说明）。markdown 语法写的图片与链接、以及正文里手写的
    raw HTML 标签，走的都是这一条路。扫描只看「像不像一个标签」，因此 raw HTML 块里
    ``<script>`` 字符串中写着标签形状的内容也会被改写——预览里的 raw HTML 本来就会被执行，
    这一档按同一口径接受。

    以下引用一律**原样保留**，因为猜错比不改更糟：

    - 带 scheme 的（``https:`` / ``data:`` / ``mailto:`` …）、协议相对的（``//host/…``）、
      纯片段（``#anchor``）——它们本来就不是仓库里的文件；
    - 带查询串的——``/raw/`` 的 ``?rev=`` 与查看器直达链接的 ``?path=`` 语义完全不同，把查询串
      原样接在任一种地址后面都会得到一个含义不同的地址；
    - 解析之后跑出仓库根的（``../../x`` 回到仓库之外）或解析结果为空的。

    前导 ``/`` 按**仓库根相对**解释：查看器的 ``/`` 上没有仓库文件，而 ``/assets/`` 正好是
    查看器自己的静态资源目录，照着页面根解析只会拿到错的字节或 404。

    Args:
        html_fragment (str): 待改写的 HTML 片段。
        base_directory (str): 片段所属文档所在目录的仓库相对路径（POSIX 分隔符）；
            文档在仓库根时为空串。
        build_reference_url (Callable[[str, str], str]): 把「属性名 + 仓库相对路径」拼成最终
            地址的回调。属性名会原样传入，因为 ``src`` 与 ``href`` 的去向本来就不一样。

    Returns:
        str: 改写后的片段。
    """

    def rewrite_tag(markup_tag: str) -> str:
        return _REFERENCE_ATTRIBUTE_PATTERN.sub(
            lambda attribute_match: _rewrite_reference_attribute(
                attribute_match, base_directory, build_reference_url
            ),
            markup_tag,
        )

    return _MARKUP_TAG_PATTERN.sub(lambda tag_match: rewrite_tag(tag_match.group(0)), html_fragment)


def prewarm_highlighting() -> None:
    """在后台预热 Pygments 的导入与词法解析，使首屏不为这段导入付费。

    典型耗时 100–150ms，正好落在冷启动预算里；预热失败不影响功能，只是首个文件
    请求会自己付这段开销。
    """
    highlight_source_lines("prewarm = True\n", "view_prewarm.py")


def _rewrite_reference_attribute(
    attribute_match: re.Match[str],
    base_directory: str,
    build_reference_url: Callable[[str, str], str],
) -> str:
    """改写一个 ``src`` / ``href`` 属性的取值，改不动时原样返回。

    Args:
        attribute_match (re.Match[str]): :data:`_REFERENCE_ATTRIBUTE_PATTERN` 的一处匹配。
        base_directory (str): 片段所属文档所在目录的仓库相对路径。
        build_reference_url (Callable[[str, str], str]): 「属性名 + 仓库相对路径 → 地址」的回调。

    Returns:
        str: 改写后的属性文本；该引用不该重写时是匹配到的原文。
    """
    quote_character = '"' if attribute_match.group(3) is not None else "'"
    raw_reference = (
        attribute_match.group(3)
        if attribute_match.group(3) is not None
        else attribute_match.group(4)
    )
    resolved_reference = _resolve_relative_reference(raw_reference, base_directory)
    if resolved_reference is None:
        return attribute_match.group(0)
    resolved_path, reference_fragment = resolved_reference
    reference_url = build_reference_url(attribute_match.group(2), resolved_path)
    return (
        f"{attribute_match.group(1)}"
        f"{quote_character}{reference_url}{reference_fragment}{quote_character}"
    )


def _resolve_relative_reference(
    reference_value: str, base_directory: str
) -> tuple[str, str] | None:
    """把一个引用取值解析成「仓库相对路径 + 尾随片段」。

    Args:
        reference_value (str): 属性里原样的取值（可能含 HTML 实体转义）。
        base_directory (str): 片段所属文档所在目录的仓库相对路径。

    Returns:
        tuple[str, str] | None: 仓库相对路径与 ``#`` 之后的片段（没有片段时为空串）；
            该引用不该被重写时为 ``None``。
    """
    # 属性里的 `&` 在 markdown 产出里是 `&amp;`，按实体解回来再交给回调逐段编码，
    # 否则 `&` 与 `;` 会被编码进文件名里，变成一个取不到字节的地址。
    candidate = html.unescape(reference_value).strip()
    if not candidate or "?" in candidate:
        return None
    if candidate.startswith(("#", "//")) or _ABSOLUTE_REFERENCE_PATTERN.match(candidate):
        return None

    reference_path, separator, reference_fragment = candidate.partition("#")
    if not reference_path:
        return None
    if reference_path.startswith("/"):
        resolved_path = posixpath.normpath(reference_path.lstrip("/"))
    else:
        resolved_path = posixpath.normpath(posixpath.join(base_directory, reference_path))
    # 跑出仓库根的引用不重写：那种地址在 `/raw/` 上只会被越界断言拒掉，而查看器也没有
    # 「仓库之外」这一层可供跳转。
    if resolved_path in (".", "..", "") or resolved_path.startswith("../"):
        return None
    return resolved_path, f"{separator}{reference_fragment}" if separator else ""


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
