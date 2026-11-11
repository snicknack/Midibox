# Soft-touch coating options

- ChatGPT conversation id: 68e0a637-caa4-8333-adbf-825fc9ba204f
- Created: 2025-10-04 04:44
- Updated: 2025-10-04 04:46
- Project: Midibox raspberry pi
- Messages: 7

## User · 2025-10-04 04:44

If I 3d printed a case how could I get the finish on it that other manufacturers use such as maschine? It’s a bit like a rubber feel but it’s a coating 

## Tool (file_search) · 2025-10-04 04:44

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

## Tool (file_search) · 2025-10-04 04:44

All the files uploaded by the user have been fully loaded. Searching won't provide additional information.

## Assistant · 2025-10-04 04:44

Got it 👍 — you’re talking about the **“soft-touch rubberized” coating** that a lot of music hardware manufacturers (like Maschine, Ableton Push, Native Instruments keyboards) use. A raw 3D print, even smoothed, won’t have that finish on its own — you’ll need a **post-processing step**.  

Here are the main options:

---

### 1. **Soft-Touch Paint/Coating**
- Many manufacturers use a **urethane or silicone-based soft-touch paint** applied by spray.
- Available as **aerosol cans** (search for “soft-touch coating spray” or “rubberized spray finish”).
- Usually matte, with a slightly grippy/rubber feel.
- Needs good surface prep (sand + primer) and multiple light coats.

⚠️ Note: Some cheaper sprays can get tacky over time (especially in humid conditions). The higher-end industrial coatings (e.g. from **Sherwin-Williams or PlastiDip’s professional range**) hold up better.

---

### 2. **Plasti Dip (or similar rubberized sprays)**
- A popular DIY solution.
- Gives a matte, rubbery feel.
- Easy to re-coat or peel off if you mess up.
- Downsides: less durable than pro soft-touch paints, can wear shiny on heavy contact areas.

---

### 3. **Urethane/Rubber Overmolding (advanced)**
- Professional hardware often uses **injection-molded parts with overmolded TPE (thermoplastic elastomer)**.
- Hard to replicate at home, unless you want to 3D print a hard shell and then cast/silicone-mold a thin rubber skin.
- Great finish but more of a manufacturing process than DIY.

---

### 4. **Surface Prep First**
- No coating will look good unless the 3D print is **sanded and smoothed**:
  - Wet sand up to 400–600 grit.
  - Use a filler primer spray to even out layer lines.
  - Sand again before applying soft-touch coating.

---

✅ **Recommendation for your Midibox case (DIY level):**
- Sand + filler primer → sand again → matte black base coat → apply **soft-touch spray coating**.  
That’ll get you *very* close to the feel of Maschine/Push without factory tooling.

---

Would you like me to put together a **step-by-step guide (with product examples you can buy in the UK)** for finishing your 3D printed Midibox case in this soft-touch style?

## User · 2025-10-04 04:46

Yes

## Assistant · 2025-10-04 04:46

Perfect 👌 let’s build you a **DIY finishing workflow** for your 3D-printed Midibox case so it looks and feels closer to Native Instruments / Maschine hardware. I’ll keep it UK-friendly with products you can buy locally.

---

# 🎛 Soft-Touch Finish Guide for 3D-Printed Cases

### 🔧 Step 1 – Surface Prep
1. **Sand the print**
   - Start at **180–240 grit** to knock down layer lines.
   - Move up to **400–600 grit wet sanding** for a smooth surface.

2. **Fill & prime**
   - Use an **automotive filler primer spray** (Halfords Grey Plastic Primer works well).
   - 2–3 light coats, drying between each.
   - Sand again (600–800 grit wet) until the surface feels glassy smooth.

---

### 🎨 Step 2 – Base Coat
- Spray with a **matte black basecoat** (Halfords or Montana Black spray cans).
- This gives you the uniform colour under the soft-touch coat.
- Let it cure fully (at least overnight).

---

### 🖌 Step 3 – Soft-Touch Coating
You have two main DIY options:

#### Option A – **Soft-Touch Spray (closest to Maschine)**
- Search: **“Soft Touch Rubber Paint Spray”** (brands: *Sherwin-Williams*, *Eastwood*, *Rust-Oleum Soft Touch*).
- These give the same slightly rubberised, matte feel that NI uses.
- Apply 2–3 **very light coats**. Too thick = tacky feel.

#### Option B – **Plasti Dip (rubberised spray)**
- Widely available in UK (Amazon, Halfords).
- Matte, rubbery, removable if you want to retry.
- More forgiving than pro soft-touch sprays, but not quite as refined.
- Best if you want to experiment first.

---

### 🕑 Step 4 – Curing
- Let the coating cure for **24–48 hours** in a dust-free area.
- Don’t handle too soon, or you’ll leave shiny marks.

---

### 🛠 Step 5 – Protection (Optional)
- For extra durability, apply a **matte clear coat for soft-touch finishes** (Sherwin-Williams / Eastwood make these).
- Adds scratch resistance while keeping the rubbery feel.

---

# 🛒 Example Shopping List (UK)
- **Halfords Plastic Primer** (Grey filler primer spray)  
- **Halfords Matte Black Spray Paint** (base coat)  
- **Rust-Oleum Soft Touch Clear Spray** *(if you can find it in UK, otherwise Plasti Dip Matte Black)*  
- Wet/dry sandpaper set (180 → 800 grit)  
- Nitrile gloves + respirator mask (these coatings are solvent-based)  

---

👉 This workflow gives you something that feels **95% like a commercial controller**, without injection-moulding. If you want the *absolute pro finish*, you’d have to go into **urethane paint shops** (same coatings used on car interiors).  

---

Do you want me to sketch out a **timeline (like: Day 1 prep, Day 2 paint, Day 3 coating, Day 4 cure)** so you know exactly how long the finishing process will take before the Midibox case is usable?

