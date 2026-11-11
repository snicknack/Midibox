# Pi5 eurorack synthesizer design

- ChatGPT conversation id: 68fa0223-0bf4-8326-95e4-7ca333ad5ed1
- Created: 2025-10-23 10:23
- Updated: 2026-10-08 06:51
- Project: outside Midibox raspberry pi (shared link from Desktop/Links)
- Messages: 6

## User · 2025-10-23 10:23

I’m interested in building a pi5 eurorack synthesizer, it would be similar to the knobula monumatic but I would like it to have a daw vst interface

## Assistant · 2025-10-23 10:23

That’s a *brilliant* concept, Stephen — a **Raspberry Pi 5-powered Eurorack synth** with a **DAW-linked VST interface** would give you the tactile immediacy of modular *and* the recall, automation, and plugin convenience of modern production.  
Let’s sketch out what a solid architecture for that could look like 👇

---

## 🧠 Core Concept

Think of it as a **hybrid digital module**:
- **Front-end (hardware):** A Eurorack-sized control surface with encoders, faders, CV ins/outs, OLED/TFT display, maybe MIDI/CV bridge.  
- **Engine (Pi 5):** Runs Linux-based synth engines (e.g., custom JUCE app, LV2 plugins, or Python/C++ DSP code).  
- **Back-end (plugin bridge):** A VST3/AU plugin in your DAW that communicates bi-directionally with the Pi over network or USB, so it feels like a native instrument.

This is very doable with the Pi 5 — it has the horsepower for low-latency DSP and OpenGL GUIs.

---

## ⚙️ System Architecture

| Layer | Role | Example Tech |
|-------|------|---------------|
| **Hardware I/O** | Encoders, pots, CV I/O, gate triggers, displays | STM32/Pico microcontroller via I²C/SPI/USB |
| **Synth Engine (Pi 5)** | Core DSP (oscillators, envelopes, filters) | JUCE C++ app, SuperCollider, VCV Rack SDK module, or custom LV2 |
| **Audio Interface** | CV/audio conversion | HiFiBerry DAC+ ADC Pro or USB audio interface |
| **VST/AU Bridge Plugin** | GUI + control sync | Custom JUCE VST3 plugin (communicates via TCP/WebSocket/MIDI-over-USB) |
| **Networking Layer** | DAW ↔ Pi communication | OSC, RTP-MIDI, or custom JSON over WebSocket |
| **CV/Mod Matrix** | Mod routing, parameter mapping | JSON config or Lua scripts |

---

## 🧩 Workflow Example

1. **In your DAW**  
   Load the *Holson PiSynth* VST. It exposes parameters like *osc shape*, *filter cutoff*, *env attack*, etc.  
   → When you tweak a knob on the Pi’s Eurorack panel, the VST automation lane moves.

2. **On the Eurorack module**  
   The Pi runs your DSP engine standalone, processing audio locally (or returning it via USB).  
   It syncs clock and state with the VST through OSC or MIDI NRPNs.

3. **Result:**  
   - Tactile modular experience  
   - Full DAW automation + preset recall  
   - Expandable DSP core (swap engines, load different synth models)

---

## 🔌 Possible Hardware Stack

| Component | Suggested Part |
|------------|----------------|
| CPU | **Raspberry Pi 5 (8 GB)** |
| Audio | **HiFiBerry DAC+ ADC Pro** or **Audio Injector Ultra** |
| Control MCU | **Raspberry Pi Pico W** or **STM32F4** for high-speed knob scanning |
| Screen | **2.8-inch ILI9341** or **3.5-inch capacitive TFT** |
| CV interface | **Bela Mini** or **Expert Sleepers ES-8** (if you want ±10 V CV I/O) |
| Power | Eurorack ±12 V → 5 V DC-DC converter |
| Case depth | ≤ 45 mm for skiff-friendly build |

---

## 💻 Software Foundations

### On the Pi
- **Real-time kernel** (low-latency audio)
- **JUCE app** (your synth engine and local GUI)
- **OSC/WebSocket server** (to communicate with VST)
- Optional: **LV2 host** (to load other plugins inside the module)

### On the Computer (VST)
- **JUCE-based VST3/AU plugin**
  - Mirrors the parameters
  - Handles automation + preset management
  - Connects via IP or USB serial to the Pi
  - Optionally streams audio back for convenience

---

## 🧪 Next Steps

1. **Decide on the synth “voice”**  
   - Mono-synth like Knobula Monsoon → simple 1-voice subtractive  
   - Polyphonic digital engine (wavetable, FM, additive)  
   - Granular or sample-based (Pi 5 has power for that)

2. **Prototype control surface**  
   Use a Pico scanning your encoders + sliders and send MIDI CC/NRPN over USB to Pi.

3. **Build a JUCE template**  
   I can help you scaffold a pair:
   - `holson_module_engine` (Pi executable)
   - `holson_vst_bridge` (desktop plugin)

4. **Test round-trip latency + sync**  
   (Use RTP-MIDI or WebSocket loopback to ensure automation feels instant.)

---

If you like, I can **mock up a system diagram + folder structure** for the full project (hardware + software + VST bridge) — including how the Pi’s JUCE engine talks to the microcontroller and the DAW plugin.

Would you like me to draw that next?

## User · 2025-10-23 10:27

Great ideas! Other Things other devices don’t have 

Large polyphony/ multitimberal 
Direct computer access (midi class compliant) 
Automatable , pitch mod wheel cc response. 
Project recall 

Basically I wan to build it for powwwer lots of oscillators and voices !! 

## Assistant · 2025-10-23 10:27

Love it — let’s design this like a **power module**: tons of voices, multitimbral, class-compliant MIDI to the computer, fully automatable, with one-click project recall. Here’s a crisp blueprint you can build from.

# 🚀 High-Level Goal
A **Pi 5 Eurorack synth** that runs a **multitimbral, high-polyphony DSP engine** on-board, exposes **USB class-compliant MIDI** to a computer, mirrors every parameter in a **VST3 editor/bridge** for automation + preset recall, and optionally offers **CV I/O** for modular integration.

---

# 🧱 System Architecture (proven pattern)

**Front panel**
- 4–8 endless encoders w/ push, 2 faders, transport, small TFT/OLED.
- Optional: 4–8 CV ins (±10 V to 0–3.3 V via op-amp/precision attenuators) + 2–4 CV outs (via dedicated DAC or ES-8/ES-9).
- MCU (RP2040 or STM32F4/F7/H7) scans controls **and** acts as a **USB class-compliant MIDI device** to the computer.

**Pi 5 engine**
- Runs a low-latency audio stack (48 or 96 kHz, 64–128-sample buffer).
- DSP app in **JUCE** (or your C++ framework) = poly/multitimbral synth.
- Talks to the panel MCU over USB (CDC/serial or MIDI), and to the desktop **VST3** over **OSC/WebSocket/RTP-MIDI**.
- Stores/loads **Project** blobs for total recall.

**Desktop**
- **VST3/AU “Editor/Bridge”**: mirrors the module UI, automates every parameter, saves the full state inside DAW projects, pushes/recalls state to/from the Pi.

> Why the MCU as the USB device?  
> Pi 5’s USB device/gadget mode is awkward for a Eurorack product. A tiny MCU gives bulletproof **USB MIDI class compliance**, hot-plug reliability, and keeps Pi work focused on DSP.

---

# 🎹 Synth Engine: Polyphony & Multitimbrality (for real “powwwer”)

**Voice design (typical subtractive VA)**
- 2–3 band-limited oscillators (VA/wavetable), sub osc, noise
- 12/24 dB ladder or SVF filter
- 3 ADSR, 2 LFOs, mod matrix
- Per-voice drive + global FX (chorus/delay/verb)

**Scheduling**
- **N Parts (multitimbral)**, each bound to a MIDI channel.  
- Per-part **max_voices** (e.g., 8 parts × 16 voices = 128 voices).  
- Global **voice-stealing** (oldest-env-low-amp, or per-part priority).

**CPU budgeting on Pi 5 (rule-of-thumb)**
- Pi 5 (4× Cortex-A76 @ ~2.4 GHz) with NEON can realistically manage:
  - **64–128 VA voices @ 48 kHz** with modest FX, or
  - **32–64 voices @ 96 kHz** with heavier filters/FX,
  - **Hundreds** of simpler wavetable/FM voices (efficient ops).
- Use **SIMD/NEON**, **lookup BLEP/MIP-mapped wavetables**, and **shared modulation** where possible. Pin the audio thread to one core, workers to others.

**Audio I/O**
- If you need analog in the rack: HiFiBerry DAC+ADC Pro / Audio Injector / or ES-8/ES-9 for DC-coupled CV.  
- Purely “computer audio” use-case? Stream over your interface; keep module as a **sound source in the rack** and bring audio back via your regular studio chain.

---

# 🔌 Connectivity & Automation

**Direct computer access (class-compliant MIDI)**
- **Panel MCU presents as a USB MIDI device** (no drivers).  
- Host sees ports like:  
  - `Holson PiSynth [Panel]` (knobs, keyboard thru)  
  - `Holson PiSynth [Engine]` (Pi echoes engine parameters via RTP-MIDI/USB MIDI in)

**Automation, Pitch/Mod response**
- The **VST3** exposes all parameters and translates **DAW automation → Pi**.  
- Map **Pitch Bend**, **Mod Wheel (CC1)**, **Aftertouch** (channel & poly-AT/MPE if you want), **NRPN** for high-res.  
- Optional **MPE** mode per part.

**Clock & sync**
- MIDI Clock + Song Pos, or Ableton Link (on Pi), or DAW time over the plugin bridge.

---

# 💾 Project & Preset Recall (rock solid)

**State model**
- `Project` → multiple `Parts` → per-Part `Program` + FX + mixer.  
- JSON (versioned) for human-readable backups + a compact binary for fast load.
- Every load/save increments a `state_version` to avoid drift.

**Where it saves**
- DAW: the VST stores full engine state in the project file (total recall).  
- Pi: keeps a local library (`/home/pi/Holson/Projects/*.hproj`, `/Programs/*.hprog`).  
- **Push/Pull** from VST: “Store to Module” / “Recall from Module”.

---

# 🧪 Minimum Viable Path (fast to results)

**Phase 0 — Prove the polyphony**
1. Pi 5 + USB audio (or HAT), low-latency JACK/PipeWire.
2. JUCE synth with **64-voice wavetable** engine, simple ladder filter.
3. UDP **OSC** endpoint: `setParam(part, id, value)`, `noteOn/Off(part, ch, key, vel)`.
4. Basic front OLED + 4 encoders via Pico (USB MIDI → Pi).

**Phase 1 — VST3 bridge & recall**
1. JUCE VST3 that mirrors ~32 core params + program list.
2. Bi-dir state sync (push/pull JSON); parameter change coalescing.
3. Pitch bend, CC1/AT pass-through; DAW automation ↔ Pi round-trip.

**Phase 2 — Multi-part + voice manager**
1. 4–8 parts, per-part polyphony cap, priority stealing.
2. Per-part FX sends; master compressor/limiter (cheap + safe).

**Phase 3 — Performance + UX**
1. SIMD/NEON paths for oscillators/filters; lock-free param queues.
2. On-module preset browsing; quick layer/split per part.
3. Optional: MPE per part; per-voice modulation osc.

---

# 🧰 Concrete Tech Choices (drop-in)

- **DSP/GUI**: JUCE 7 app (Pi) + JUCE VST3 (desktop).
- **Transport**: OSC over UDP (low overhead) or WebSocket if you prefer structured JSON.
- **MIDI**:  
  - MCU → Computer: USB MIDI class-compliant (TinyUSB on RP2040 / STM32Cube).  
  - Computer → Pi: RTP-MIDI or route via the VST bridge.
- **Control MCU**: RP2040 (lots of IO + rock-solid USB). Scan encoders/faders, debounced, 1 kHz.
- **Storage**: LittleFS on MCU for panel prefs; ext4 on Pi for projects.
- **Power**: Eurorack ±12 V → 5 V buck (≥3 A for Pi spikes) + local filtering.

---

# 🎛️ Parameter Map (starter set)

**Per Part (exposed in VST & panel)**  
`osc1_wave, osc1_shape, osc1_level`  
`osc2_wave, detune, sync, ring`  
`sub_level, noise_level`  
`filter_type, cutoff, resonance, drive, keytrack`  
`env1(A,D,S,R), env2(A,D,S,R)`  
`lfo1(rate, shape, amt), lfo2(...)`  
`mod_matrix[x].src/dst/amt`  
`pan, level, out_bus, fx_send_chorus, fx_send_delay, fx_send_verb`  
`poly_limit, priority, mpe_mode`

**Global**  
`tempo, clock_src, link_enable, master_lim_th, project_name`

---

# 📦 Folder/Layout (ready for Git)

```
holson-pisynth/
  engine_pi/
    CMakeLists.txt
    src/
      audio/ (voices, osc, filter, fx, mixer)
      core/  (voice alloc, part, param store)
      io/    (midi, osc_server, rtp_midi)
      ui/    (local TFT/OLED, pages)
    resources/ (wavetables, factory presets)
  plugin_vst/
    CMakeLists.txt
    src/ (editor UI, net client, state)
  panel_mcu/
    src/ (enc scan, USB MIDI dev, param pages)
  tools/
    osc_cli.py
  presets/
    factory/
```

---

# 🔍 Practical polyphony tips

- Use **poly-BLEP** or **minBLEP** oscillators; precompute tables per pitch range.
- **Shared LFOs** per part when possible (per-voice only if audible).
- Vectorize envelopes & filters with NEON; keep denormals off.
- Run FX at half-rate where inaudible; oversample only where it pays (non-linear filter drive).
- Keep the audio thread lock-free; parameter updates via SPSC ring buffers.

---

# 🗺️ What I can deliver next
- A **JUCE starter** for both the **Pi engine** and the **VST3 bridge** (compiles out-of-the-box).  
- A **message schema** (OSC/JSON) and a tiny **RP2040 firmware** that shows up as **USB MIDI** and drives 4 encoders + OLED.  
- A **voice allocator** that scales to 8 parts × 16 voices with graceful stealing.

If you want, I’ll drop in a first cut of the **engine/VST skeleton** with 64-voice wavetable, 4 parts, CC1/pitch bend wired, and JSON project save/load — so you can hear the “powwwer” immediately and iterate from there.

