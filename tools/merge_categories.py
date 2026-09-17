#!/usr/bin/env python3
"""把文章 frontmatter 里的重复/杂散分类合并到规范分类。

只改 frontmatter，不移动文件 —— 站点 permalinks 是 post: /p/:slug/，
URL 由 slug 决定，所以改分类不会动到任何已有链接。

用法：
    python3 tools/merge_categories.py          # dry-run，只打印
    python3 tools/merge_categories.py --apply  # 实际写入
"""
import argparse
import os
import re
import sys

ROOT = "content/post"

# 规范分类 = content/post 下的目录名
CANONICAL = {
    "Agent", "Book", "Design", "DeepLearning", "Engineering", "Grammar",
    "Knowledge", "Library", "PaperReading", "Platforms_Tools",
    "Project_Application", "Vibe-Coding",
}

# 旧分类 → 规范分类。None 表示直接丢弃（它不是一个分类）
MERGE = {
    "Project&Application": "Project_Application",
    "Platforms&Tools": "Platforms_Tools",
    "library": "Library",
    "Python-Library": "Library",
    "python": "Library",
    "DeepLearing": "DeepLearning",
    "LLM": "DeepLearning",
    "Study": "Project_Application",
    "web": "Platforms_Tools",
    "Chart": "Design",
    "前端架构": "Library",
    "others": None,
    "": None,
}

BLOCK = re.compile(r"^(categories:\s*\n)((?:(?:[ \t]*#.*|[ \t]*-[ \t]*.*)?\n)+)", re.M)


def parse_block(block):
    """返回 (注释行, 分类列表)"""
    comments, cats = [], []
    for line in block.splitlines():
        s = line.strip()
        if s.startswith("#"):
            comments.append(line)
            continue
        m = re.match(r"[ \t]*-[ \t]*(.*)$", line)
        if m:
            val = m.group(1).strip().strip('"').strip("'")
            cats.append(val)
    return comments, cats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    changed = []
    unchanged = 0

    for dp, _, files in os.walk(ROOT):
        if "index.md" not in files:
            continue
        path = os.path.join(dp, "index.md")
        text = open(path, encoding="utf-8").read()
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        head, fm, body = parts

        m = BLOCK.search(fm)
        if not m:
            continue
        comments, cats = parse_block(m.group(2))

        out, seen = [], set()
        for c in cats:
            target = MERGE.get(c, c)
            if target is None:
                continue
            if target not in CANONICAL:
                # 没在映射表里也不是规范分类 —— 报出来，别偷偷改
                print(f"  !! 未处理分类 {c!r} 于 {path}", file=sys.stderr)
                target = c
            if target in seen:
                continue
            seen.add(target)
            out.append(target)

        if not out:
            print(f"  !! 合并后没有分类了，跳过：{path}", file=sys.stderr)
            continue

        if out == cats:
            unchanged += 1
            continue

        new_block = "categories:\n" + "".join(
            l + "\n" for l in comments
        ) + "".join(f"    - {c}\n" for c in out)
        new_fm = fm[:m.start()] + new_block + fm[m.end():]
        changed.append((path, cats, out))
        if args.apply:
            with open(path, "w", encoding="utf-8") as f:
                f.write(head + "---" + new_fm + "---" + body)

    print(f"\n{'已写入' if args.apply else 'DRY-RUN'}：{len(changed)} 篇需要改，{unchanged} 篇已合规\n")
    for path, old, new in sorted(changed):
        print(f"  {path.replace(ROOT + '/', '')}")
        print(f"      {old}  ->  {new}")


if __name__ == "__main__":
    main()
