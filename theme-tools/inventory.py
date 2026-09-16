#!/usr/bin/env python3
"""
inventory.py - build the "strike package" a premium model needs.

Instead of handing the premium model a 320 KB file (~89k tokens), we hand it:
  01-CLASSES.md        every class/ID in use, with counts  (~8k tokens)
  02-MARKUP-SAMPLE.html a representative slice of markup   (~3k tokens)
  03-SLOP.md           measured evidence of what looks wrong

The premium model can then write a from-scratch design system without ever
reading the source file. That is the whole trick.

Usage:  python inventory.py index.html --out strike
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

CLASS_RE = re.compile(r'class="([^"]*)"')
ID_RE = re.compile(r'id="([^"]*)"')
TAG_RE = re.compile(r"<([a-zA-Z][\w-]*)")
IMG_RE = re.compile(r"<img\b[^>]*>")
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]"
)


def body_text(text: str) -> tuple[str, int]:
    """Return markup after </style>, plus the line offset."""
    m = re.search(r"</style>", text, re.IGNORECASE)
    if not m:
        return text, 0
    offset = text[: m.end()].count("\n")
    return text[m.end() :], offset


def class_inventory(body: str) -> tuple[Counter, Counter, Counter]:
    classes: Counter = Counter()
    ids: Counter = Counter()
    tags: Counter = Counter()
    for c in CLASS_RE.findall(body):
        for tok in c.split():
            tok = tok.strip()
            if tok:
                classes[tok] += 1
    for i in ID_RE.findall(body):
        ids[i] += 1
    for t in TAG_RE.findall(body):
        tags[t.lower()] += 1
    return classes, ids, tags


def locate(anchor: str, body: str) -> int | None:
    m = re.search(r'id="%s"' % re.escape(anchor), body)
    return m.start() if m else None


def markup_sample(text: str, body: str, anchors: list[str], budget: int) -> str:
    """Head + a window of markup around each anchor, capped at `budget` chars."""
    head = text[: text.lower().find("</style>")]
    head = re.sub(r"<style[\s\S]*?</style>", "<!-- STYLE BLOCK REMOVED -->", head, flags=re.I)
    out: list[str] = ["<!-- SAMPLE: <head> + one window per section. NOT the full file. -->", head.strip()]
    per = max(600, (budget - len(head)) // max(1, len(anchors)))
    for a in anchors:
        pos = locate(a, body)
        if pos is None:
            out.append(f"\n<!-- section '{a}': anchor id not found -->")
            continue
        start = body.rfind("\n", 0, max(0, pos - 200))
        chunk = body[start : pos + per]
        out.append(f"\n<!-- ===== section: {a} ===== -->\n{chunk.strip()}")
    joined = "\n".join(out)
    return joined[:budget]


def slop_report(text: str, body: str, classes: Counter) -> str:
    important = len(re.findall(r"!important", text))
    fonts = Counter(re.findall(r"font-family: *'?([A-Za-z0-9 ,'\-]+)'?", text))
    radii = Counter(re.findall(r"border-radius: *([^;]+);", text))
    grad_text = len(re.findall(r"background-clip", text))
    shadows = len(re.findall(r"box-shadow", text))
    emoji = Counter(EMOJI_RE.findall(body))
    imgs = len(IMG_RE.findall(body))
    inline_styles = len(re.findall(r'style="', body))

    L: list[str] = ["# 03-SLOP.md - measured evidence\n"]
    L.append(f"- `!important` declarations: **{important}** - cascade is unwinnable; patching on top of this is why it looks sloppy.")
    L.append(f"- Inline `style=\"...\"` attributes: **{inline_styles}** - hardcode colour/spacing outside CSS.")
    L.append(f"- Competing font families: **{len(fonts)}** distinct stacks.")
    for f, n in fonts.most_common(8):
        L.append(f"  - `{f.strip()}` x{n}")
    L.append(f"- Distinct `border-radius` values: **{len(radii)}** - no radius scale.")
    L.append(f"  - {', '.join(f'{v.strip()} x{n}' for v, n in radii.most_common(8))}")
    L.append(f"- Gradient text (`background-clip`): **{grad_text}**")
    L.append(f"- `box-shadow` declarations: **{shadows}**")
    L.append(f"- Emoji used as icons: **{sum(emoji.values())}** ({''.join(emoji.keys())})")
    L.append(f"- `<img>` tags: **{imgs}**")
    L.append(f"- Distinct class names: **{len(classes)}**")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--out", default="strike")
    ap.add_argument("--anchors", default="experience,education,responsibilities,scientific,projects,certification,media,partnership")
    ap.add_argument("--budget", type=int, default=9000, help="max chars of markup sample")
    args = ap.parse_args()

    path = Path(args.file)
    text = path.read_text(encoding="utf-8", errors="replace")
    body, _ = body_text(text)
    classes, ids, tags = class_inventory(body)
    anchors = [a.strip() for a in args.anchors.split(",") if a.strip()]

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # 01 - classes
    md = ["# 01-CLASSES.md - every class / id in use\n",
          "Sorted by frequency. A premium model writing a from-scratch stylesheet",
          "should cover at least the top ~80.\n",
          "## Classes\n", "| Class | Count |", "|---|---|"]
    for c, n in classes.most_common(200):
        md.append(f"| `.{c}` | {n} |")
    md.append("\n## IDs\n| ID | Count |\n|---|---|")
    for i, n in ids.most_common(60):
        md.append(f"| `#{i}` | {n} |")
    md.append("\n## Tags\n| Tag | Count |\n|---|---|")
    for t, n in tags.most_common(25):
        md.append(f"| `<{t}>` | {n} |")
    (out / "01-CLASSES.md").write_text("\n".join(md), encoding="utf-8")

    # 02 - markup sample
    (out / "02-MARKUP-SAMPLE.html").write_text(
        markup_sample(text, body, anchors, args.budget), encoding="utf-8"
    )

    # 03 - slop
    (out / "03-SLOP.md").write_text(slop_report(text, body, classes), encoding="utf-8")

    print(f"[inventory] {len(classes)} classes, {len(ids)} ids, {len(tags)} tags")
    for f in sorted(out.iterdir()):
        print(f"[inventory] {f}  {f.stat().st_size/1024:.1f} KB  (~{int(f.stat().st_size/3.6):,} tokens)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
