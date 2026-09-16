#!/usr/bin/env python3
"""
swap_css.py - the free mechanical step, run AFTER the premium model delivers
              assets/theme.css.

Does four things, zero model tokens:
  1. Extracts the old <style> block to assets/styles.legacy.css (kept, unlinked).
  2. Replaces it with <link rel="stylesheet" href="assets/theme.css">.
  3. Injects the Google Fonts <link>s the new theme needs.
  4. Neutralises COSMETIC inline style declarations so the theme can win.
     Layout-critical inline props (padding 374, border 366, font-size 297) are
     deliberately PRESERVED - only colour/type/shadow props are touched, and
     inline border colours are re-pointed at var(--rule) rather than removed.

Usage:
  python theme-tools/swap_css.py index.html --dry
  python theme-tools/swap_css.py index.html
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

STYLE_RE = re.compile(r"<style\b[^>]*>.*?</style>", re.DOTALL | re.IGNORECASE)
INLINE_RE = re.compile(r'style="([^"]*)"')

# Declared purely cosmetic -> delete so the stylesheet wins.
COSMETIC = {
    "color", "background-color", "border-radius", "box-shadow",
    "font-family", "text-shadow", "outline-color",
}
# Kept but colour-rewritten (layout depends on the shorthand existing).
BORDER_PROPS = ("border", "border-top", "border-bottom", "border-left", "border-right")
COLOUR_RE = re.compile(
    r"(#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|\b(?:red|blue|green|gray|grey|orange|"
    r"yellow|purple|pink|teal|navy|gold|white|black|silver)\b)",
    re.IGNORECASE,
)

FONTS_HREF = (
    "https://fonts.googleapis.com/css2?"
    "family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&"
    "family=Source+Sans+3:wght@400;500;600&display=swap"
)


def neutralise(style: str) -> tuple[str, int]:
    """Strip cosmetic props, recolour borders. Return (new_style, n_changes)."""
    kept: list[str] = []
    changed = 0
    for decl in style.split(";"):
        d = decl.strip()
        if not d or ":" not in d:
            continue
        prop, _, val = d.partition(":")
        p = prop.strip().lower()
        v = val.strip()

        if p in COSMETIC:
            changed += 1
            continue
        if p == "background" and not v.lower().startswith("url("):
            if COLOUR_RE.search(v):
                changed += 1
                continue
        if p in BORDER_PROPS:
            new_v, n = COLOUR_RE.subn("var(--rule)", v)
            if n:
                changed += n
                kept.append(f"{p}:{new_v}")
                continue
        kept.append(d)

    return ";".join(kept), changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--theme", default="assets/theme.css")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    path = Path(args.file)
    text = path.read_text(encoding="utf-8", errors="replace")

    m = STYLE_RE.search(text)
    if not m:
        print("[swap] no <style> block found — already external?")
        return 1

    legacy = m.group(0)
    theme_css = Path(args.theme)
    if not theme_css.is_file() and not args.dry:
        print(f"[swap] {theme_css} not found. Put the generated file there first.", file=sys.stderr)
        return 1

    # 1 + 2 + 3
    text = text[: m.start()] + f'<link rel="stylesheet" href="{args.theme}">' + text[m.end():]
    font_block = (
        f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        f'    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'    <link rel="stylesheet" href="{FONTS_HREF}">'
    )
    old_font = re.search(r'<link[^>]*fonts\.googleapis\.com[^>]*>', text)
    if old_font:
        # Replace the old Outfit / Plus Jakarta / Playfair request in place.
        text = text[: old_font.start()] + font_block + text[old_font.end():]
    else:
        text = text.replace("</head>", f"    {font_block}\n</head>", 1)

    # 4
    total = 0
    def sub(mi: re.Match) -> str:
        nonlocal total
        new, n = neutralise(mi.group(1))
        total += n
        return f'style="{new}"'
    text = INLINE_RE.sub(sub, text)

    if args.dry:
        print(f"[swap] DRY RUN — would extract {len(legacy)/1024:.0f} KB of legacy CSS, "
              f"link {args.theme}, inject fonts, neutralise {total} cosmetic inline decls.")
        return 0

    assets = Path("assets")
    assets.mkdir(exist_ok=True)
    (assets / "styles.legacy.css").write_text(legacy, encoding="utf-8")

    backup = path.with_suffix(path.suffix + ".bak")
    if not backup.is_file():
        backup.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

    path.write_text(text, encoding="utf-8")
    print(f"[swap] legacy CSS -> assets/styles.legacy.css ({len(legacy)/1024:.0f} KB, unlinked)")
    print(f"[swap] linked {args.theme} + Google Fonts")
    print(f"[swap] neutralised {total} cosmetic inline declarations")
    print(f"[swap] backup: {backup.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
