# 00-BRIEF.md (v2) — surgical restyle of an academic CV

## Read this first: an earlier attempt already failed

A previous pass tried to **replace** the stylesheet with a clean from-scratch
one. It broke the layout badly and was reverted. Do not repeat it.

**You are writing an OVERRIDE LAYER, not a replacement.**
The existing 92 KB stylesheet stays exactly as it is. Your file is loaded
*after* it and only changes what it explicitly names.

## Why a rewrite cannot work (evidence)

- The file is 6,848 lines; 92 KB of bespoke CSS lives in `<style>` (lines 12–3394).
- `.cv-container` is redefined **8 times** (lines 66, 75, 1436, 1999, 2014,
  2029, 2444, 3318) — the layout is patched across many breakpoints.
- **484 inline `style="…"` attributes** carry real layout:
  padding ×374, border ×366, font-size ×297.
- **259 `!important`** declarations.
- 52 `linear-gradient` uses, 10 `@keyframes`, 10 `animation:` declarations.

None of that survives a rewrite. Your layer rides on top of it, so it survives.

---

## What you MAY change

- colour, background, border-colour, box-shadow, text-shadow, border-radius
- font-family
- gradients → flat colour
- suppression of the named gimmicks below
- add a `@media print` block
- spacing only where you name it explicitly in your Assumptions

## What you MUST NOT change

- `display`, `position`, `top/right/bottom/left`, `float`, `clear`
- `grid-template-columns`, `grid-template-rows`, `flex-*`, `grid-gap`
- `width`, `height`, `min-width`, `max-width`
- `padding`, `margin`
- `font-size` — except where a named fix requires it
- the two-column grid (420px sidebar + fluid main)
- never delete or comment out an existing rule

## Hard constraint — ignoring this will break the page

**The sidebar is dark. Keep it dark.**

Its content is white-on-dark, carried by roughly 40 inline
`rgba(255, 255, 255, …)` colours that you are not allowed to touch. Making the
sidebar light renders that text invisible. Refine the dark; restyle the light
main column.

## `!important` is expected here

Because the existing sheet uses `!important` 259 times, your overrides need it
too. Use it freely — that is what an override layer is for.

---

## Direction: editorial academic

This is the CV of **Pr. Dr. Eng. CHERIF Adnane**, Senior Professor & Research
Director. Readers are hiring and funding committees, and they print it.
It should read like a well-set academic monograph — quiet, typographic,
authoritative. Not a startup landing page.

### Palette

```
--paper        #faf9f7   warm off-white (main column)
--ink          #16181d
--ink-2        #3d4149
--ink-3        #6b7078
--rule         #ddd9d2   hairline
--accent       #1f5c53   deep verdigris — the ONLY accent, max ~5% coverage
--accent-soft  #e8efec

sidebar        #14171c   flat, replaces the current gradient — stays dark
```

### Type

Currently 5 competing stacks (Outfit, Plus Jakarta Sans, Playfair Display,
monospace, and a system fallback). Reduce to **two**:

- **Source Serif 4** — headings, name, figures
- **Source Sans 3** — body and UI

Change families only; leave sizes alone unless you name the exception.

### Named gimmicks to neutralise

| Selector | Line | What to do |
|---|---|---|
| `.profile-img.floating` | 213–234 | Photo detaches and follows the scroll. Make it static (`position: static`) or hide it. |
| `.floating-shapes` | 126, 2008 | Decorative layer → hide |
| `.shape`, `.shape-1/2/3` | 136, 142, 152, 162 | Drifting blobs → hide |
| `.sidebar::before` | 104 | SVG grain overlay → hide |
| `background-clip: text` | 1711, 1712, 2671 | Gradient text → solid `--ink` |
| `.sidebar` gradient | 86 | → flat `#14171c` |
| `body` gradient | 44 | → flat `--paper` |
| `.skill-progress` | — | Neon bar → 2px hairline in `--accent` |
| `@keyframes` / `animation:` | 172, 235, 252, 268, 334, 360, 589, 603, 654, 1085 / 139, 231, 331, 346, 419, 445, 466, 651, 1082, 1631 | Stop decorative motion; keep scroll-progress if present |

### Also add

- `@media print` — single column, ink on white, no nav, no video,
  `break-inside: avoid` on `.experience-item`, `.education-item`, `.annex-item`
- Tidy the inconsistent radii (currently 20 distinct values) into 2–3 tokens
- Reduce the 49 `box-shadow` declarations toward hairline borders

---

## Deliverable

1. `assets/theme.css` — **250–450 lines**. Banner comments by group.
   Do not re-emit any existing CSS. Every rule you write must change
   something the current design gets wrong.
2. **Assumptions** — ≤10 lines.
3. **Gaps** — ≤10 lines.

No clarifying questions. No HTML. No restating the brief.
