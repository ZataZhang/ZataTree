"""按 **git 版本** 读取仓库内容：对象库里的字节与大小。

改动视图对「有旧新两版可比」的文件（尤其是图片）要在同一页里给出两侧，而工作区里只存在
新侧——旧侧只存在于 git 的对象库与索引里。本模块只负责这一件事：把「哪一侧」这个**封闭
枚举**映射成具体的 git 表达式，回答「这一侧有没有这个文件、多大」，并按需把字节读出来。

只读是硬边界：这里只有 ``cat-file`` 查询，不写对象、不动索引，也不碰工作区。

两侧的取值从不来自调用方传入的字符串：调用方按改动分区选 :data:`HEAD_REVISION` 或
:data:`INDEX_REVISION`，映射表在模块里。路径则拼进 ``<rev>:<path>`` 这**一个** argv 元素，
因此以 ``-`` 开头、含空格或中文的路径都不会被 git 当成选项。
"""

from __future__ import annotations

import posixpath
import subprocess
from pathlib import Path

#: 改动视图的「旧侧」基准：已提交的 HEAD。
HEAD_REVISION = "head"

#: 索引（stage 0）——已暂存的内容。它既是「已暂存」分区的新侧，也是「未暂存」分区的旧侧。
INDEX_REVISION = "index"

#: 认可的版本取值。封闭枚举：不在表里的取值一律拒绝，绝不作为参数流进 git。
KNOWN_REVISIONS = frozenset({HEAD_REVISION, INDEX_REVISION})

#: 版本取值 → ``<rev>:<path>`` 里的版本前缀。``:0`` 是 stage 0 的索引写法。
_GIT_REVISION_PREFIX_BY_REVISION: dict[str, str] = {
    HEAD_REVISION: "HEAD",
    INDEX_REVISION: ":0",
}

#: ``cat-file -t`` 报告的对象类型；只有它算「这个版本里有这个文件」。
_BLOB_OBJECT_TYPE = b"blob"


def is_known_revision(revision_name: str) -> bool:
    """判断版本取值是否在封闭枚举内。

    Args:
        revision_name (str): 界面传来的版本取值。

    Returns:
        bool: 是否是可用取值。
    """
    return revision_name in KNOWN_REVISIONS


def read_blob_size(repository_root: Path, revision_name: str, relative_path: str) -> int | None:
    """给出某个版本里该文件的大小，顺带回答它到底在不在。

    先取对象类型再取大小：``cat-file -s`` 对**目录**同样返回 0 并打印 tree 对象的大小，
    只看大小会把一个目录说成「这个版本里有这个文件」，界面上随之出现一张取不到字节的破图。

    Args:
        repository_root (Path): 仓库根绝对路径。
        revision_name (str): :data:`KNOWN_REVISIONS` 里的取值。
        relative_path (str): 仓库相对路径。

    Returns:
        int | None: 字节数；该版本里没有这个文件、或它不是普通文件（blob）时为 ``None``。
    """
    git_expression = _build_git_expression(revision_name, relative_path)
    object_type_result = _run_cat_file(repository_root, git_expression, "-t")
    if object_type_result.returncode != 0:
        return None
    if object_type_result.stdout.strip() != _BLOB_OBJECT_TYPE:
        return None

    size_result = _run_cat_file(repository_root, git_expression, "-s")
    if size_result.returncode != 0:
        return None
    return int(size_result.stdout.strip())


def read_blob_bytes(repository_root: Path, revision_name: str, relative_path: str) -> bytes | None:
    """读出某个版本里该文件的原始字节。

    ``cat-file blob`` 对目录直接失败（``bad file``），因此这里不必再判一次类型。

    Args:
        repository_root (Path): 仓库根绝对路径。
        revision_name (str): :data:`KNOWN_REVISIONS` 里的取值。
        relative_path (str): 仓库相对路径。

    Returns:
        bytes | None: 原始字节；该版本里没有这个文件、或它不是普通文件时为 ``None``。
    """
    blob_result = _run_cat_file(
        repository_root, _build_git_expression(revision_name, relative_path), "blob"
    )
    if blob_result.returncode != 0:
        return None
    return blob_result.stdout


def _build_git_expression(revision_name: str, relative_path: str) -> str:
    """拼出 ``<rev>:<path>`` 形式的单个 git 表达式。

    路径先做词法归一化：``<rev>:<path>`` 里的路径 git **不做** ``..`` 归一化，实测
    ``HEAD:a/../b`` 会直接报「path 'a/../b' exists on disk, but not in 'HEAD'」。越出
    仓库的那种 ``..`` 在解析阶段已被拒绝，因此归一化后不可能以 ``..`` 开头。

    这里刻意不用「解析后的绝对路径」来反推 git 路径：工作区里的符号链接在 git 里存的是
    链接本身，反推出来的目标路径会读错对象。

    Args:
        revision_name (str): :data:`KNOWN_REVISIONS` 里的取值。
        relative_path (str): 仓库相对路径。

    Returns:
        str: 形如 ``HEAD:docs/x.png`` / ``:0:docs/x.png`` 的表达式。
    """
    return f"{_GIT_REVISION_PREFIX_BY_REVISION[revision_name]}:{posixpath.normpath(relative_path)}"


def _run_cat_file(
    repository_root: Path, git_expression: str, *cat_file_arguments: str
) -> subprocess.CompletedProcess[bytes]:
    """执行一次 ``git cat-file`` 并按字节返回结果。

    刻意不复用 :mod:`workspace` 里那个文本模式的 ``_run_git``：那条路径把「非零退出」当
    失败抛错，而这里「这个版本里没有这个文件」是**正常答案**之一，要按退出码分流；对象
    字节也不是文本，不能解码。两者语义不同，硬合并只会让两边都变含糊。

    Args:
        repository_root (Path): 仓库根绝对路径。
        git_expression (str): :func:`_build_git_expression` 产出的表达式。
        *cat_file_arguments (str): 传给 ``cat-file`` 的选项，如 ``"-t"`` / ``"-s"`` / ``"blob"``。

    Returns:
        subprocess.CompletedProcess[bytes]: 完成结果；退出码由调用方判定。
    """
    return subprocess.run(
        ["git", "--no-pager", "cat-file", *cat_file_arguments, git_expression],
        cwd=repository_root,
        capture_output=True,
        check=False,
    )
