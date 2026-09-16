#!/usr/bin/env python3
"""
theme.py - zero-token theme tooling.

The whole point of this file: do the mechanical 80% of a website theme change
WITHOUT spending a single premium-model token. Code is free; inference is not.

Commands
--------
  map     Scan a site file and write .workbuddy-ai/THEME-MAP.md
          (token inventory, hardcoded-colour hotspots, inline-style hotspots,
          section index). This is the recon artifact a premium model reads
          INSTEAD OF the 320 KB source file.

  apply   Apply a THEME-SPEC.json token map to the file, mechanically.
          Supports --dry to preview, and git is recommended before running.

Usage
-----
  python theme.py map   index.html
  python theme.py apply index.html THEME-SPEC.json --dry
  python theme.py apply index.html THEME-SPEC.json
  python theme.py apply index.html THEME-SPEC.json --literals   # also rewrite
                                                               # raw hex literals

Exit codes: 0 ok, 1 usage/IO error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RGB_RE = re.compile(r"\brgba?\([^)]*\)", re.IGNORECASE)
ROOT_RE = re.compile(r":root\s*\{(.*?)\}", re.DOTALL)
VAR_DECL_RE = re.compile(r"(--[\w-]+)\s*:\s*([^;]+);")
INLINE_STYLE_RE = re.compile(r'style="([^"]*)"')
SECTION_RE = re.compile(
    r"<(section|header|footer|nav|main|aside)\b[^>]*?(?:id=\"([^\"]+)\"|class=\"([^\"]+)\")?[^>]*>",
    re.IGNORECASE,
)


# ---------------------------------------------------------------- map command
def find_root_vars(text: str) -> list[tuple[str, str, int]]:
    """Return [(var_name, value, line_no)] declared inside :root."""
    out: list[tuple[str, str, int]] = []
    for m in ROOT_RE.finditer(text):
        base_line = text[: m.start()].count("\n") + 1
        for vm in VAR_DECL_RE.finditer(m.group(1)):
            line = base_line + m.group(1)[: vm.start()].count("\n")
            out.append((vm.group(1), vm.group(2).strip(), line))
    return out


def scan_literals(text: str) -> tuple[Counter, dict[str, list[int]], Counter, int]:
    """Count hex + rgb() literals and record where they live."""
    hex_counts: Counter = Counter()
    hex_lines: dict[str, list[int]] = {}
    rgb_counts: Counter = Counter()
    for i, line in enumerate(text.splitlines(), 1):
        for hm in HEX_RE.finditer(line):
            h = hm.group(0).lower()
            hex_counts[h] += 1
            hex_lines.setdefault(h, []).append(i)
        for rm in RGB_RE.finditer(line):
            rgb_counts[rm.group(0)] += 1
    inline = len(INLINE_STYLE_RE.findall(text))
    return hex_counts, hex_lines, rgb_counts, inline


def section_index(text: str) -> list[tuple[int, str, str]]:
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines, 1):
        m = SECTION_RE.search(line)
        if m:
            tag = m.group(1).lower()
            ident = m.group(2) or m.group(3) or ""
            out.append((i, tag, ident[:70]))
    return out


def cmd_map(path: Path, out_dir: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    size_kb = len(text.encode("utf-8")) / 1024

    vars_ = find_root_vars(text)
    hex_counts, hex_lines, rgb_counts, inline = scan_literals(text)
    sections = section_index(text)

    md: list[str] = []
    md.append(f"# THEME-MAP - {path.name}\n")
    md.append(f"- File: `{path}`")
    md.append(f"- Size: **{size_kb:,.0f} KB** / {len(lines):,} lines")
    md.append(f"- Est. tokens if read whole: **~{int(len(text) / 3.6):,}** (do NOT feed to a premium model)\n")

    md.append("## 1. Design tokens (`:root`)\n")
    if vars_:
        md.append("| Variable | Value | Line |")
        md.append("|---|---|---|")
        for name, val, ln in vars_:
            md.append(f"| `{name}` | `{val}` | {ln} |")
        md.append(f"\n**{len(vars_)} tokens.** Editing these alone re-themes every rule that uses `var(--…)`.")
    else:
        md.append("_No `:root` block found. Consider creating one before re-theming._")

    md.append("\n## 2. Hardcoded hex literals (ignore tokens — theme leaks here)\n")
    md.append("| Colour | Count | First lines |")
    md.append("|---|---|---|")
    for h, c in hex_counts.most_common(30):
        ls = ", ".join(str(x) for x in hex_lines[h][:6])
        md.append(f"| `{h}` | {c} | {ls} |")

    md.append(f"\n`rgb()/rgba()` literals: **{sum(rgb_counts.values())}**")
    md.append(f"| Inline `style=\"…\"` attributes: **{inline}** — these bypass CSS and are the #1 cause of a half-applied theme. |\n")

    md.append("## 3. Section index (line numbers for surgical edits)\n")
    md.append("| Line | Tag | id / class |")
    md.append("|---|---|---|")
    for ln, tag, ident in sections[:60]:
        md.append(f"| {ln} | `{tag}` | `{ident}` |")
    if len(sections) > 60:
        md.append(f"\n_…and {len(sections) - 60} more._")

    md.append("\n## 4. How to use this file\n")
    md.append(
        "1. Do NOT paste this source file into a premium model.\n"
        "2. Write `THEME-SPEC.json` with only the tokens you want changed.\n"
        "3. Run `python theme.py apply <file> THEME-SPEC.json --dry` (free).\n"
        "4. Apply. Only send the premium model the *remaining* taste problems, "
        "as line ranges, never the whole file.\n"
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "THEME-MAP.md"
    out.write_text("\n".join(md), encoding="utf-8")
    print(f"[theme.py] wrote {out}")
    print(f"[theme.py] {len(vars_)} tokens | {sum(hex_counts.values())} hex literals "
          f"| {sum(rgb_counts.values())} rgb() | {inline} inline styles | ~{int(len(text)/3.6):,} tokens if read whole")
    return 0


# -------------------------------------------------------------- apply command
def cmd_apply(path: Path, spec_path: Path, dry: bool, do_literals: bool) -> int:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    tokens: dict[str, str] = spec.get("tokens", {})
    literals: dict[str, str] = spec.get("literals", {})

    if not tokens and not literals:
        print("[theme.py] spec has no 'tokens' or 'literals'. Nothing to do.", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8", errors="replace")
    original = text
    changed_tokens = 0
    changed_literals = 0

    # 1) rewrite :root declarations
    def repl_root(m: re.Match) -> str:
        nonlocal changed_tokens
        body = m.group(1)

        def repl_var(vm: re.Match) -> str:
            nonlocal changed_tokens
            name, value = vm.group(1), vm.group(2)
            if name in tokens and tokens[name] != value.strip():
                changed_tokens += 1
                return f"{name}: {tokens[name]};"
            return vm.group(0)

        return m.group(0).replace(body, VAR_DECL_RE.sub(repl_var, body))

    text = ROOT_RE.sub(repl_root, text)

    # 2) optionally rewrite raw literals everywhere else
    if do_literals and literals:
        for old, new in literals.items():
            n = text.lower().count(old.lower())
            if n:
                text = re.sub(re.escape(old), new, text, flags=re.IGNORECASE)
                changed_literals += n

    if dry:
        print(f"[theme.py] DRY RUN -> would change {changed_tokens} token(s), "
              f"{changed_literals} literal(s). No files written.")
        return 0

    if text == original:
        print("[theme.py] no changes produced — check your spec keys match the token names.")
        return 1

    backup = path.with_suffix(path.suffix + ".bak")
    backup.write_text(original, encoding="utf-8")
    path.write_text(text, encoding="utf-8")
    print(f"[theme.py] applied {changed_tokens} token(s), {changed_literals} literal(s).")
    print(f"[theme.py] backup at {backup.name} — verify, then delete it.")
    return 0


# ---------------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Zero-token theme tooling.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_map = sub.add_parser("map", help="scan a file and write THEME-MAP.md")
    p_map.add_argument("file")
    p_map.add_argument("--out", default=".workbuddy-ai")

    p_apply = sub.add_parser("apply", help="apply a THEME-SPEC.json")
    p_apply.add_argument("file")
    p_apply.add_argument("spec")
    p_apply.add_argument("--dry", action="store_true")
    p_apply.add_argument("--literals", action="store_true",
                         help="also rewrite raw hex literals (broader, verify visually)")

    args = ap.parse_args(argv)
    target = Path(args.file)
    if not target.is_file():
        print(f"[theme.py] not found: {target}", file=sys.stderr)
        return 1

    if args.cmd == "map":
        return cmd_map(target, Path(args.out))
    return cmd_apply(target, Path(args.spec), args.dry, args.literals)


if __name__ == "__main__":
    raise SystemExit(main())
