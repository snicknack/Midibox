# MidiBox service

One process for the whole box, and the box's link to PatchSYS. Lives at
`~/midibox/service/` on the Pi (this folder is the copy in the repo).

```
sudo python3 -m service.midibox_service                 # everything, talking to PatchSYS
sudo python3 -m service.midibox_service --no-link       # devices only; prints what it would send
python3 -m service.midibox_service --no-hw --selftest --seconds 4   # no hardware, synthetic events
sudo python3 -m service.midibox_service --only encoders,leds,haptics --no-link
```

`sudo` is for the NeoPixels (DMA) as before. Run from `~/midibox` so the
existing drivers import (`midio/`, `drivers/faders/`, `config/`).

To keep it running in the background for a session:
`cd ~/midibox && nohup sudo python3 -m service.midibox_service > service.log 2>&1 &`
and `sudo pkill -f service.midibox_service` to stop it. `midibox.service` is a
systemd unit for later (`sudo cp service/midibox.service /etc/systemd/system/
&& sudo systemctl daemon-reload && sudo systemctl start midibox`; add
`enable` for start at boot; logs with `journalctl -u midibox -f`).

## What goes where

| Control | PatchSYS | Screen | Other |
|---|---|---|---|
| Encoders 1–4, bank A | Filter Attack, Filter Release, Cutoff, Resonance (`set_parameter`) | arcs 1–4 | |
| Encoders 1–4, bank B | Balance, Env Amount, Movement, Movement Speed | arcs 1–4 (same labels) | |
| Arc1 press, short | | | bank A ⇄ B, ring flashes white |
| Arc1 press, long (0.7 s) | | | SuperCore mode cycle |
| SuperCore turn, TEMPO mode (cyan ring) | `tempo` action, 20–200 BPM | tempo arc | tick per detent, bump at the ends |
| SuperCore turn, DEPTH mode (amber ring) | `set_depth` action, 0–100 | | |
| Arc touched on screen | same control as its encoder | | |
| Pitch / mod wheels | | pitch and mod bars | MIDI pitch bend / CC1 on "Midibox Controls", wheel pixels |
| Faders 1 / 2 | Balance / Movement (`set_parameter`), configurable in `faders.targets` | arcs when bank B is up | MIDI CC 7 / CC 74 as well |

PatchSYS's confirmed values come back over the Link and move the arcs, so the
screen follows the app after a Generate or an Undo. A value we are turning is
protected for 300 ms so feedback never fights the hand.

With the V4 sketch flashed (`esp32/arduino/lvgl_hello_gui_SL_V4_patchsys`), the
service also drives the PatchSYS page: link state, target and sound names,
the four control names of the current bank, the SuperCore mode and value, and
it brings that page up when PatchSYS first comes online. The page's GEN, VARY
and UNDO buttons become Link actions; BANK and MODE do what the encoder
presses do. On the V3 sketch these extra messages are answered with
`{"err":"unknown"}` and ignored.

If the SuperCore's own push switch (SX1509 P14) proves stable, set
`"press_pin": 14, "press_button": "supercore"` in `config.json`: then a short
press cycles the mode and a long press asks PatchSYS for a VARIATION, and the
Arc1 button is free again.

## PatchSYS side

Nothing to install. PatchSYS Surface (the current app; Development too) starts
its Link on port 39276 when it opens (`PATCHSYS_REMOTE_LINK` not set to 0). The service connects to
`Stephens-Mac-mini-3068.local`; change `link.host` in `config.json` for another
Mac. The target must be ONLINE in PatchSYS (a synth loaded, not busy) before
writes are accepted; until then the service keeps the newest knob values and
sends them when the app comes back.

For a bench test without PatchSYS, run the stand-in on the Mac:
`cd ~/PatchSYS && PYTHONPATH=src .venv/bin/python ~/MidiBox/tools/link_standin.py`.

## LEDs

Both strips are driven from one `rpi_ws281x` instance (channel 0 wheel pixels
on GPIO18, channel 1 ring on GPIO13), because two strip objects cannot share
the Pi's PWM/DMA block. The ring's wire order is set as `SK6812_STRIP_RGBW`,
which matches how the ring behaved in the test scripts; if cyan comes out as
something else, change `leds.ring.strip_type` to `SK6812_STRIP_GRBW`.
