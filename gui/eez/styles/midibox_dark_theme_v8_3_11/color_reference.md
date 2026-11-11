# Midibox Dark Neon Theme (LVGL 8.3.11)

This theme matches the Midibox/ Holson Instruments visual identity:
dark graphite panels, neon cyan highlights, warm amber accents.

## 🎨 Core Palette
| Role | Hex | Description |
|------|-----|-------------|
| Primary | `#00F0FF` | Neon cyan (accent glow) |
| Accent | `#FF9900` | Warm amber (mod, warning, LEDs) |
| Surface | `#1C1F24` | Deep graphite background |
| Container | `#2A2E35` | Slightly lighter panel |
| Active / Focus | `#00C0E0` | Bright aqua edge |
| Text | `#E0E0E0` | Light text |
| Secondary Text | `#A0A0A0` | Muted labels |
| Border | `#33373D` | Subtle line separators |
| Error | `#FF4C4C` | Limit, peak, or fault state |

---

## 🧩 How to Use
After importing `midibox_dark_theme.eez-style` in EEZ Studio:

1. Go to **Assets → Styles → Import**.
2. Choose `midibox_dark_theme.eez-style`.
3. You can then apply:
   - `style_panel`
   - `style_container`
   - `style_btn_primary`
   - `style_btn_accent`
   - `style_label_text`
   - `style_label_secondary`
   - `style_warning`
4. Neon glow buttons use LVGL shadows for focus/active states.

---

## ✨ Neon Look
Buttons and sliders have a cyan glow when active:
- Shadow width: 8 px
- Shadow color: `#00C0E0`
- Glow intensity tuned for 240x320 TFT brightness.
