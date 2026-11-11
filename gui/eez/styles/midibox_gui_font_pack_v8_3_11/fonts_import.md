# Midibox GUI Font Pack (LVGL 8.3.11)

This pack gives you **ready-to-use styles** that map to LVGL's built‑in Montserrat fonts
and optional placeholders for **ExtraBold** if you later import a local TTF.

## What's inside
- `midibox_fonts.eez-style` — EEZ Studio style collection with named styles:
  - `font_montserrat_28_extrabold`  *(placeholder → currently uses Bold 28)*
  - `font_montserrat_26_bold`
  - `font_montserrat_22` *(Regular)*
  - `font_montserrat_18_semibold` *(uses Bold 18 as a close match)*
  - `font_montserrat_16` *(Regular)*
- `fonts_import.md` — this guide

---

## How to import in EEZ Studio

1. Open your project → **Assets → Styles**.
2. Click **Import** and select `midibox_fonts.eez-style`.
3. The styles will appear in the **Text Font** dropdown of any widget.

> These styles are mapped to **built-in LVGL fonts** that ship with 8.3.11,
> so they work immediately with **no external TTFs** required.

---

## Optional: Real ExtraBold (TTF)

If you want a true ExtraBold weight:

1. Download `Montserrat-ExtraBold.ttf` from the official source (e.g., Google Fonts).
2. In EEZ Studio: **Assets → Fonts → Add Font** → choose `TTF` → select `Montserrat-ExtraBold.ttf`.
3. Set **Pixel size** to **28** (or the sizes you prefer).
4. In **Assets → Styles**, edit `font_montserrat_28_extrabold` style to point to your imported font.

Until you import the TTF, `font_montserrat_28_extrabold` falls back to LVGL's built-in **Bold 28**.

---

## Suggested usage map

- Titles / Big numbers: `font_montserrat_26_bold`
- Section headers: `font_montserrat_22`
- Labels / Body: `font_montserrat_16`
- Emphasis / Pills / Buttons: `font_montserrat_18_semibold` (Bold 18 proxy)
- Hero emphasis: `font_montserrat_28_extrabold` (falls back to Bold 28 until you import TTF)
