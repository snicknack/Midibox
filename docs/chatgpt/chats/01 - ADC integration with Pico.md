# ADC integration with Pico

- ChatGPT conversation id: 68e12d99-2480-832f-a712-d6ce782fdd43
- Created: 2025-10-04 14:22
- Updated: 2026-11-11 18:54
- Project: Midibox raspberry pi
- Messages: 4

## User · 2025-10-04 14:22

So finding these FFC/FPC breakouts on Amazon, and a pick pi on order what would it take to provide the adc of the keyboard into the pick

## Assistant · 2025-10-04 14:22

Got it — since you’ve got FFC/FPC breakouts on the way and a **Raspberry Pi Pico (RP2040)** (“pick pi”) on order, here’s a concrete, no-nonsense path to feed the keyboard’s analog signals (e.g., aftertouch / pressure) into the Pico and then up to the main Pi over USB-MIDI.

If you meant a different micro (not the Pico), the same architecture applies—just swap pin names and ADC specs.

---

# What it takes (electrical + firmware)

## 1) Identify which ribbon lines are truly analog
- **Likely analog**: aftertouch/pressure strip(s) or zone taps. These behave like **FSR** (variable resistance with force) or a resistive ladder.
- **Likely digital**: key contacts/rows/columns (scanned matrix for note on/off/velocity via time delta).
- Quick test now: with the keyboard powered **off**, meter between suspected AT line and GND. Press a few keys—if the resistance drops as you push, that’s your analog pressure line (or a per-zone tap).

## 2) Front-end for the Pico ADC (3.3 V domain)
The Pico’s ADC is 12-bit, ~500 kS/s, and wants **low source impedance** (<5 kΩ) for best accuracy.

**Single aftertouch strip (mono AT, one channel):**
- Make a simple divider:
  - 3.3 V → 10 k → (node to ADC) → FSR → GND
- Buffer the ADC node with a **rail-to-rail op-amp** (e.g., MCP6002, TLV9052). Put a **100 Ω** series resistor into the ADC pin and a **100 nF** to ground at the ADC pin (RC ~10 µs anti-alias + sample-hold help).
- Add **ESD/over-voltage protection**: a small TVS or a 3.6 V clamp to 3.3 V rail + 100 Ω series is usually enough.

**Polyphonic/zonal aftertouch (many channels):**
- Use **analog multiplexers** to fan many channels into **one buffered ADC**:
  - 16-to-1 mux: **CD74HC4067** (3.3 V powered)
  - Or 8-to-1 mux: **CD4051B** (3.3 V powered)
- Each sensor line → mux input. Mux output → **op-amp buffer** → ADC.
- Keep each sensor’s source impedance reasonable; if the sensors are high-Z, consider **per-channel series 47–100 k** into the mux and rely on the post-mux op-amp.
- Put **100 nF** from mux output to ground (post-mux, pre-buffer). After switching the mux channel, wait **2–5 µs** for the node to settle before sampling.

> Throughput sanity check:  
> 88 channels × 1 kHz updates = **88 kS/s**, which the RP2040’s ADC can handle (500 kS/s typical). Budget a few µs for mux settle + sample time and you’re fine. If you only need 250–500 Hz per channel, you’ve got loads of headroom.

**External precision option (if you want higher resolution / cleaner ref):**
- The **ADS1115** you mentioned is super easy but **too slow** for lots of channels (max ~860 S/s *shared*). It’s great for 1–4 slow channels, not for 88.  
- If you want SPI multi-channel speed at 12–16-bit: **MCP3208/3008 (12-bit)** or **AD7689 (16-bit, 8-ch)**. You’d still mux if >8 channels.

## 3) Power, grounding, and reference
- Give the analog side a **quiet 3.3 V**: LDO + ferrite bead from your 5 V, then split **AGND** and **DGND** with a star point at the Pico ground.
- If you want better ADC stability, feed **ADC_VREF** on the Pico with a precision 3.0–3.3 V reference (e.g., **REF3030**), and decouple it (1 µF + 100 nF close).
- Keep the FFC cable’s analog lines away from high-dI/dt digital lines; twist with ground where possible.

## 4) Firmware on the Pico (RP2040)
- Configure **GPIO** for mux select lines (4 lines for a 16:1).
- Scan loop:
  1. Set mux to channel n  
  2. `sleep_us(2–5)` for settle  
  3. Read ADC (maybe **average 4–8 samples** for noise)  
  4. Move to next channel
- Use a **timer/PIO** cadence to keep the scan rate steady (e.g., 500–1000 Hz per channel).
- Apply a light **IIR filter** per channel:
  ```
  y[n] = y[n-1] + α*(x[n] - y[n-1])   // α ~ 0.2–0.4
  ```
- Calibration: store min/max per channel on startup (or over a service command) to normalize 0–127 for MIDI.

## 5) Turning readings into MIDI
- **Mono aftertouch**: average across channels (or take max) → send **Channel Pressure** (0xD0) if you don’t need Poly AT.
- **Poly AT**: send **Polyphonic Key Pressure** (0xA0) per active note.  
  If you go full per-key AT, you’ll need a map from each sensor channel to its key number (and you’ll push a lot more MIDI data).
- Consider **MPE** if you want per-note expression via channels (more host setup, very flexible).
- The Pico can enumerate as a **USB-MIDI device** and plug directly to the Pi or Mac.

## 6) Key on/off and velocity (if you also bypass the STM32)
- Fatar beds often use **two contacts per key**; velocity is derived from the **time delta** between them closing.
- Treat those as **digital** inputs. Use Pico GPIO with pull-ups and timestamp the closures.  
- That’s parallel to the analog AT scanning and doesn’t load the ADC.

## 7) Minimum BOM (zonal/Poly AT example)
- 1× **Raspberry Pi Pico** (or Pico W), 3.3 V logic
- 6× **CD74HC4067** (for 96 inputs → plenty for 88 keys/zones) *or fewer if you’re doing fewer zones*
- 1× dual rail-to-rail **op-amp** (MCP6002/TLV9052) — one channel to buffer mux output; spare for future
- Passives: 10 k (dividers), 47–100 k (per-channel source limit), 100 Ω series to ADC, 100 nF caps (lots), 1 µF and 10 µF decoupling
- Optional: **REF3030** (or 3.3 V precision ref) to Pico’s ADC_VREF
- **TVS** or clamp diodes for ESD
- FFC/FPC **breakouts** that match your ribbon pitch (looks like you’ve got these)

## 8) Wiring tips from the FFC
- Bring **at least two grounds** from the keyboard ribbon to your analog ground on the breakout.
- If multiple analog lines run in the ribbon, interleave ground where possible on your breakouts/routing.
- Keep the **post-mux trace** short and guarded by ground; that node is sensitive.

---

# Quick “ASCII schematic” for one 16-channel block

```
[Sensor ch0]--47k--+ 
                    \ 
[Sensor ch1]--47k--- > CD74HC4067 IN0..IN15  ---o---- [100nF] --- GND
                    /                           |
[Sensor ch15]-47k--+                           [Op-Amp Buffer] ---> 100Ω ---> Pico ADC0
                                                |
                                               GND

Pico GPIOs --> MUX S0..S3
3.3V ---- LDO/Bead ----> Analog 3.3V
Analog 3.3V -> (op-amp Vcc), MUX Vcc
Pico ADC_VREF <- optional REF3030 (with 100nF + 1µF)
```

---

# Software drop points in your repo
When you’re ready, we can add:
- `/Users/stephennicholson/Midibox/firmware/pico/at_scan/`
  - `main.c` or `main.py` (Pico SDK or MicroPython)
  - `mux.h/.c` (select logic)
  - `adc.c` (calibration, filtering)
  - `midi_usb.c` (USB-MIDI, Mono/Poly AT, optional MPE)
- A tiny Python util on the Pi to read the Pico over USB and bridge to ALSA MIDI if you want routing control.

---

## TL;DR
Use **Pico ADC + analog muxes + op-amp buffer** to scan aftertouch/pressure channels from the FFC breakouts. Protect and filter the inputs, keep analog power quiet, scan at ~500–1000 Hz per channel, normalize, and spit out **USB-MIDI** (Channel Pressure or Poly AT). The ADS1115 you’ve got is fine for a **few** slow channels, but for 88-key poly you’ll want **mux + Pico ADC** (or a fast multi-channel SPI ADC).

If you can share a clear photo and pin count of the FFC(s), I’ll map channels and propose exact mux counts + pinout labels for you.

