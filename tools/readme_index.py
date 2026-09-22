#!/usr/bin/env python3
"""Regenerate the content index section of README.md.

Scans the tracked files under content/post/, reads the title from each
index.md front matter, and rewrites the block between the CONTENT-INDEX
markers in README.md.

Usage:
    python3 tools/readme_index.py            # rewrite README.md in place
    python3 tools/readme_index.py --check    # exit 1 if README.md is stale
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
POST_DIR = REPO / "content" / "post"
README = REPO / "README.md"

BEGIN = "<!-- BEGIN:CONTENT-INDEX -->"
END = "<!-- END:CONTENT-INDEX -->"

# Directories that hold assets rather than articles.
ASSET_DIRS = {"images", "image", "files"}

TITLE_RE = re.compile(r"^title:\s*(.+?)\s*$", re.MULTILINE)


def read_title(index_md: Path) -> str:
    """Return the front matter title, falling back to the folder name."""
    text = index_md.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            match = TITLE_RE.search(text[3:end])
            if match:
                return match.group(1).strip().strip("'\"")
    return index_md.parent.name


class Node:
    def __init__(self, name: str) -> None:
        self.name = name
        self.title: str | None = None  # set when this dir contains index.md
        self.children: dict[str, "Node"] = {}

    def child(self, name: str) -> "Node":
        return self.children.setdefault(name, Node(name))

    @property
    def post_count(self) -> int:
        return (1 if self.title else 0) + sum(
            c.post_count for c in self.children.values()
        )


def iter_index_files() -> list[Path]:
    """Return the tracked index.md files, i.e. the ones that will be committed.

    Walking the working tree instead would also pick up articles that are still
    untracked, so a locally regenerated index could mention a path that is
    absent from the commit, and CI — which recomputes the index from its own
    checkout — would then disagree with the committed README.
    """
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--", "content/post"],
            cwd=REPO,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"cannot list tracked files via git: {exc}", file=sys.stderr)
        raise SystemExit(1)
    # -z emits raw paths with no quoting, which keeps non-ASCII names intact.
    names = result.stdout.decode("utf-8").split("\0")
    # Plain "index.md" only: section metadata is "_index.md".
    return sorted(REPO / name for name in names if name.endswith("/index.md"))


def build_tree() -> Node:
    root = Node("")
    for index_md in iter_index_files():
        rel = index_md.parent.relative_to(POST_DIR)
        parts = [p for p in rel.parts if p not in ASSET_DIRS]
        if not parts:
            continue
        node = root
        for part in parts:
            node = node.child(part)
        node.title = read_title(index_md)
    return root


def link(node: Node, rel: Path) -> str:
    # Spaces would terminate a CommonMark link destination, so escape them.
    target = rel.as_posix().replace(" ", "%20")
    return f"[{node.title}](content/post/{target}/)"


def render_children(node: Node, rel: Path, indent: int, out: list[str]) -> None:
    """Render nested bullet lists for everything below a tag heading."""
    for name in sorted(node.children):
        child = node.children[name]
        child_rel = rel / name
        pad = " " * indent
        if child.title:
            out.append(f"{pad}- {link(child, child_rel)}")
        else:
            out.append(f"{pad}- {name}")
        render_children(child, child_rel, indent + 4, out)


def build_index() -> str:
    tree = build_tree()
    out: list[str] = []
    for name in sorted(tree.children):
        category = tree.children[name]
        rel = Path(name)
        out.append(f"## {name} ({category.post_count})")
        out.append("")
        names = [n for n in sorted(category.children)
                 if category.children[n].post_count]
        for i, child_name in enumerate(names):
            child = category.children[child_name]
            child_rel = rel / child_name
            if child.children:
                out.append(f"### {child_name}")
                out.append("")
                if child.title:
                    out.append(f"- {link(child, child_rel)}")
                render_children(child, child_rel, 0, out)
                out.append("")
            else:
                out.append(f"- {link(child, child_rel)}")
                # close the list when the next sibling is a heading or the
                # category ends
                nxt = category.children[names[i + 1]] if i + 1 < len(names) else None
                if nxt is None or nxt.children:
                    out.append("")
        while out and out[-1] == "":
            out.pop()
        out.append("")
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        current = README.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"{README} not found", file=sys.stderr)
        return 1

    if BEGIN not in current or END not in current:
        print(f"markers not found in {README}", file=sys.stderr)
        return 1

    index = build_index()
    updated = re.sub(
        re.escape(BEGIN) + r".*?" + re.escape(END),
        lambda _: f"{BEGIN}\n{index}\n{END}",
        current,
        count=1,
        flags=re.DOTALL,
    )

    if args.check:
        if updated != current:
            print("README.md content index is stale; run tools/readme_index.py")
            return 1
        print("README.md content index is up to date")
        return 0

    if updated != current:
        README.write_text(updated, encoding="utf-8")
        print("README.md updated")
    else:
        print("README.md already up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
