"""Thin wrappers over the drivers that already work on the Pi, so the service can run
with any of them missing. Nothing in here changes the drivers' behaviour.

Encoders  midio/encoders_sx1509_poll3.py  (SX1509 0x3E, polling, one press pin)
Wheels    midio/ads1115_reader.py         (ADS1115 0x48, A0 pitch, A1 mod) + ads1115_cal.json
Faders    drivers/faders/infinium_x1_serial.py (two Infinium X1 on ttyAMA2/3) + calibration.json
LEDs      one rpi_ws281x instance for both strips: wheel pixels on GPIO18 (PWM0) and the
          SuperCore ring on GPIO13 (PWM1). Two separate strips cannot share the PWM block.
Haptics   DRV2605L 0x5A through adafruit_drv2605, in ERM mode as fitted today.
ESP       /dev/serial0 115200: ``name:value\\n`` out, JSON lines in.
MIDI      a virtual ALSA port through mido.
"""

from __future__ import annotations

import json
import logging
import os
import time

LOGGER = logging.getLogger("midibox.hw")


def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as error:
        LOGGER.warning("could not read %s: %s", path, error)
        return {}


class Encoders:
    """poll3 rows become ('turn', index, delta) and ('press', pressed_bool) events."""

    def __init__(self, cfg):
        from midio.encoders_sx1509_poll3 import SX1509Encoders
        pairs = [tuple(pair) for pair in cfg.get("pairs", [[0, 1], [3, 4], [6, 7], [9, 10], [12, 13]])]
        press_pin = cfg.get("press_pin", 2)
        self.driver = SX1509Encoders(
            addr=int(cfg.get("addr", 0x3E)), pairs=pairs, poll_hz=int(cfg.get("poll_hz", 500)),
            arc1_press_pin=press_pin, use_hw_debounce=True, debounce_code=0b100,
        ).begin()
        self.press_button = str(cfg.get("press_button", "arc1"))

    def read(self):
        events = []
        for index, delta, pressed in self.driver.read_and_zero():
            if delta:
                events.append(("turn", index, int(delta)))
            else:
                events.append(("press", self.press_button, bool(pressed)))
        return events

    def close(self):
        self.driver.close()


class Wheels:
    """Pitch and mod wheels through the ADS1115, calibrated in CC units like the wheel reader."""

    def __init__(self, cfg, root):
        from midio.ads1115_reader import ADS1115Reader
        self.reader = ADS1115Reader(address=int(cfg.get("addr", 0x48)))
        cal = _load_json(os.path.join(root, cfg.get("cal_path", "config/ads1115_cal.json")))
        self.pitch = cal.get("0", {"min": 0, "max": 127})
        self.mod = cal.get("1", {"min": 0, "max": 127})
        self.alpha = float(cfg.get("alpha", 0.7))
        self.last01 = [0.5, 0.0]
        self.last7 = [None, None]

    @staticmethod
    def _to01(value, cal):
        lo, hi = float(cal.get("min", 0)), float(cal.get("max", 127))
        if hi <= lo:
            return 0.0
        x = max(0.0, min(1.0, (value - lo) / (hi - lo)))
        return 1.0 - x if cal.get("invert") else x

    def read(self):
        """-> list of ('pitch'|'mod', value01, value7) for the wheels that moved past their deadband."""
        cc = self.reader.read_cc()
        out = []
        for index, (name, cal) in enumerate((("pitch", self.pitch), ("mod", self.mod))):
            x = self._to01(cc[index], cal)
            x = (1.0 - self.alpha) * self.last01[index] + self.alpha * x
            self.last01[index] = x
            value7 = int(x * 127 + 0.5)
            dead = int(cal.get("deadband", 1))
            if self.last7[index] is None or abs(value7 - self.last7[index]) >= dead:
                self.last7[index] = value7
                out.append((name, x, value7))
        return out


class Faders:
    """Two Behringer Infinium X1 faders; values scaled by calibration.json when it has a range."""

    def __init__(self, cfg, root):
        from drivers.faders.infinium_x1_serial import (
            CurveConfig, FilterConfig, GestureConfig, InfiniumSerialConfig, InfiniumX1Serial,
            MappingLayers, PickupConfig, SerialConfig,
        )
        cal = _load_json(os.path.join(root, cfg.get("cal_path", "config/calibration.json")))
        self.faders = []
        for number, port in enumerate(cfg.get("ports", ["/dev/ttyAMA2", "/dev/ttyAMA3"]), start=1):
            config = InfiniumSerialConfig(
                serial=SerialConfig(port=port, baud=31250, timeout=0.001),
                filters=FilterConfig(smoothing_ms=6, rate_hz=500),
                curve=CurveConfig(kind="linear"),
                pickup=PickupConfig(enabled=False),
                gesture=GestureConfig(velocity_scale=0.0, accel_scale=0.0),
                fourteen_bit=False, midi_channel=1,
                layers=MappingLayers(pages={"A": {"cc": 74}}, default_page="A"),
                prefer_pitchbend=False, learn_cc=None,
            )
            try:
                driver = InfiniumX1Serial(config)
            except Exception as error:
                LOGGER.warning("fader %d on %s unavailable: %s", number, port, error)
                driver = None
            span = cal.get(f"fader{number}", {})
            lo, hi = float(span.get("min", 0.0)), float(span.get("max", 0.0))
            self.faders.append({"driver": driver, "lo": lo, "hi": hi, "last": None})

    def read(self):
        """-> list of (fader_index, value01, value7) for faders whose 7-bit value changed."""
        out = []
        for index, fader in enumerate(self.faders):
            driver = fader["driver"]
            if driver is None:
                continue
            try:
                event = driver.process()
            except Exception as error:
                LOGGER.debug("fader %d read failed: %s", index + 1, error)
                continue
            norm = float(event.get("norm", 0.0)) if isinstance(event, dict) else 0.0
            lo, hi = fader["lo"], fader["hi"]
            if hi > lo + 1e-6:
                norm = max(0.0, min(1.0, (norm - lo) / (hi - lo)))
            value7 = int(round(norm * 127))
            last = fader["last"]
            # the Infinium stream wobbles by a step at rest: move on 2 steps, or when an end is reached
            if last is None or abs(value7 - last) >= 2 or (value7 in (0, 127) and value7 != last):
                fader["last"] = value7
                out.append((index, norm, value7))
        return out


class Leds:
    """Both strips from one rpi_ws281x instance: channel 0 = wheel pixels, channel 1 = ring."""

    def __init__(self, cfg):
        from rpi_ws281x import PixelStrip, ws
        wheels = cfg.get("wheels", {})
        ring = cfg.get("ring", {})
        self.ws = ws
        self.strip = PixelStrip(
            int(wheels.get("count", 2)), int(wheels.get("pin", 18)), 800000, int(cfg.get("dma", 10)),
            False, int(wheels.get("brightness", 255)), 0,
            getattr(ws, wheels.get("strip_type", "WS2811_STRIP_GRB")),
        )
        self.ring_count = int(ring.get("count", 12))
        self.ring_channel = ws.ws2811_channel_get(self.strip._leds, 1)
        ws.ws2811_channel_t_count_set(self.ring_channel, self.ring_count)
        ws.ws2811_channel_t_gpionum_set(self.ring_channel, int(ring.get("pin", 13)))
        ws.ws2811_channel_t_invert_set(self.ring_channel, 0)
        ws.ws2811_channel_t_brightness_set(self.ring_channel, int(ring.get("brightness", 12)))
        ws.ws2811_channel_t_strip_type_set(self.ring_channel, getattr(ws, ring.get("strip_type", "SK6812_STRIP_RGBW")))
        self.strip.begin()
        self.top_offset = int(ring.get("top_offset", 0)) % max(1, self.ring_count)
        self.mode_colors = {name: tuple(rgbw) for name, rgbw in ring.get("mode_colors", {}).items()}
        self.bank_flash = tuple(ring.get("bank_flash", [0, 0, 0, 160]))
        self.flash_until = 0.0
        self.ring_fill = (0, 0, 0, 0)
        self.ring_lit = 0

    @staticmethod
    def _pack(r, g, b, w=0):
        return (int(w) << 24) | (int(r) << 16) | (int(g) << 8) | int(b)

    def wheels(self, pitch7, mod01):
        """pixel 0: pitch, green up / red down, brighter away from centre; pixel 1: mod, blue."""
        diff = pitch7 - 64
        bright = int(abs(diff) / 63 * 255)
        r, g = (0, bright) if diff > 0 else ((bright, 0) if diff < 0 else (0, 0))
        self.strip.setPixelColor(0, self._pack(r, g, 0))
        self.strip.setPixelColor(1, self._pack(0, 0, int(40 + 215 * max(0.0, min(1.0, mod01)))))
        self.strip.show()

    def ring(self, fraction, color):
        """A bar of the ring, pixel 0 at 12 o'clock through top_offset."""
        lit = max(0, min(self.ring_count, int(round(fraction * self.ring_count))))
        now = time.monotonic()
        fill = self.bank_flash if now < self.flash_until else tuple(color)
        if (fill, lit) == (self.ring_fill, self.ring_lit) and now >= self.flash_until:
            return
        self.ring_fill, self.ring_lit = fill, lit
        for index in range(self.ring_count):
            on = index < lit
            self.ws.ws2811_led_set(self.ring_channel, (index + self.top_offset) % self.ring_count,
                                   self._pack(*fill) if on else 0)
        self.strip.show()

    def flash(self, seconds=0.15):
        self.flash_until = time.monotonic() + seconds
        self.ring_lit = -1  # force a redraw

    def clear(self):
        for index in range(self.ring_count):
            self.ws.ws2811_led_set(self.ring_channel, index, 0)
        self.strip.setPixelColor(0, 0)
        self.strip.setPixelColor(1, 0)
        self.strip.show()


class Haptics:
    """DRV2605L effects: 1 sharp click (tick), 15 double strong click (confirm), 11 strong click (end stop)."""

    def __init__(self, cfg):
        import board
        import busio
        import adafruit_drv2605 as drv
        self.drv = drv
        self.device = drv.DRV2605(busio.I2C(board.SCL, board.SDA), address=int(cfg.get("addr", 0x5A)))
        if str(cfg.get("motor", "erm")).lower() == "lra":
            (getattr(self.device, "use_LRM", None) or getattr(self.device, "use_LRA"))()
            self.device.library = 6
        else:
            self.device.use_ERM()
            self.device.library = 1
        self.tick_interval = float(cfg.get("tick_interval_s", 0.012))
        self._last_tick = 0.0

    def _play(self, *effects):
        slot = 0
        for effect in effects:
            self.device.sequence[slot] = self.drv.Effect(effect) if effect > 0 else self.drv.Pause(-effect)
            slot += 1
        for index in range(slot, 8):
            self.device.sequence[index] = self.drv.Pause(0)
        self.device.play()

    def tick(self):
        now = time.monotonic()
        if now - self._last_tick < self.tick_interval:
            return
        self._last_tick = now
        self._play(1)

    def confirm(self):
        self._play(15)

    def endstop(self):
        self._play(11, -10, 11)


class Esp:
    """The ESP32 screen link on the Pi's UART."""

    def __init__(self, cfg):
        import serial
        self.serial = serial.Serial(cfg.get("port", "/dev/serial0"), int(cfg.get("baud", 115200)), timeout=0)
        self.buffer = b""
        self.sent = 0

    def send(self, name, value):
        try:
            self.serial.write(f"{name}:{int(value)}\n".encode("ascii"))
            self.sent += 1
        except Exception as error:
            LOGGER.debug("esp write failed: %s", error)

    def poll(self):
        """-> list of dicts for JSON lines from the screen (get/set/err), newest last."""
        try:
            data = self.serial.read(4096)
        except Exception:
            return []
        if not data:
            return []
        self.buffer += data
        out = []
        while b"\n" in self.buffer:
            line, self.buffer = self.buffer.split(b"\n", 1)
            line = line.strip()
            if not line.startswith(b"{"):
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
        if len(self.buffer) > 4096:
            self.buffer = b""
        return out


class MidiOut:
    def __init__(self, cfg):
        import mido
        self.port = mido.open_output(str(cfg.get("port_name", "Midibox Controls")), virtual=True)
        self.channel = max(0, min(15, int(cfg.get("channel", 1)) - 1))
        self.mido = mido

    def cc(self, control, value):
        self.port.send(self.mido.Message("control_change", channel=self.channel, control=int(control), value=int(value)))

    def pitch(self, value01):
        self.port.send(self.mido.Message("pitchwheel", channel=self.channel, pitch=int(value01 * 16383) - 8192))
