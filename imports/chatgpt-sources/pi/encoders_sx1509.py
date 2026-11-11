# midibox/io/encoders_sx1509.py
import threading
import time
from .sx1509 import SX1509
import RPi.GPIO as GPIO
from collections import deque

# 2-bit quadrature lookup (prev<<2 | now) -> -1/0/+1
_Q = {
    0b0001:+1, 0b0011:+1, 0b0110:+1, 0b0100:+1,
    0b0010:-1, 0b0111:-1, 0b1110:-1, 0b1100:-1,
}

class SX1509Encoders:
    def __init__(self, address=0x3E, i2c_bus=1, int_gpio=22, rst_gpio=None, enc_maps=None):
        """
        enc_maps: list of dicts: {"name":"ENC1","a":0,"b":1,"sw":2}
                  pins are SX1509 P# indices (0..15)
        """
        if enc_maps is None:
            enc_maps = [
                {"name":"ENC1","a":0,"b":1,"sw":2},
                {"name":"ENC2","a":3,"b":4,"sw":5},
                {"name":"ENC3","a":6,"b":7,"sw":8},
                {"name":"ENC4","a":9,"b":10,"sw":11},
            ]
        self.ic = SX1509(i2c_bus=i2c_bus, address=address, rst_gpio=rst_gpio)
        self.int_gpio = int_gpio
        self.encs = []
        for e in enc_maps:
            self.encs.append({
                "name": e["name"],
                "a": e["a"], "b": e["b"], "sw": e["sw"],
                "state": 0, "count": 0, "pressed": False, "last_sw": 1
            })
        self._configure_ic()
        self._configure_irq()

    def _pinmask(self, pins):
        m = 0
        for p in pins: m |= (1<<p)
        return m

    def _configure_ic(self):
        # Inputs on all encoder pins; pull-ups + debounce; both-edge on A/B, falling-edge on SW
        pins = []
        for e in self.encs: pins += [e["a"], e["b"], e["sw"]]
        mask = self._pinmask(pins)

        self.ic.set_dir_inputs(mask)                 # 1=input
        self.ic.enable_pullups(mask)                 # pull-ups on
        self.ic.disable_input_buffer(0x0000)         # keep input buffers enabled
        # Edge sense
        ab_mask = self._pinmask([p for e in self.encs for p in (e["a"], e["b"])])
        sw_mask = self._pinmask([e["sw"] for e in self.encs])

        self.ic.set_edge_sense(rising_mask := (ab_mask | 0), falling_mask := (ab_mask | sw_mask))
        # Debounce (~2ms) on all pins
        self.ic.set_debounce(mask, time_sel=0b100)
        # Unmask interrupts (enable) on these pins
        self.ic.set_interrupt_mask(~mask & 0xFFFF)
        # Prime states
        port = self.ic.read_inputs()
        for e in self.encs:
            e["state"] = ((port>>e["a"]) & 1) | (((port>>e["b"]) & 1)<<1)
            e["last_sw"] = (port>>e["sw"]) & 1

    def _configure_irq(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.int_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setwarnings(False)
        # GPIO.add_event_detect(self.int_gpio, GPIO.FALLING, callback=self._irq, bouncetime=1)

    def _irq(self, ch):
        port = self.ic.read_inputs()     # read clears IRQ
        self.ic.clear_interrupts()

        for e in self.encs:
            a = (port>>e["a"]) & 1
            b = (port>>e["b"]) & 1
            now = (a | (b<<1))
            delta = _Q.get((e["state"]<<2) | now, 0)
            if delta:
                e["count"] += delta
                # Here you could publish an event into your Midibox bus
                # e.g., self.on_step(e["name"], delta)
            e["state"] = now

            sw = (port>>e["sw"]) & 1
            if sw != e["last_sw"]:
                e["pressed"] = (sw == 0)
                # publish press/release as needed
                e["last_sw"] = sw

    # Poll counts (atomic enough for GUI/audio loop)
    def read_and_zero(self):
        out = []
        for e in self.encs:
            c = e["count"]; e["count"] = 0
            out.append((e["name"], c, e["pressed"]))
        return out
