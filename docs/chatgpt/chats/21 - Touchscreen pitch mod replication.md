# Touchscreen pitch mod replication

- ChatGPT conversation id: 68e8e0cb-6808-832c-ab30-d151615c966d
- Created: 2025-10-10 10:32
- Updated: 2025-10-10 10:46
- Project: Midibox raspberry pi
- Messages: 21

## User · 2025-10-10 10:32

Are there any touchscreens that could replicate pitch and mod wheels? Say 5cmx15cm 

## Tool (file_search) · 2025-10-10 10:32

> MidiBox Design Overview



Two Long Throw Faders for CC 



Transport Control via the MPR121 capacitive Touch

	Start, Stop, Rec, Jog L, Jog R, Loop, 



Pitch and Mod Wheel 



Fatar Midi Keyboard

	Aftertouch

	Velocity

	88 Keys



Touch Screen FT6236 and 

	

	Page 1

	Midi Transpose

	Midi Octave up/down

	Display Chords Played 

	Display 4 touch encoder parameters



	Page 2 - Arpeggiator

	Scale Major minor etc.

	Up/Down/Chord



	Page 3 - 2 Faders and 4 touch sensitive encoders Setup page

	Allow Change cc out of 2 faders

	Assign Touch sensitive encoders to internal functions such as midi transpose octave jump

	Or assign touch encoders to cc.



	Page 4 - Select USB Midi Out (for devices on USB-A ports



USB Midi out 

	USB-A allows class compliant midi devices such as synthesizers

	USB-C Allows connection to Class compliant Hosts such as OSX (gadget)





Other features

	Swipe functions 

	UI Design using a library such as Ktinter or Kivy, PyQt and PySide

	

Optional

RGB Leds available for suggestionsas previously tested

Buttons available for suggestions

	

	

Code Requirements



Skeleton Main.py - Not Bulky and full of code

Multiple Files/Modules for each Requirement (gestures, UI, Midi USB-C, Midi USB-A, Midi Scales CC and Transport functions.

Allows for Updates and my learning.

(When Project is complete) = Boot direct into Program with Boot Screen and no need for Pi OS interaction.













Hardware Equipment 



PI 4

Ft6236 3.2”TFT SPI  TouchScreen 240 x 320

MPR121 Break out (adafruit)

Midi and Pitch Wheels (analogue)

4 Smooth Encoders with Capacitive functionality and Clickable

Capacitive Pads for Transport Functions Not Purchased yet (make recommendations)

3D Printer for Case

Will need to create a 2M cable going from the FATAR Keyboard to my Midi Box

## Tool (file_search) · 2025-10-10 10:32

All the files uploaded by the user have been fully loaded. Searching won't provide additional information.

## Assistant · 2025-10-10 10:32

Yes — you can absolutely replicate **pitch and mod wheel** behaviour on a **touchscreen strip** roughly **5 × 15 cm**, and there are several suitable hardware options. Based on your *Midibox Build Overview* (which already uses an FT6236-based TFT touchscreen), here’s how this could work and which panels fit best:

---

### 🧠 Concept
A **touchstrip** acts like two continuous axes:
- **Pitch bend:** X-axis swipe with recentring spring emulation (returns to 0 in code).  
- **Modulation:** Y-axis or a separate vertical zone with persistent CC values.

This gives you **smooth, high-resolution control** (12-bit or higher via ADC emulation) and can visually show position/colour feedback, something traditional wheels can’t.

---

### 🧩 Recommended Touch Panels (~5 × 15 cm)

| Model | Size (approx.) | Controller | Interface | Notes |
|--------|----------------|-------------|------------|-------|
| **Tontec GT911 Capacitive Touch Panel** | 5 × 15 cm | GT911 | I²C | Widely available; supports multi-touch, great for custom strips. |
| **Waveshare Capacitive Touch Overlay (7″ cut strip)** | Custom (cut down to 5 × 15 cm) | FT6236 | I²C | You can reuse the same FT6236 driver you already use — ideal for uniformity. |
| **Adafruit MPR121 Capacitive Strip (DIY)** | 5 × 15 cm (PCB pads) | MPR121 | I²C | Not a display, but could work as a raw capacitive “touch ribbon.” |
| **Goodix GT5688 Touch Film** | 50 × 150 mm | GT5688 | I²C | Thin flexible film; perfect for embedding in a 3D-printed case, supports multitouch and gesture readout. |
| **ZynTouch / Azoteq IQS5xx Series** | Custom strip | Proprietary / I²C | Used in ROLI Seaboard; excellent analog feel and pressure sensing (costlier). |

---

### 🧰 Implementation Ideas
- Mount the strip **beside or below the TFT**.
- Use **Kivy or PyQt** to visualise a **virtual pitch/mod strip** — e.g. gradient bar or waveform motion.
- Add **soft return** for pitch (auto-centre to 0 CC = 64) and **hold-mode** for modulation.
- Optionally apply **LED feedback** around the strip using WS2812/WS2811 like your mod wheel plan.

---

### ⚙️ Integration with your setup
- The **FT6236 driver** already present in your Midibox build supports multiple touch zones, so you could reuse it.
- Just map a specific rectangle region (x/y coordinates) to act as:
  - Zone 1 → Pitch bend (send MIDI 0xE0)
  - Zone 2 → Mod wheel (send MIDI CC #1)

---

Would you like me to sketch a visual concept (render) showing how a 5 × 15 cm pitch/mod touchscreen strip would sit beside your current box layout? It could show both the functional zones and the display feedback.

## User · 2025-10-10 10:34

Any off the shelf capacitive touchscreens

## Assistant · 2025-10-10 10:34

Yes — there *are* off-the-shelf capacitive touch panels / overlays you could adapt to that purpose. The trick is finding one with sufficiently fine resolution and a shape you can integrate. Below are some real products + tips and caveats.

  
---

## ✅ Example off-the-shelf capacitive touch panels

Here are a few existing panels / overlays you can look at. (These are mostly small displays + touch, or touch overlays, which you could repurpose.)  
products{"selections":[["turn0product3","GT911 8″ Capacitive Touch Panel"],["turn0product1","Capacitive Touch Panel Overlay"],["turn0product6","EastRising Capacitive Touch Panel"],["turn0product19","5-inch Multi Touch Screen Panel"],["turn0product15","USB Capacitive Touch Panel (various sizes)"],["turn0product14","Capacitive Touch Display Module"],["turn0product7","BIGTREETECH 5\" Capacitive Touch"],["turn0product17","Allsee 15\" PCAP Touch Screen"]],"tags":["mid-size panel","overlay only","bare panel","small display","custom size set","module + display","Pi display","large display"]}  

Here are some that are more relevant to your ~5 × 15 cm target (or usable as strips/overlays):

- **product_entity["turn0product1","Capacitive Touch Panel Overlay for LattePanda Display"]** — an overlay without a display. You might cut / adapt it (if physically feasible).  
- **product_entity["turn0product6","EastRising Capacitive Touch Panel"]** — a bare panel; could be useful if the active area is close to what you need.  
- **product_entity["turn0product19","5-inch Multi Touch Screen Panel"]** — about 5″ diagonal; may approximate your needed strip, though the aspect ratio might not match your 5 × 15 cm exactly.  
- **product_entity["turn0product15","USB Capacitive Touch Panel (various sizes)"]** — often sold as sensor / digitizer glass in various rectangular sizes (you might find something close to 50×150 mm).  
- **product_entity["turn0product14","Capacitive Touch Display Module"]** — a combined touch + display module; might be more than you need, but useful if you want visual feedback built in.  
- **product_entity["turn0product7","BIGTREETECH 5\" Capacitive Touchscreen"]** — a touchscreen for Raspberry Pi / microcontroller; again, aspect ratio likely different but usable.  
- **product_entity["turn0product3","GT911 8″ Capacitive Touch Panel"]** — larger panel, but you could use just a strip section of it.  
- **product_entity["turn0product17","Allsee 15\" PCAP Touch Screen"]** — big surface; mostly for reference or if you want a whole touch front panel rather than a small strip.

---

## ⚠️ Considerations & constraints

- **Aspect ratio / active area**: Most standard touch panels are designed for displays (square or widescreen). A 5 × 15 cm elongated strip is nonstandard, so many panels will be too “short and wide” or “tall and narrow”. You may need to cut or mask parts of a larger panel.

- **Resolution & sensitivity**: To get smooth behaviour (for pitch / mod), you’ll want fairly high resolution (many sample points across the strip). Cheap panels sometimes quantize too coarsely.

- **Controller / interface**: Many capacitive panels come with I²C, SPI, or USB controllers. You’ll need one you can hook up to your microcontroller / Pi. Some touch controller ICs (like GT911) are commonly used.  

- **Edge trimming / cutting**: Some glass touch panels can be cut or trimmed (with care) to the desired shape, but it’s delicate and risky (cracking, damaging traces). Overlays (flexible touch foils) might be safer to trim.

- **Overlay vs full display**: If you use a touch overlay (i.e. just the touch sensor, no display), you’ll need something behind or under it to show visual feedback (or nothing if you just display via LEDs / other UI). Overlays are more flexible in shape.

- **Capacitive “strip sensors” / slider sensors**: Rather than full 2D panels, you can also find capacitive slider / strip sensors (essentially 1D touch sensors) which are more directly suited to pitch/mod behaviour. For example, small “capacitive touch slider” modules (e.g. Adafruit or TinyCircuits) can detect position along a line. (Here’s one: **Capacitive Touch Slider Wireling** with 80 mm length) citeturn0search0

- **Industrial / custom sensor fabs**: Companies like Orient Display or Zytronic manufacture touch sensors and panels, and can often do custom sizes (e.g. 50 × 150 mm) in volume. citeturn0search8turn0search13

---

If you like, I can hunt for capacitive touch panels *exactly* in the range **≈ 50 × 150 mm** (or close), and find ones available to ship to the UK. Do you want me to do that?

## User · 2025-10-10 10:35

It could be approx 5cmx15cm what is close and in aspect ratio ?

## Assistant · 2025-10-10 10:35

I dug around: not many commercial capacitive touch panels come exactly in a **50 × 150 mm** shape (or that extreme a 1:3 aspect ratio) — most are more square or wide formats. But there *are* some close ones and workable alternatives. Below are options + strategies + tradeoffs.

  
---

## ✅ Some product options (close / usable)

Here are a few touch / touch + display modules that might be close or usable by cropping / masking:

products{"selections":[["turn1product3","GT911 8\" Capacitive Touch Panel"],["turn1product16","GT911 7\" 165×100 mm Touch Panel"],["turn0product2","Capacitive Touch Overlay (for LattePanda display)"],["turn1product6","Capacitive Touch Panel with Controller"],["turn1product10","EastRising Capacitive Touch Panel"],["turn1product4","7-inch Capacitive Digitizer Glass"],["turn1product12","Waveshare 7.9\" Capacitive LCD"],["turn1product7","Capacitive Touch Display Module"]],"tags":["large square","closer to strip","overlay only","bare panel + ctrl","budget panel","digitizer glass","with display","complete module"]}  

Here are a few highlights:

- **product_entity["turn1product16","GT911 7\" 165×100 mm Touch Panel"]** — this gives you a panel that is 165 mm × 100 mm (aspect ~1.65:1). You could use a 50×150 mm strip from this, though you’d be discarding parts or masking regions.

- **product_entity["turn1product3","GT911 8\" Capacitive Touch Panel"]** — a larger square-ish panel; more waste, but usable if you only use a strip region.

- **product_entity["turn0product2","Capacitive Touch Overlay (for LattePanda display)"]** — overlay only (no display). You could adapt it to your dimensions or bend/trim carefully if its substrate allows.

- **product_entity["turn1product6","Capacitive Touch Panel with Controller"]** — a bare capacitive touch panel + controller. If its dimensions are closer, it might be feasible.

- **product_entity["turn1product10","EastRising Capacitive Touch Panel"]** — cheap option; you'd need to check its active area dimensions.

- **product_entity["turn1product4","7-inch Capacitive Digitizer Glass"]** — purely sensor glass; gives flexibility to combine with your own display or backing.

- **product_entity["turn1product12","Waveshare 7.9\" Capacitive LCD"]** — has a display + touch; you could restrict to a vertical strip region.

- **product_entity["turn1product7","Capacitive Touch Display Module"]** — full module; likely has more “bulk” than you want, but might work if placed appropriately.

---

## 🔍 Other smaller / linear options

- **Capacitive Touch Slider Wireling (TinyCircuits)** — this is ~10 mm × 80 mm. Too short for what you want, but good example of a 1D capacitive slider. citeturn0search0  
- You might also consider *capacitive slider modules* rather than full 2D touch panels; these are essentially 1D touch strips.  
- Some companies that produce custom touch sensors (e.g. *Zytronic*, *Orient Display*, etc.) can make glass touch panels to custom shapes. Zytronic is known for projected capacitive sensor tech. citeturn0search15  

---

## ⚠️ Tradeoffs & what to watch out for

- **Resolution & sensitivity along the strip**: If your strip is narrow, you’ll want sufficiently dense electrodes so the touch resolution (say sub-millimeter) is good.
- **Edge effects & bleed**: Many panels are designed for full-surface use. If you rely only on a strip, the parts you don’t use might “interfere” unless masked or electrically isolated.
- **Cutting / trimming**: Glass or capacitive sensor glass is delicate. Trimming or cutting can break the sensor traces. Overlays or flexible foils are safer to trim.
- **Controller compatibility**: Make sure the panel’s touch controller (I²C, SPI, USB, etc.) is something your system can interface with.
- **Aspect ratio compromise**: Using part of a larger panel or masking will reduce effective area and might degrade linearity near edges.

---

If you like, I can filter the above list to ones that ship to the UK and are *closest* (within, say, ±10 mm) to your target 50×150 mm, and send you direct product links. Do you want me to find those?

## User · 2025-10-10 10:45

Ok what about 1600 x 600 pixels 

## Assistant · 2025-10-10 10:45

Yes — there *is* at least one off-the-shelf capacitive touch display with **1600×600 px**:

- **Waveshare 9.3-inch Capacitive Touch Display, 1600×600** — IPS panel, 10-point capacitive touch. citeturn0search0turn0search3turn0search4  
  - Its overall dimensions are 239 × 94 mm (touch dimensions) citeturn0search3  
  - Display area is ~231 × 89 mm (active) citeturn0search3  
  - It uses HDMI for video + USB Type-C for touch. citeturn0search5turn0search4  

As a concrete product you can order:  
**product_entity["turn0product0","Waveshare 9.3″ 1600×600 Capacitive Touch Display"]**

---

### 🔍 How “close” is this to your ~5×15 cm target?

- The panel is significantly wider than you want (239 mm wide vs your 150 mm target), and taller (94 mm vs your 50 mm target). citeturn0search3  
- But you could consider using only a **strip / subset region** of that panel (i.e. crop to your 50×150 mm region), letting the rest of the touch area be inactive or masked.  
- The touch resolution (1600 px wide) gives a good density: you’d get ~10.7 px/mm horizontally (if you used full width). If you restrict to 150 mm region, you still have ~1600 * (150/239) ≈ 1005 px across your active strip — more than enough for smooth control.

---

### ⚠️ Caveats & considerations

- The panel is wide (landscape orientation). If you want a **vertical** strip (i.e. tall relative to width), you’d need to rotate orientation or reconfigure the touch driver.  
- Using only part of the panel means you must remap the touch coordinates so that only the strip region is active (i.e. ignore touches outside the desired region).  
- Edge effects: the unused portion might still respond to touches unless properly masked or disabled.  
- The height (94 mm) is nearly twice your desired 50 mm — you'd need to mask or frame it so only the central strip is usable.  
- The driver & firmware must allow you to remap / calibrate to a cut region.

---

If you like, I can search for displays with **exactly ~1600×600** or **very elongated aspect ratios** (say 3:1 or 4:1) that are *physically* closer to your 50×150 mm target, and find ones that ship to the UK. Do you want me to look those up?

## User · 2025-10-10 10:46

Ok look for similar 

## Assistant · 2025-10-10 10:46

I found at least one display that *exactly* matches **1600×600 px** (with touch) and several more conventional touch panels. None are perfect 50×150 mm strips, but you could use parts of them (crop / mask). Here are some options + how usable they might be:

  
---

## ✅ Close match: 1600×600 display

products{"selections":[["turn0product0","Waveshare 9.3″ 1600×600 Capacitive Touch Display"]],"tags":["exact-match resolution"]}  

- **product_entity["turn0product0","Waveshare 9.3″ 1600×600 Capacitive Touch Display"]** — this is a 9.3-inch IPS display with 1600×600 resolution and 10-point capacitive touch. citeturn0search0turn0search3turn0search5  
  - Physical dimensions: the touch panel is about **239 × 94 mm** (H × V) citeturn0search3  
  - Active/display area: ~231 × 89 mm citeturn0search3  
  - You could carve out a 50×150 mm strip from that, or mask off unused regions.

This one is your best “off-the-shelf” match for resolution + touch. But the physical size is much larger than your target strip, so you'll have to **use only part of it** (i.e. remap touch region).

---

## ⚡ Other conventional touch panels (less exotic)

Here are some typical touch displays (with more standard resolutions) you might also consider. They won't give you 1600×600, but may be easier to source or integrate, especially if you're okay using sub-regions.

products{"selections":[["turn0product12","10.1″ Capacitive Touch Display"]],"tags":["standard small display"]}  

- **product_entity["turn0product12","10.1″ Capacitive Touch Display"]** — a 10.1″ capacitive touch module, commonly used with Raspberry Pi / embedded systems.  
- (Other panels in the search results are large monitors / touch screens, less useful for your strip use case.)

---

## 🔍 Summary & tradeoffs

- The **Waveshare 9.3″ 1600×600** is the only one I found that meets your requested resolution exactly. Good for full-surface use or cropping.  
- But it’s large, so your “strip” would occupy only a portion of it (i.e. you’ll need to **remap** the touch region and possibly **mask off** the unused parts.  
- The other panels are more conventional in shape and likely easier to mount, but they lack the elongated resolution you desired.

---

If you like, I can try to find more *elongated* touch panels (e.g. 1600×600, or other “wide & narrow” formats) in the UK / Europe that ship reasonably. Want me to search UK-stock elongated touch panels?

