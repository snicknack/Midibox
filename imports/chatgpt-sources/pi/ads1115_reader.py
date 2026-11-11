# midibox/io/ads1115_reader.py
import time
import threading
import json
import os
from smbus2 import SMBus

# ADS1115 registers
_REG_CONV = 0x00
_REG_CFG  = 0x01

# MUX codes for single-ended AINx (datasheet)
_MUX_BASE = {0: 0b100, 1: 0b101, 2: 0b110, 3: 0b111}

# Data rate bits
_DR_BITS = {8:0b000, 16:0b001, 32:0b010, 64:0b011, 128:0b100, 250:0b101, 475:0b110, 860:0b111}

def _hi(x): return (x >> 8) & 0xFF
def _lo(x): return x & 0xFF

class ADS1115Reader:
    """
    Polls ADS1115 channels in a background thread, smooths with EMA,
    and exposes 7-bit (0..127) values. Optional per-channel calibration
    loaded from a JSON file.
    """

    def __init__(self, i2c_bus=1, address=0x48, channels=(0,1,2,3),
                 rate_sps=860, ema_alpha=0.2,
                 cal=None, cal_path=None):
        self.bus = SMBus(i2c_bus)
        self.addr = address
        self.channels = tuple(channels)
        self.ema_alpha = float(ema_alpha)

        # live values
        self.values_raw = {ch: 0 for ch in self.channels}   # signed 16-bit counts
        self.values_ema = {ch: 0.0 for ch in self.channels} # volts (EMA)
        self.values_cc  = {ch: 0 for ch in self.channels}   # 0..127 (pre-calibration)

        # calibration setup
        self.cal_path = cal_path
        self.cal = {int(k): v for (k, v) in (cal or {}).items()}
        if self.cal_path and os.path.isfile(self.cal_path):
            try:
                with open(self.cal_path, "r") as f:
                    file_cal = json.load(f)
                for k, v in file_cal.items():
                    self.cal[int(k)] = v
            except Exception:
                # ignore bad/empty file; keep in-memory defaults
                pass

        # precompute config for each channel (single-shot, PGA ±4.096 V)
        dr_bits = _DR_BITS[rate_sps]
        self._cfg_for = {}
        for ch in self.channels:
            mux = _MUX_BASE[ch]
            # OS=1 (start), MUX, PGA=001 (±4.096V), MODE=1 (single), DR, COMP=11 (disabled)
            cfg = (1<<15) | (mux<<12) | (0b001<<9) | (1<<8) | (dr_bits<<5) | 0b11
            self._cfg_for[ch] = cfg

        self._period = 1.0 / float(rate_sps)   # minimum wait between single-shot reads
        self._stop = False
        self._t = threading.Thread(target=self._loop, daemon=True)
        self._t.start()

    # ----------------- low-level I2C helpers -----------------

    def _write_cfg(self, cfg_word):
        # ADS1115 expects big-endian register order; smbus2 write_word_data is little-endian,
        # so we swap the bytes when writing.
        be = (_lo(cfg_word) << 8) | _hi(cfg_word)
        self.bus.write_word_data(self.addr, _REG_CFG, be)

    def _read_conv(self):
        # read_word_data returns little-endian; swap to big-endian
        v = self.bus.read_word_data(self.addr, _REG_CONV)
        v = ((v & 0xFF) << 8) | (v >> 8)
        if v & 0x8000:   # sign extend
            v -= 1 << 16
        return v

    # ----------------- sampling thread -----------------

    def _loop(self):
        """
        Sample each requested channel in single-shot mode at the chosen data rate.
        Map raw counts to volts (using ±4.096 V range), clamp to 0..3.3 V,
        apply EMA, then convert to 0..127 pre-calibration.
        """
        # Small guard so we never sleep less than ~1ms between conversions
        min_sleep = max(self._period, 0.001)

        while not self._stop:
            t0 = time.perf_counter()
            for ch in self.channels:
                # start conversion for this mux
                self._write_cfg(self._cfg_for[ch])
                # wait for the conversion to complete (~1 / rate_sps)
                time.sleep(min_sleep)
                raw = self._read_conv()
                self.values_raw[ch] = raw

                # convert to volts (PGA ±4.096 V)
                volts = (raw / 32768.0) * 4.096
                # ADS is referenced to GND; our pots are 0..3.3 V
                if volts < 0.0: volts = 0.0
                if volts > 3.3: volts = 3.3

                # EMA smoothing
                ema = self.values_ema[ch]
                ema = ema + self.ema_alpha * (volts - ema)
                self.values_ema[ch] = ema

                # scale to 0..127
                cc = int(round((ema / 3.3) * 127.0))
                if cc < 0: cc = 0
                if cc > 127: cc = 127

                # only update outward value if it moved by ≥1 to reduce chatter
                if abs(cc - self.values_cc[ch]) >= 1:
                    self.values_cc[ch] = cc

            # keep overall loop paced reasonably
            # (per-channel waits already dominate; no extra sleep needed here)

    # ----------------- calibration & API -----------------

    def _apply_cal(self, ch, cc):
        """
        Apply per-channel calibration:
          - clamp to [min..max]
          - optional deadband near endpoints (in raw-CC domain)
          - rescale to 0..127
          - optional invert
        """
        c = self.cal.get(int(ch))
        if not c:
            return cc

        dead = int(c.get("deadband", 0))
        cmin = int(c.get("min", 0))
        cmax = int(c.get("max", 127))

        # deadband clamp near ends
        if dead > 0:
            if cc < cmin + dead: cc = cmin
            if cc > cmax - dead: cc = cmax

        # clamp then map
        if cmax < cmin:
            cmin, cmax = cmax, cmin
        cc = max(cmin, min(cmax, cc))
        out = 0 if cmax == cmin else int(round((cc - cmin) * 127.0 / (cmax - cmin)))

        if bool(c.get("invert", False)):
            out = 127 - out
        return 0 if out < 0 else 127 if out > 127 else out

    def read_cc(self):
        """Return a dict {channel: 0..127} with calibration applied."""
        return {ch: self._apply_cal(ch, val) for ch, val in self.values_cc.items()}

    def save_cal(self, path=None):
        """Persist current calibration table to JSON."""
        p = path or self.cal_path
        if not p:
            raise ValueError("No cal_path provided to save.")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        # keys as strings for nicer JSON
        payload = {str(k): v for k, v in self.cal.items()}
        with open(p, "w") as f:
            json.dump(payload, f, indent=2, sort_keys=True)

    def stop(self):
        """Stop the sampling thread."""
        self._stop = True
        try:
            self._t.join(timeout=0.5)
        except Exception:
            pass
