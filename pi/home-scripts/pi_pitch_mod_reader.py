# pi_pitch_mod_reader.py
import time, mido

# ---- Try your package driver first ----
ReaderObj = None
try:
    from midibox.io.ads1115_reader import ADS1115Reader as _UserReader  # your module
    ReaderObj = _UserReader  # may or may not have expected methods
except Exception:
    _UserReader = None

# ---- Optional fallback: Adafruit driver ----
def _make_adafruit_reader():
    import board, busio
    from adafruit_ads1x15.ads1115 import ADS1115, Mode
    from adafruit_ads1x15.analog_in import AnalogIn
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS1115(i2c); ads.mode = Mode.CONTINUOUS
    ch = [AnalogIn(ads, ADS1115.P0), AnalogIn(ads, ADS1115.P1)]
    class _AFReader:
        def __init__(self): pass
        # unified API: return raw ints from .value
        def read_idx(self, idx): return ch[idx].value
    return _AFReader()

class ReaderAdapter:
    """
    Wraps whatever ADS reader you have and exposes a single method:
      read_idx(idx) -> raw integer
    """
    def __init__(self):
        self._obj = None
        self._list_method = None

        if _UserReader is not None:
            try:
                self._obj = _UserReader()
            except Exception:
                self._obj = None

        if self._obj is None:
            # fallback to Adafruit
            self._obj = _make_adafruit_reader()
            self.read_idx = self._obj.read_idx
            return

        # Map to a callable
        candidates = [
            "read_channel_raw", "read_channel", "read", "get", "value"
        ]
        for name in candidates:
            if hasattr(self._obj, name):
                fn = getattr(self._obj, name)
                self.read_idx = lambda i, _fn=fn: _fn(i)
                return

        # Maybe it has a list-returning method
        listers = ["read_all_raw", "read_all", "values"]
        for name in listers:
            if hasattr(self._obj, name):
                self._list_method = getattr(self._obj, name)
                self.read_idx = lambda i, _fn=self._list_method: _fn()[i]
                return

        # Nothing matched → Adafruit fallback
        self._obj = _make_adafruit_reader()
        self.read_idx = self._obj.read_idx

class PitchModReader:
    def __init__(self):
        self.reader = ReaderAdapter()
        print("Calibrating pitch + mod wheels… move them through travel for 1s")
        t0 = time.time()
        pr = self.reader.read_idx(0)
        mr = self.reader.read_idx(1)
        pmin=pmax=pr; mmin=mmax=mr
        while time.time()-t0 < 1.0:
            v0 = self.reader.read_idx(0)
            v1 = self.reader.read_idx(1)
            pmin=min(pmin,v0); pmax=max(pmax,v0)
            mmin=min(mmin,v1); mmax=max(mmax,v1)
            time.sleep(0.005)
        # avoid div by zero
        self.pmin, self.pmax = pmin, (pmax if pmax>pmin else pmin+1)
        self.mmin, self.mmax = mmin, (mmax if mmax>mmin else mmin+1)

        self.midi_out = mido.open_output()
        self.lastP = self.lastM = None

    @staticmethod
    def _norm(x, lo, hi):
        if x <= lo: return 0.0
        if x >= hi: return 1.0
        return (x-lo)/(hi-lo)

    def _send_pitch(self, v01):
        bend = int(max(0,min(1,v01))*16383) - 8192
        self.midi_out.send(mido.Message('pitchwheel', pitch=bend))

    def _send_mod(self, v01):
        self.midi_out.send(mido.Message('control_change', control=1, value=int(max(0,min(1,v01))*127)))

    def run(self, interval=0.01, deadband=0.002):
        print("Running…")
        while True:
            p = self._norm(self.reader.read_idx(0), self.pmin, self.pmax)
            m = self._norm(self.reader.read_idx(1), self.mmin, self.mmax)

            if self.lastP is None or abs(p-self.lastP) > deadband:
                self._send_pitch(p); self.lastP = p
            if self.lastM is None or abs(m-self.lastM) > 0.01:
                self._send_mod(m); self.lastM = m

            time.sleep(interval)

if __name__ == "__main__":
    try:
        PitchModReader().run()
    except KeyboardInterrupt:
        print("\nStopped.")
