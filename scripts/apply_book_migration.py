#!/usr/bin/env python3
"""执行「分类=书、tag=章节」的全量迁移。

映射表的唯一事实源是 scripts/category_migration_map.py（RULES / OVERRIDES /
CH_REFS，运行前它自身的硬校验必须先通过）。本脚本按映射：

  1. git mv 文章目录  content/post/{旧}/{…}/{文章} → content/post/{书}/{章节}/{文章}
     （平铺书 → content/post/{书}/{文章}）
  2. 重写 front matter：categories = [书]，tags = [章节] + 保留的自由标签
     （平铺书 tags = 保留原样；5 处 front matter 与目录不一致的，以映射表为准顺带修正）
  3. 重写正文 relref 交叉引用的路径段（slug 引用不动；tags/RAG、tags/LangChain
     两个被引用的旧 tag 生成 alias 重定向，外链不断）
  4. 建新分类骨架 content/categories/{书}/_index.md（沿用 zata.py 的样式，
     封面图后补），删除全部旧分类/旧 tag 骨架和空目录，git rm 两个空文件

不动 slug / permalink（/p/:slug/）——文章 URL 全程零变更。
旧分类骨架先删后建：新分类 19 个里 5 个（Agent/DeepLearning/Design/
Engineering/Knowledge）与旧分类同名，骨架内容直接替换成新版。

用法：
    python3 scripts/apply_book_migration.py            # dry-run，只打印
    python3 scripts/apply_book_migration.py --apply    # 实际执行
    python3 scripts/apply_book_migration.py --apply --keep-old  # 保留旧分类/tag 骨架
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import category_migration_map as m

ROOT = m.ROOT  # content/post
CATS_DIR = "content/categories"
TAGS_DIR = "content/tags"

# 迁移后成为章节名、需要保留引用的旧 tag → 给它们的 term 页生成 alias
TAG_ALIASES = {"RAG": "/tags/rag-原理与实践/", "LangChain": "/tags/langchain-基础/"}


def git(*args, check=True):
    return subprocess.run(["git", *args], check=check, capture_output=True, text=True)


def is_clean(rel):
    """文章目录在 git 里没有待提交改动（staged/unstaged 都算）。"""
    r = git("status", "--porcelain", "--", os.path.join(ROOT, rel), check=False)
    return r.returncode == 0 and not r.stdout.strip()


def resolve_mapping():
    """复用映射脚本的 collect/read_article，返回 {rel: (book, chapter|None, title)}。

    前置条件：category_migration_map.py --stdout 校验通过（未映射/死规则直接退出）。
    """
    rels = m.collect()
    rows = {}
    for rel in rels:
        book = m.OVERRIDES.get(rel)
        if not book:
            parts = rel.split(os.sep)
            key = (parts[0], parts[1] if len(parts) >= 3 else None)
            book = m.RULES.get(key)
        if not book:
            print(f"未映射文章: {rel}", file=sys.stderr)
            sys.exit(1)
        title, _ = m.read_article(rel)
        rows[rel] = [book, None, title]

    # 章节解析（与映射脚本同一套规则：tag: 整组引用 + 单篇路径引用）
    by_book = {}
    for rel, (book, _, _) in rows.items():
        by_book.setdefault(book, []).append(rel)
    for book, chapters in m.CHAPTERS.items():
        if not chapters:
            continue
        book_rels = by_book.get(book, [])
        seen = {}
        for ch in chapters:
            for ref in m.CH_REFS.get(book, {}).get(ch, []):
                if ref.startswith("tag:"):
                    cat, tag = ref[4:].split("/", 1)
                    hits = [r for r in book_rels
                            if r.split(os.sep)[0] == cat
                            and len(r.split(os.sep)) >= 3
                            and r.split(os.sep)[1] == tag]
                else:
                    hits = [ref] if ref in book_rels else []
                for h in hits:
                    if h in seen:
                        print(f"{h} 被分到多个章节", file=sys.stderr)
                        sys.exit(1)
                    seen[h] = ch
                    rows[h][1] = ch
        for rel in book_rels:
            if rel not in seen:
                print(f"{book}：未分章节：{rel}", file=sys.stderr)
                sys.exit(1)
    return rows


def plan_moves(mapping):
    """返回 {rel: (src_dir, dst_dir)}。dst 的章节目录名加序号前缀。"""
    moves = {}
    for rel, (book, ch, _) in sorted(mapping.items()):
        src = os.path.join(ROOT, rel)
        art = rel.split(os.sep)[-1]
        if ch:
            idx = m.CHAPTERS[book].index(ch) + 1
            dst = os.path.join(ROOT, book, f"{idx:02d}-{ch}", art)
        else:
            dst = os.path.join(ROOT, book, art)
        moves[rel] = (src, dst)
    return moves


def rewrite_front_matter(path, book, chapter):
    """重写 categories/tags。返回 (是否改动, 旧tags, 新tags)。"""
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---"):
        print(f"  !! 无 front matter，跳过：{path}", file=sys.stderr)
        return False, [], []
    parts = text.split("---", 2)
    if len(parts) < 3:
        return False, [], []
    head, fm, body = parts

    def block(key):
        # 只认「纯列表行」的块；行内带 # 注释的块结构复杂，跳过由用户手工处理
        mm = re.search(rf"^{key}:[ \t]*\n((?:(?![ \t]*#)[ \t]*-[ \t]*.*\n)+)", fm, re.M)
        if not mm:
            return None, []
        vals = [ln.split("-", 1)[1].strip().strip('"').strip("'")
                for ln in mm.group(1).splitlines() if "-" in ln]
        return mm, vals

    cat_m, _ = block("categories")
    tag_m, old_tags = block("tags")
    if cat_m is None and re.search(r"^categories:", fm, re.M):
        print(f"  !! categories 块含注释行，跳过（需手工处理）：{path}", file=sys.stderr)
        return False, [], []
    if tag_m is None and re.search(r"^tags:", fm, re.M):
        print(f"  !! tags 块含注释行，跳过（需手工处理）：{path}", file=sys.stderr)
        return False, [], []

    new_fm = fm
    cat_lines = f"categories:\n    - {book}\n"
    if cat_m:
        new_fm = new_fm[:cat_m.start()] + cat_lines + new_fm[cat_m.end():]
    elif re.search(r"^categories:", new_fm, re.M):
        # 有 categories 字段但块匹配失败（注释行），前面已告警跳过；这里兜底不追加
        pass
    else:
        new_fm += cat_lines

    if chapter is None:
        new_tags = old_tags  # 平铺书保留原 tags
    else:
        keep = [t for t in old_tags if t and t != chapter]
        new_tags = [chapter] + keep
    tag_lines = "tags:\n" + "".join(f"    - {t}\n" for t in new_tags)
    if tag_m:
        # categories 块可能已改，重新定位 tags
        tag_m2, _ = re.search(r"^tags:\s*\n((?:(?![ \t]*#)[ \t]*-[ \t]*.*\n)+)", new_fm, re.M), None
        new_fm = new_fm[:tag_m2.start()] + tag_lines + new_fm[tag_m2.end():]
    elif re.search(r"^tags:", new_fm, re.M):
        pass  # 同上兜底
    else:
        new_fm += tag_lines

    if new_fm == fm:
        return False, old_tags, new_tags
    with open(path, "w", encoding="utf-8") as f:
        f.write(head + "---" + new_fm + "---" + body)
    return True, old_tags, new_tags


def rewrite_relrefs(moves, apply, quiet=False):
    """把正文 relref 里的旧路径换成新路径。返回替换次数。

    目标分两类：旧路径（迁移后 404，必须换）；已是新路径（文章提前用目标路径
    互链，迁移后自然复活，只提示不动）。"""
    # 旧 rel 路径 → 新 rel 路径（相对 content/post）
    remap = {}
    for rel, (_, dst) in moves.items():
        remap[rel] = os.path.relpath(dst, ROOT)
    valid_new = set(remap.values())
    n = 0
    targets = []
    for dp, _, files in os.walk(ROOT):
        if "index.md" in files:
            targets.append(os.path.join(dp, "index.md"))
    pat = re.compile(r'(relref\s+["\']/?post/)([^"\']+?)(/index\.md["\'])')
    for path in targets:
        text = open(path, encoding="utf-8").read()
        def sub(mm):
            nonlocal n
            old = mm.group(2)
            new = remap.get(old)
            if not new:
                if old in valid_new:
                    if not quiet:
                        print(f"  提示：已是新路径（迁移后生效）：{old}（{path}）", file=sys.stderr)
                else:
                    print(f"  !! relref 目标不在迁移表：{old}（{path}）", file=sys.stderr)
                return mm.group(0)
            n += 1
            return mm.group(1) + new + mm.group(3)
        out = pat.sub(sub, text)
        if apply and out != text:
            open(path, "w", encoding="utf-8").write(out)
    return n


def write_category_skeleton(name):
    d = os.path.join(CATS_DIR, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "_index.md"), "w", encoding="utf-8") as f:
        f.write(f"""---
title: "{name}"
description: "《{name}》：分类即书，连续阅读。"
slug: "{name}"
style:
    background: "#238377"
    color: "#fff"
---
""")


def write_tag_alias(tag, alias):
    d = os.path.join(TAGS_DIR, tag)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "_index.md"), "w", encoding="utf-8") as f:
        f.write(f"""---
title: "{tag}"
slug: "{tag}"
aliases:
    - {alias}
---
""")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--keep-old", action="store_true", help="保留旧分类/旧 tag 骨架目录")
    args = ap.parse_args()

    mapping = resolve_mapping()
    moves = plan_moves(mapping)
    print(f"映射解析完成：{len(moves)} 篇\n")

    dirty = [rel for rel in moves if not is_clean(rel)]
    print(f"工作区有未提交改动的文章目录：{len(dirty)} 个"
          + ("（git mv 会失败，请先提交或 stash）" if dirty and args.apply else "（dry-run 不受影响）"))
    for rel in dirty:
        print(f"  {rel}")
    print()

    # ---- 1. 目录移动 ----
    print("== 目录移动 ==")
    for rel, (src, dst) in sorted(moves.items()):
        print(f"  {rel}  ->  {os.path.relpath(dst, ROOT)}")
        if args.apply:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            git("mv", src, dst)

    # ---- 2. front matter ----
    print("\n== front matter（categories/tags）==")
    changed = 0
    for rel, (book, ch, _) in sorted(mapping.items()):
        path = os.path.join(moves[rel][1] if args.apply else moves[rel][0], "index.md")
        if args.apply:
            ok, old, new = rewrite_front_matter(path, book, ch)
            if ok:
                changed += 1
        else:
            keep = "" if ch is None else f"  tags: 章节「{ch}」+ 保留自由标签"
            print(f"  {rel}  ->  categories: [{book}]{keep}")
    print(f"  （{'已改写' if args.apply else 'dry-run'}，apply 时统计改写数）" if not args.apply
          else f"  实际改写 {changed} 篇")

    # ---- 3. relref ----
    print("\n== relref 交叉引用 ==")
    n = rewrite_relrefs(moves, args.apply, quiet=args.apply)
    print(f"  {n} 处路径替换（{'已写入' if args.apply else 'dry-run'}）")

    # ---- 4. 分类/tag 骨架 ----
    print("\n== 分类/tag 骨架 ==")
    if args.apply:
        if not args.keep_old:
            for d in (CATS_DIR, TAGS_DIR):
                for name in os.listdir(d):
                    p = os.path.join(d, name)
                    if os.path.isdir(p) and not name.startswith("."):
                        shutil.rmtree(p)
                        print(f"  删除旧骨架 {p}")
        for name in m.BOOK_ORDER:
            write_category_skeleton(name)
        print(f"  新建 {len(m.BOOK_ORDER)} 个分类骨架（封面图后补）")
        for tag, alias in TAG_ALIASES.items():
            write_tag_alias(tag, alias)
        print(f"  新建 {len(TAG_ALIASES)} 个 tag alias 页（旧 tag 外链重定向）")
    else:
        old_cats = [d for d in os.listdir(CATS_DIR) if os.path.isdir(os.path.join(CATS_DIR, d))]
        old_tags = [d for d in os.listdir(TAGS_DIR) if os.path.isdir(os.path.join(TAGS_DIR, d))]
        print(f"  将删除旧分类骨架 {len(old_cats)} 个：{old_cats}")
        print(f"  将删除旧 tag 骨架 {len(old_tags)} 个：{old_tags}")
        print(f"  将新建分类骨架 {len(m.BOOK_ORDER)} 个 + tag alias {len(TAG_ALIASES)} 个"
              + ("（--keep-old 可保留旧骨架）" if not args.keep_old else ""))

    # ---- 5. 空文件/空目录 ----
    print("\n== 空文件与空目录 ==")
    empties = []
    for dp, dns, fns in os.walk(ROOT):
        for fn in fns:
            p = os.path.join(dp, fn)
            if fn == "index.md" and os.path.getsize(p) == 0:
                empties.append(p)
    for p in empties:
        print(f"  git rm 空文件 {p}")
        if args.apply:
            git("rm", "-q", p)
    for dp, dns, fns in os.walk(ROOT, topdown=False):
        if not os.listdir(dp):
            print(f"  删除空目录 {dp}")
            if args.apply:
                os.rmdir(dp)

    print(f"\n{'APPLY 完成' if args.apply else 'DRY-RUN（未改动任何文件）'}"
          f"：{len(moves)} 篇 / {len(m.BOOK_ORDER)} 本 / "
          f"{sum(len(v) for v in m.CHAPTERS.values())} 章")


if __name__ == "__main__":
    main()
