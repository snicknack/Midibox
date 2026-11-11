# encoders_sx1509_driver.py
# Direct SMBus driver for SX1509 encoders (A/B) + button press/release.
# Compatible with older calls: addr=..., poll_hz=..., pairs=..., presses=...
# Exposes callbacks and convenience methods: read_and_zero(), close().

from smbus2 import SMBus
from time import monotonic, sleep

# ---------------- SX1509 minimal register set ----------------
class SX1509:
    REG_INPUT_DISABLE_B   = 0x00
    REG_INPUT_DISABLE_A   = 0x01
    REG_PULLUP_B          = 0x06
    REG_PULLUP_A          = 0x07
    REG_DIR_B             = 0x0E
    REG_DIR_A             = 0x0F
    REG_DATA_B            = 0x10
    REG_DATA_A            = 0x11
    REG_DEBOUNCE_CONFIG   = 0x22
    REG_DEBOUNCE_ENABLE_B = 0x23
    REG_DEBOUNCE_ENABLE_A = 0x24

    def __init__(self, bus=1, address=0x3E):
        self.bus  = SMBus(bus)
        self.addr = address
        # shadow registers we touch
        self._dirA  = 0xFF
        self._dirB  = 0xFF
        self._pullA = 0x00
        self._pullB = 0x00
        self._debA  = 0x00
        self._debB  = 0x00
        # set directions to inputs by default
        self.writeReg(self.REG_DIR_A, self._dirA)
        self.writeReg(self.REG_DIR_B, self._dirB)

    # --- low-level i2c ---
    def writeReg(self, reg, val):
        self.bus.write_byte_data(self.addr, reg, val & 0xFF)

    def readReg(self, reg):
        return self.bus.read_byte_data(self.addr, reg) & 0xFF

    # --- GPIO helpers ---
    def digitalRead(self, pin):
        bankA = pin < 8
        reg   = self.REG_DATA_A if bankA else self.REG_DATA_B
        bit   = pin if bankA else (pin - 8)
        val   = self.readReg(reg)
        return (val >> bit) & 1

    def setInput(self, pin, pullup=True, debounce=False):
        """Configure pin as input, optionally with pull-up and debounce."""
        bankA = pin < 8
        bit   = pin if bankA else (pin - 8)

        # Direction: 1 = input
        if bankA:
            self._dirA |= (1 << bit)
            self.writeReg(self.REG_DIR_A, self._dirA)
        else:
            self._dirB |= (1 << bit)
            self.writeReg(self.REG_DIR_B, self._dirB)

        # Pull-up control
        if bankA:
            if pullup: self._pullA |= (1 << bit)
            else:      self._pullA &= ~(1 << bit)
            self.writeReg(self.REG_PULLUP_A, self._pullA)
        else:
            if pullup: self._pullB |= (1 << bit)
            else:      self._pullB &= ~(1 << bit)
            self.writeReg(self.REG_PULLUP_B, self._pullB)

        # Debounce enable
        if bankA:
            if debounce: self._debA |= (1 << bit)
            else:        self._debA &= ~(1 << bit)
            self.writeReg(self.REG_DEBOUNCE_ENABLE_A, self._debA)
        else:
            if debounce: self._debB |= (1 << bit)
            else:        self._debB &= ~(1 << bit)
            self.writeReg(self.REG_DEBOUNCE_ENABLE_B, self._debB)

        # Input buffer enable (clear bit in INPUT_DISABLE)
        reg_in_dis = self.REG_INPUT_DISABLE_A if bankA else self.REG_INPUT_DISABLE_B
        cur = self.readReg(reg_in_dis)
        cur &= ~(1 << bit)  # 0 = input buffer enabled
        self.writeReg(reg_in_dis, cur)

    def setDebounceTime(self, approx_ms=0):
        """
        Set debounce period (global) — coarse. We pick a reasonable code.
        Refer to datasheet for exact timing table. 0b010 is a decent mid value.
        """
        code = 0b000  # ~few ms (works well for encoder presses)
        self.writeReg(self.REG_DEBOUNCE_CONFIG, code & 0x07)


# ---------------- Quadrature decode table ----------------
# prev(2b)<<2 | curr(2b) -> delta
_QD = {
    0b0001: +1, 0b0010: -1,
    0b0100: +1, 0b0111: -1,
    0b1000: -1, 0b1011: +1,
    0b1110: +1, 0b1100: -1,
}
# All other transitions are ignored (bounce/invalid)


# ---------------- Encoder Driver ----------------
class EncoderDriver:
    def __init__(
        self,
        bus=1,
        address=0x3E,
        poll_interval_s=0.003,   # ~3 ms (≈333 Hz)
        on_rotate=None,          # fn(name:str, delta:int)
        on_press=None,           # fn(name:str)
        on_release=None,         # fn(name:str)
        enable_ab_pullups=True,  # enable pull-ups on A/B unless you have externals
        debounce_ms=8,
        # --- compatibility shims ---
        addr=None,               # alias for address
        poll_hz=None,            # provide frequency instead of interval
        pairs=None,              # list of (A,B) tuples
        presses=None,            # list of press pins aligned with pairs
    ):
        # Map compatibility args
        if addr is not None:
            address = addr
        if poll_hz:
            poll_interval_s = 1.0 / float(poll_hz)

        # Build pin map
        if pairs is not None:
            default_presses = [2, 5, 8, 11, 14]
            if presses is None:
                presses = default_presses[:len(pairs)]
            names = ["arc1", "arc2", "arc3", "arc4", "tempo"]
            self.pinmap = {}
            for i, (a, b) in enumerate(pairs):
                name = names[i] if i < len(names) else f"enc{i+1}"
                self.pinmap[name] = {"a": a, "b": b, "press": presses[i]}
        else:
            # Standard 5-encoder layout
            self.pinmap = {
                "arc1":  {"a": 0,  "b": 1,  "press": 2},
                "arc2":  {"a": 3,  "b": 4,  "press": 5},
                "arc3":  {"a": 6,  "b": 7,  "press": 8},
                "arc4":  {"a": 9,  "b": 10, "press": 11},
                "tempo": {"a": 12, "b": 13, "press": 14},
            }

        self.sx = SX1509(bus=bus, address=address)
        self.poll_interval_s = poll_interval_s
        self.on_rotate = on_rotate
        self.on_press = on_press
        self.on_release = on_release

        self._ab_prev = {}   # name -> (A<<1 | B)
        self._pr_prev = {}   # name -> HIGH=idle / LOW=pressed
        self._running = False

        # index order for read_and_zero()
        self._order = list(self.pinmap.keys())
        self._delta_accum = {name: 0 for name in self._order}
        self._press_edge  = {name: 0 for name in self._order}  # +1=press, -1=release, 0=none

        self._configure(enable_ab_pullups, debounce_ms)

    # Backwards-compat: allow chaining .begin()
    def begin(self):
        return self

    # --- hardware setup ---
    def _configure(self, enable_ab_pullups, debounce_ms):
        # A/B lines
        for _, pins in self.pinmap.items():
            self.sx.setInput(pins["a"], pullup=enable_ab_pullups, debounce=False)
            self.sx.setInput(pins["b"], pullup=enable_ab_pullups, debounce=False)

        # Press lines (pull-up + debounce)
        for _, pins in self.pinmap.items():
            self.sx.setInput(pins["press"], pullup=True, debounce=True)

        self.sx.setDebounceTime(debounce_ms)

        # Seed previous states
        for name, pins in self.pinmap.items():
            a = self.sx.digitalRead(pins["a"])
            b = self.sx.digitalRead(pins["b"])
            pr = self.sx.digitalRead(pins["press"])  # HIGH idle (due to pull-up)
            self._ab_prev[name] = (a << 1) | b
            self._pr_prev[name] = pr

    # --- one poll step ---
    def poll(self):
        # Rotation: accumulate deltas
        for name, pins in self.pinmap.items():
            a = self.sx.digitalRead(pins["a"])
            b = self.sx.digitalRead(pins["b"])
            curr = (a << 1) | b
            prev = self._ab_prev[name]
            code = ((prev & 0b11) << 2) | (curr & 0b11)
            delta = _QD.get(code, 0)
            if delta:
                self._delta_accum[name] += delta
                if self.on_rotate:
                    self.on_rotate(name, delta)
            self._ab_prev[name] = curr

        # Press / Release (active low) → edge flags
        for name, pins in self.pinmap.items():
            state = self.sx.digitalRead(pins["press"])
            prev  = self._pr_prev[name]
            if state != prev:
                if state == 0:   # HIGH->LOW = pressed
                    self._press_edge[name] = +1
                    if self.on_press: self.on_press(name)
                else:            # LOW->HIGH = released
                    self._press_edge[name] = -1
                    if self.on_release: self.on_release(name)
            self._pr_prev[name] = state

    # --- compatibility/convenience ---
    def read_and_zero(self):
        """
        Return a list of (idx, delta, edge) for encoders that moved or had a press/release
        since the last call. edge: +1=press, -1=release, 0=none.
        """
        self.poll()
        out = []
        for idx, name in enumerate(self._order):
            d = self._delta_accum[name]
            e = self._press_edge[name]
            if d != 0 or e != 0:
                out.append((idx, d, e))
            self._delta_accum[name] = 0
            self._press_edge[name]  = 0
        return out

    def run_forever(self):
        self._running = True
        next_t = monotonic()
        while self._running:
            self.poll()
            next_t += self.poll_interval_s
            sleep(max(0.0, next_t - monotonic()))

    def stop(self):
        self._running = False

    def close(self):
        """Close the underlying I²C bus."""
        try:
            self.sx.bus.close()
        except Exception:
            pass


# ---------------- Optional smoke test ----------------
if __name__ == "__main__":
    def _rot(n, d): print(f"[ROTATE] {n} {d:+d}")
    def _prs(n):    print(f"[PRESS ] {n}")
    def _rel(n):    print(f"[RELEASE] {n}")

    drv = EncoderDriver(addr=0x3E, poll_hz=333).begin()
    drv.on_rotate  = _rot
    drv.on_press   = _prs
    drv.on_release = _rel
    try:
        drv.run_forever()
    except KeyboardInterrupt:
        drv.stop()
        drv.close()
