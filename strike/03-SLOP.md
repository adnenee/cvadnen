# 03-SLOP.md - measured evidence

- `!important` declarations: **259** - cascade is unwinnable; patching on top of this is why it looks sloppy.
- Inline `style="..."` attributes: **484** - hardcode colour/spacing outside CSS.
- Competing font families: **5** distinct stacks.
  - `monospace` x6
  - `Outfit', sans-serif` x5
  - `Plus Jakarta Sans', sans-serif` x5
  - `Playfair Display', serif` x2
  - `Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` x1
- Distinct `border-radius` values: **20** - no radius scale.
  - 12px x18, 8px x11, 50% x9, 6px x8, 0 x6, 4px x5, 16px x4, 3px x3
- Gradient text (`background-clip`): **3**
- `box-shadow` declarations: **49**
- Emoji used as icons: **0** ()
- `<img>` tags: **19**
- Distinct class names: **153**