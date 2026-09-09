#!/usr/bin/env python3
"""Generate 1200x400 cover SVGs for ZataTree articles.

Usage:
  python3 tools/cover.py                # regenerate every index.svg cover
  python3 tools/cover.py path/to/index.md [more/index.md ...]
"""

import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
CANVAS_W, CANVAS_H = 1200, 400
TEXT_ZONE_W = 640          # title must fit inside x in [96, 736]
TITLE_X = 96
MOTIF_X = 760

CATEGORY_STYLE = {
    "Agent":             ("#7C9CF5", "#A78BFA", "graph"),
    "Engineering":       ("#5B87BF", "#22D3EE", "terminal"),
    "DeepLearning":      ("#8B5CF6", "#22D3EE", "chip"),
    "Vibe-Coding":       ("#60A5FA", "#34D399", "flow"),
    "Platforms_Tools":   ("#5B87BF", "#8B5CF6", "layers"),
    "Library":           ("#38BDF8", "#5EEAD4", "doc"),
    "Design":            ("#A78BFA", "#5EEAD4", "layers"),
    "Knowledge":         ("#94A3B8", "#22D3EE", "doc"),
    "Grammar":           ("#5EEAD4", "#60A5FA", "terminal"),
    "PaperReading":      ("#F472B6", "#818CF8", "doc"),
}
DEFAULT_STYLE = ("#5B87BF", "#22D3EE", "flow")


def parse_frontmatter(text):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not match:
        return {}
    meta, current = {}, None
    for raw in match.group(1).splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line[0] in " \t-" and current:
            meta.setdefault(current, []).append(line.lstrip(" \t-").strip().strip("'\""))
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value:
            meta[key] = value.strip("'\"")
            current = None
        else:
            meta.setdefault(key, [])
            current = key
    return meta


def char_width(ch, size):
    if ord(ch) > 0x2E7F:            # CJK and fullwidth punctuation
        return size
    if ch == " ":
        return size * 0.34
    return size * 0.56              # latin, digits, punctuation


def text_width(s, size):
    return sum(char_width(c, size) for c in s)


def split_balanced(title):
    cut = None
    target = len(title) / 2
    best = None
    for i, ch in enumerate(title):
        if ch in " ：:，,·、/）)":
            dist = abs(i - target)
            if best is None or dist < best[0]:
                best, cut = (dist, i + 1), i + 1
    if cut is None:
        cut = max(1, len(title) // 2)
    return [title[:cut].rstrip(), title[cut:].lstrip()]


def layout_title(title):
    for size in (72, 64, 56, 48, 44):
        if text_width(title, size) <= TEXT_ZONE_W:
            return [title], size
    lines = split_balanced(title)
    for size in (56, 48, 44, 40, 36):
        if max(text_width(line, size) for line in lines) <= TEXT_ZONE_W:
            return lines, size
    return lines, 36


def svg_defs(a, b):
    return f"""
  <defs>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{a}"/>
      <stop offset="100%" stop-color="{b}"/>
    </linearGradient>
    <pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.3" fill="#26324a"/>
    </pattern>
  </defs>"""


def motif_terminal(a, b):
    return f"""
  <circle cx="930" cy="200" r="128" fill="none" stroke="#1c2a44" stroke-width="1.5"/>
  <rect x="780" y="122" width="300" height="168" rx="14" fill="#101a2e" stroke="url(#accent)" stroke-width="2.5"/>
  <line x1="780" y1="154" x2="1080" y2="154" stroke="#26324a" stroke-width="1.5"/>
  <circle cx="802" cy="138" r="5" fill="{a}"/>
  <circle cx="822" cy="138" r="5" fill="{b}" opacity="0.7"/>
  <circle cx="842" cy="138" r="5" fill="#334155"/>
  <rect x="802" y="176" width="180" height="11" rx="5.5" fill="#334155"/>
  <rect x="802" y="200" width="126" height="11" rx="5.5" fill="{a}" opacity="0.65"/>
  <rect x="802" y="224" width="152" height="11" rx="5.5" fill="#26324a"/>
  <path d="M802 258 l12 8 -12 8" fill="none" stroke="{b}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="826" y="261" width="70" height="9" rx="4.5" fill="#334155"/>"""


def motif_flow(a, b):
    nodes = [(806, 200), (940, 200), (1074, 200)]
    parts = ['\n  <circle cx="940" cy="200" r="128" fill="none" stroke="#1c2a44" stroke-width="1.5"/>']
    for x1, x2 in ((nodes[0][0] + 46, nodes[1][0] - 46), (nodes[1][0] + 46, nodes[2][0] - 46)):
        parts.append(f'  <line x1="{x1}" y1="200" x2="{x2 - 8}" y2="200" stroke="{a}" stroke-width="2.5" stroke-linecap="round" opacity="0.8"/>')
        parts.append(f'  <path d="M{x2} 200 l-11 -7 M{x2} 200 l-11 7" stroke="{b}" stroke-width="2.5" fill="none" stroke-linecap="round"/>')
    for i, (cx, cy) in enumerate(nodes):
        color = "url(#accent)" if i == 1 else "#3b4a68"
        fill = "#101a2e" if i == 1 else "#0e1730"
        parts.append(f'  <rect x="{cx - 46}" y="{cy - 29}" width="92" height="58" rx="13" fill="{fill}" stroke="{color}" stroke-width="2.5"/>')
        parts.append(f'  <rect x="{cx - 26}" y="{cy - 8}" width="52" height="10" rx="5" fill="{a if i == 1 else "#334155"}" opacity="{0.85 if i == 1 else 1}"/>')
    return "\n  " + "\n  ".join(parts)


def motif_layers(a, b):
    layers = [(796, 138, "#3b4a68"), (816, 178, "#2c3a58"), (836, 218, "url(#accent)")]
    parts = ['\n  <circle cx="940" cy="200" r="128" fill="none" stroke="#1c2a44" stroke-width="1.5"/>']
    for x, y, stroke in layers:
        parts.append(f'  <rect x="{x}" y="{y}" width="248" height="52" rx="13" fill="#0e1730" stroke="{stroke}" stroke-width="2.5"/>')
        parts.append(f'  <rect x="{x + 20}" y="{y + 21}" width="90" height="10" rx="5" fill="#334155"/>')
    parts.append(f'  <circle cx="1032" cy="244" r="7" fill="{b}"/>')
    return "\n  " + "\n  ".join(parts)


def motif_graph(a, b):
    nodes = [(806, 148), (1074, 148), (858, 256), (1022, 256)]
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (0, 3)]
    parts = ['\n  <circle cx="940" cy="200" r="128" fill="none" stroke="#1c2a44" stroke-width="1.5"/>']
    for i, j in edges:
        (x1, y1), (x2, y2) = nodes[i], nodes[j]
        parts.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#2c3a58" stroke-width="2"/>')
    for i, (cx, cy) in enumerate(nodes):
        r = 26 if i == 0 else 18
        stroke = "url(#accent)" if i == 0 else "#3b4a68"
        parts.append(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="#0e1730" stroke="{stroke}" stroke-width="2.5"/>')
        parts.append(f'  <circle cx="{cx}" cy="{cy}" r="{r - 10}" fill="{a}" opacity="{0.75 if i == 0 else 0.25}"/>')
    return "\n  " + "\n  ".join(parts)


def motif_chip(a, b):
    parts = ['\n  <circle cx="940" cy="200" r="128" fill="none" stroke="#1c2a44" stroke-width="1.5"/>']
    parts.append('  <rect x="848" y="148" width="184" height="104" rx="16" fill="#0e1730" stroke="url(#accent)" stroke-width="2.5"/>')
    parts.append(f'  <rect x="884" y="180" width="112" height="40" rx="9" fill="{a}" opacity="0.16"/>')
    parts.append(f'  <rect x="902" y="194" width="76" height="12" rx="6" fill="{b}" opacity="0.8"/>')
    for i in range(4):
        y = 162 + i * 26
        parts.append(f'  <line x1="812" y1="{y}" x2="848" y2="{y}" stroke="#3b4a68" stroke-width="3" stroke-linecap="round"/>')
        parts.append(f'  <line x1="1032" y1="{y}" x2="1068" y2="{y}" stroke="#3b4a68" stroke-width="3" stroke-linecap="round"/>')
    return "\n  " + "\n  ".join(parts)


def motif_doc(a, b):
    return f"""
  <circle cx="940" cy="200" r="128" fill="none" stroke="#1c2a44" stroke-width="1.5"/>
  <path d="M824 118 h128 l40 40 v124 a10 10 0 0 1 -10 10 h-158 a10 10 0 0 1 -10 -10 v-154 a10 10 0 0 1 10 -10 z"
        fill="#0e1730" stroke="url(#accent)" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M952 118 v40 h40" fill="none" stroke="{a}" stroke-width="2.5" stroke-linejoin="round"/>
  <rect x="842" y="188" width="130" height="10" rx="5" fill="#334155"/>
  <rect x="842" y="212" width="96" height="10" rx="5" fill="#334155"/>
  <rect x="842" y="236" width="112" height="10" rx="5" fill="{a}" opacity="0.65"/>
  <circle cx="1042" cy="272" r="30" fill="#101a2e" stroke="{b}" stroke-width="3"/>
  <line x1="1064" y1="294" x2="1086" y2="316" stroke="{b}" stroke-width="4" stroke-linecap="round"/>"""


MOTIFS = {
    "terminal": motif_terminal,
    "flow": motif_flow,
    "layers": motif_layers,
    "graph": motif_graph,
    "chip": motif_chip,
    "doc": motif_doc,
}


def render(title, tags, category):
    a, b, motif = CATEGORY_STYLE.get(category, DEFAULT_STYLE)
    lines, size = layout_title(title)
    baselines = [214] if len(lines) == 1 else [166, 238]
    title_svg = "\n".join(
        f'  <text x="{TITLE_X}" y="{y}" font-family="\'PingFang SC\',\'Noto Sans SC\',\'Helvetica Neue\',sans-serif" '
        f'font-size="{size}" font-weight="700" fill="#F8FAFC">{escape(line)}</text>'
        for line, y in zip(lines, baselines)
    )

    chip_svg = ""
    x = TITLE_X
    for tag in tags[:2]:
        label = escape(tag)
        w = text_width(tag, 21) + 36
        chip_svg += (
            f'  <rect x="{x:.0f}" y="296" width="{w:.0f}" height="42" rx="21" fill="#152238" stroke="#2c3a58" stroke-width="1.5"/>\n'
            f'  <text x="{x + 18:.0f}" y="324" font-family="ui-monospace,\'SF Mono\',Menlo,monospace" '
            f'font-size="21" fill="#9FB3D1">{label}</text>\n'
        )
        x += w + 14

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}" role="img" aria-label="{escape(title)}">{svg_defs(a, b)}
  <rect width="{CANVAS_W}" height="{CANVAS_H}" fill="#0B1220"/>
  <rect width="{CANVAS_W}" height="{CANVAS_H}" fill="url(#dots)" opacity="0.55"/>
  <rect x="0" y="0" width="6" height="{CANVAS_H}" fill="url(#accent)"/>
  <text x="{CANVAS_W - 96}" y="64" text-anchor="end" font-family="ui-monospace,'SF Mono',Menlo,monospace" font-size="20" fill="#64748B">zata.cc</text>
  {MOTIFS[motif](a, b).strip()}
  {title_svg}
  <rect x="{TITLE_X}" y="264" width="112" height="6" rx="3" fill="url(#accent)"/>
  {chip_svg.strip()}
</svg>
"""


def targets():
    if len(sys.argv) > 1:
        return [Path(p) for p in sys.argv[1:]]
    found = []
    for md in sorted((ROOT / "content" / "post").rglob("index.md")):
        meta = parse_frontmatter(md.read_text(encoding="utf-8"))
        if meta.get("image") == "images/index/index.svg":
            found.append(md)
    return found


def main():
    for md in targets():
        meta = parse_frontmatter(md.read_text(encoding="utf-8"))
        title = meta.get("title", md.parent.name)
        tags = meta.get("tags") or []
        category = (meta.get("categories") or [""])[0]
        out = md.parent / "images" / "index" / "index.svg"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(title, tags, category), encoding="utf-8")
        print(f"OK  {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
