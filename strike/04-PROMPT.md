# 04-PROMPT.md (v2) — paste this into GPT-6 Astra

> One message. Attach the four files listed. Do not let it open `index.html`.

---

```text
You are restyling an academic CV website by writing an OVERRIDE LAYER.
Read ONLY these four files:

  strike/00-BRIEF.md            direction, constraints, named fixes
  strike/01-CLASSES.md          every class and id in use, with frequency
  strike/02-MARKUP-SAMPLE.html  a representative slice of markup
  strike/03-SLOP.md             measured evidence of what is wrong

Do NOT open index.html. It is 320 KB (~89,000 tokens) and it is not needed.
If something is missing, say so in your Gaps list instead of opening it.

The critical rule: the existing 92 KB inline stylesheet STAYS AS IT IS.
You are not replacing it. Your file loads after it and changes only what it
names explicitly. A previous attempt replaced it and destroyed the layout.

Therefore:
  - Do not re-emit, restate, or "clean up" any existing CSS.
  - Do not touch layout properties: display, position, width, height,
    padding, margin, grid-*, flex-*.
  - The sidebar is dark and must stay dark - its text is white-on-dark via
    inline styles you cannot edit.
  - You MAY and SHOULD use !important: the existing sheet has 259 of them.

Deliverable, in this order:
  1. assets/theme.css   250-450 lines, override layer only
  2. Assumptions        max 10 lines
  3. Gaps               max 10 lines

No clarifying questions. No HTML output. No restating the brief.
```

---

## Why this version is different from v1

v1 told the model the old stylesheet was being deleted and asked for a
from-scratch replacement. That was wrong and it wrecked the page. v2 inverts
it: the existing CSS is untouchable, and the model writes a small override
layer on top. Layout survives by construction.

## Expected cost

| | Tokens |
|---|---|
| Input (4 files ≈ 20 KB) | ~6,000 |
| Output (override layer ≈ 400 lines) | ~6,000 |
| **Total, one turn** | **~12,000** |

## After Astra answers

Switch straight back to the cheap model. Then, for free:

```
# add one line to index.html, right before </head>:
<link rel="stylesheet" href="assets/theme.css">
```

I will do that injection and the visual check.
