#!/usr/bin/env python3
# Raspberry Pi 4 — MIDI UART tuner → ALSA virtual MIDI
# RX: /dev/ttyAMA0 @ 31250 (GPIO15). Outputs to an ALSA virtual port "PiTuner Out".
# Commands via stdin: mon on|off | out on|off | inv on|off | curve linear|soft|hard|gamma <x> |
#                    ch <1-16|off> | tr <n> | fmt hex|dec|name |
#                    vron off|floor <min>|scale <min> <max> |
#                    vroff off|floor <min>|scale <min> <max> | help

import sys, time, select
import serial

import mido
from mido import Message

# ---------- Config ----------
SERIAL_PORT = '/dev/tty50'   # Pi4 PL011 UART on GPIO14/15; we use RX on GPIO15
BAUD = 31250

# Performance: keep prints off by default
MONITOR = True
FORWARD_OUT = True

# Tuning defaults
INVERT_VELOCITY = True
CURVE_MODE = ('linear', 1.0)   # ('linear', _) | ('soft', _) | ('hard', _) | ('gamma', gamma)
FORCE_CHANNEL = 1              # lock to channel 1 to avoid off/on mismatches; set None to passthrough
TRANSPOSE = 0                  # semitones (int)
PRINT_FMT = 'hex'              # 'hex' | 'dec' | 'name'

# Velocity post-processing (separate for Note-On and Note-Off):
# 'off'   -> do nothing
# 'floor' -> if v>0, v = max(MIN, v)
# 'scale' -> map 1..127 -> [MIN..MAX] (0 stays 0)
VR_ON_MODE,  VR_ON_MIN,  VR_ON_MAX  = 'floor', 10, 110
VR_OFF_MODE, VR_OFF_MIN, VR_OFF_MAX = 'off',   1,  64

# ---------- Open serial (non-blocking) ----------
ser = serial.Serial(SERIAL_PORT, BAUD, timeout=0)  # non-blocking
# Try to reduce latency
try:
    ser.reset_input_buffer()
except Exception:
    pass

# ---------- ALSA virtual output ----------
outport = mido.open_output('PiTuner Out', virtual=True)
print(f'UART: {SERIAL_PORT} @ {BAUD}  →  ALSA out: "PiTuner Out"')
print('Commands: mon on|off | out on|off | inv on|off | curve linear|soft|hard|gamma <x> | ch <1-16|off> | tr <n> | fmt hex|dec|name')
print('          vron off|floor <min>|scale <min> <max> | vroff off|floor <min>|scale <min> <max> | help')

# ---------- Helpers ----------
NOTE_NAMES = ("C","C#","D","D#","E","F","F#","G","G#","A","A#","B")
def note_name(n):
    n = 0 if n < 0 else (127 if n > 127 else n)
    return "%s%d" % (NOTE_NAMES[n % 12], (n // 12) - 1)

def apply_curve(v):
    if v <= 0: return 0
    if v >= 127: return 127
    mode, p = CURVE_MODE
    x = v / 127.0
    if mode == 'linear': y = x
    elif mode == 'soft': y = x ** 0.7
    elif mode == 'hard': y = x ** 1.5
    elif mode == 'gamma':
        try:
            g = float(p)
            if g <= 0: g = 1.0
            y = x ** g
        except Exception:
            y = x
    else:
        y = x
    vv = int(round(y * 127.0))
    return 0 if vv < 0 else (127 if vv > 127 else vv)

def _vel_post(v, mode, vmin, vmax):
    if v <= 0: return 0
    if mode == 'off': return v
    if mode == 'floor':
        vv = v if v > vmin else vmin
        return 127 if vv > 127 else int(vv)
    if mode == 'scale':
        a = max(0, min(127, int(vmin)))
        b = max(0, min(127, int(vmax)))
        if b < a: a, b = b, a
        span = max(1, b - a)
        vv = a + int(round((v / 127.0) * span))
        return 0 if vv < 0 else (127 if vv > 127 else vv)
    return v

def post_velocity_on(v):  return _vel_post(v, VR_ON_MODE,  VR_ON_MIN,  VR_ON_MAX)
def post_velocity_off(v): return _vel_post(v, VR_OFF_MODE, VR_OFF_MIN, VR_OFF_MAX)

def clamp_note(n):
    nn = n + TRANSPOSE
    return 0 if nn < 0 else (127 if nn > 127 else nn)

def force_channel_status(status):
    if FORCE_CHANNEL is None: return status
    if 0x80 <= status <= 0xEF:
        return (status & 0xF0) | ((FORCE_CHANNEL - 1) & 0x0F)
    return status

def fmt_msg(status, d1=None, d2=None):
    if PRINT_FMT == 'dec':
        if d2 is None: return f"{status} {d1}"
        return f"{status} {d1} {d2}"
    if PRINT_FMT == 'name' and d1 is not None:
        base = f"{status:02X}"
        t = status & 0xF0
        if t in (0x90, 0x80):
            nm = note_name(d1)
            return f"{base} {nm}" if d2 is None else f"{base} {nm} vel={d2}"
        if t == 0xD0: return f"{base} ChPr {d1}"
        if t == 0xB0: return f"{base} CC{d1}={d2}" if d2 is not None else f"{base} CC{d1}"
        if t == 0xE0 and d2 is not None:
            val = (d2 << 7) | (d1 & 0x7F)
            return f"{base} PB={val}"
        return f"{base} {d1:02X}" if d2 is None else f"{base} {d1:02X} {d2:02X}"
    # hex
    if d1 is None: return f"{status:02X}"
    return f"{status:02X} {d1:02X}" if d2 is None else f"{status:02X} {d1:02X} {d2:02X}"

def print_event(status, d1=None, d2=None, tuned=False):
    if not MONITOR: return
    pref = "Tuned " if tuned else "Raw   "
    print(pref + "| " + fmt_msg(status, d1, d2))

# ---------- ALSA send (using mido) ----------
def alsa_send(status, d1=None, d2=None):
    if not FORWARD_OUT: return
    t = status & 0xF0
    ch = (status & 0x0F) + 1  # mido is 1-16
    try:
        if 0x90 <= t <= 0xE0:
            if t == 0x90:
                if d2 is None: return
                outport.send(Message('note_on', channel=ch-1, note=d1, velocity=d2))
            elif t == 0x80:
                if d2 is None: return
                outport.send(Message('note_off', channel=ch-1, note=d1, velocity=d2))
            elif t == 0xA0:
                outport.send(Message('polytouch', channel=ch-1, note=d1, value=d2))
            elif t == 0xB0:
                outport.send(Message('control_change', channel=ch-1, control=d1, value=d2))
            elif t == 0xC0:
                outport.send(Message('program_change', channel=ch-1, program=d1))
            elif t == 0xD0:
                outport.send(Message('aftertouch', channel=ch-1, value=d1))
            elif t == 0xE0:
                # pitchbend 14-bit from two data bytes
                if d1 is None or d2 is None: return
                pb = ((d2 & 0x7F) << 7) | (d1 & 0x7F)
                outport.send(Message('pitchwheel', channel=ch-1, pitch=pb-8192))
        elif 0xF8 <= status <= 0xFF:
            # realtime
            if status == 0xF8: outport.send(Message('clock'))
            elif status == 0xFA: outport.send(Message('start'))
            elif status == 0xFB: outport.send(Message('continue'))
            elif status == 0xFC: outport.send(Message('stop'))
            # ignore others or add as needed
    except Exception as e:
        # keep hot path safe
        pass

# ---------- MIDI parser ----------
RUN = None
NEED = 0
D1B = None

def status_len(st):
    hi = st & 0xF0
    if 0x80 <= hi <= 0xE0:
        return 2 if (hi == 0xC0 or hi == 0xD0) else 3
    return 1

def process_msg(st, d1=None, d2=None):
    print_event(st, d1, d2, tuned=False)

    typ = st & 0xF0
    out_st, out_d1, out_d2 = st, d1, d2

    if typ == 0x90:
        if d1 is None or d2 is None: return
        n = clamp_note(d1)
        v = d2
        ch = st & 0x0F
        if v == 0:
            # Treat Note On 0 as Note Off
            rv = post_velocity_off(v)
            out_st = 0x80 | ch
            out_d1, out_d2 = n, rv
            out_st = force_channel_status(out_st)
            alsa_send(out_st, out_d1, out_d2)
        else:
            if INVERT_VELOCITY:
                v = 127 - v
            v = apply_curve(v)
            v = post_velocity_on(v)
            out_d1, out_d2 = n, v
            out_st = force_channel_status(st)
            alsa_send(out_st, out_d1, out_d2)

    elif typ == 0x80:
        if d1 is None or d2 is None: return
        n = clamp_note(d1)
        rv = post_velocity_off(d2)
        out_d1, out_d2 = n, rv
        out_st = force_channel_status(st)
        alsa_send(out_st, out_d1, out_d2)

    elif 0xA0 <= typ <= 0xE0:
        out_st = force_channel_status(st)
        alsa_send(out_st, d1, d2)

    print_event(out_st, out_d1, out_d2, tuned=True)

def feed_byte(b):
    global RUN, NEED, D1B
    if 0xF8 <= b <= 0xFF:  # realtime
        alsa_send(b)
        return
    if b & 0x80:           # status
        if b >= 0xF0:
            RUN = None; NEED = 0; D1B = None
            return
        RUN = b; NEED = status_len(b) - 1; D1B = None
        return
    if RUN is None:
        return
    if NEED == 0:          # C0/D0
        process_msg(RUN, b, None)
        return
    if D1B is None:
        D1B = b; NEED -= 1
        if NEED == 0:
            process_msg(RUN, D1B, None); D1B = None
        return
    else:
        process_msg(RUN, D1B, b)
        D1B = None
        NEED = status_len(RUN) - 1

# ---------- Console handling ----------
def handle_cmd(line):
    global MONITOR, FORWARD_OUT, INVERT_VELOCITY, CURVE_MODE, FORCE_CHANNEL, TRANSPOSE, PRINT_FMT
    global VR_ON_MODE, VR_ON_MIN, VR_ON_MAX, VR_OFF_MODE, VR_OFF_MIN, VR_OFF_MAX
    s = (line or '').strip()
    if not s: return
    lo = s.lower()

    if lo in ('mon', 'mon on'): MONITOR = True;  print('Monitor ON'); return
    if lo == 'mon off':         MONITOR = False; print('Monitor OFF'); return
    if lo == 'help':
        print('inv on|off | curve linear|soft|hard|gamma <x> | ch <1-16|off> | tr <n> | fmt hex|dec|name | out on|off')
        print('vron off|floor <min>|scale <min> <max> | vroff off|floor <min>|scale <min> <max> | help')
        return

    if lo.startswith('out '):
        FORWARD_OUT = (lo.split()[1] == 'on'); print(f'USB/ALSA out = {FORWARD_OUT}'); return

    if lo.startswith('inv '):
        INVERT_VELOCITY = (lo.split()[1] == 'on'); print(f'Invert = {INVERT_VELOCITY}'); return

    if lo.startswith('curve '):
        parts = lo.split()
        if len(parts) == 2 and parts[1] in ('linear','soft','hard'):
            CURVE_MODE = (parts[1], 1.0)
        elif len(parts) == 3 and parts[1] == 'gamma':
            try: CURVE_MODE = ('gamma', float(parts[2]))
            except: print('gamma needs a number, e.g., curve gamma 1.3'); return
        else:
            print('curve linear|soft|hard|gamma <x>'); return
        print(f'Curve = {CURVE_MODE[0]} {CURVE_MODE[1]}'); return

    if lo.startswith('ch '):
        tok = lo.split()[1]
        if tok == 'off': FORCE_CHANNEL = None
        else:
            try:
                ch = int(tok)
                if 1 <= ch <= 16: FORCE_CHANNEL = ch
                else: print("Channel 1..16 or 'off'"); return
            except: print("Channel 1..16 or 'off'"); return
        print(f'Force channel = {FORCE_CHANNEL}'); return

    if lo.startswith('tr '):
        try: TRANSPOSE = int(lo.split()[1]); print(f'Transpose = {TRANSPOSE}')
        except: print('Usage: tr <integer> (e.g., tr -12)')
        return

    if lo.startswith('fmt '):
        fmt = lo.split()[1]
        if fmt in ('hex','dec','name'): PRINT_FMT = fmt; print(f'Format = {PRINT_FMT}')
        else: print('fmt hex|dec|name')
        return

    if lo.startswith('vron'):
        p = lo.split()
        if len(p) == 2 and p[1] == 'off':
            VR_ON_MODE = 'off'; print('Note-On velocity: OFF'); return
        if len(p) == 3 and p[1] == 'floor':
            try: VR_ON_MODE = 'floor'; VR_ON_MIN = int(p[2]); print(f'Note-On velocity: FLOOR min={VR_ON_MIN}')
            except: print('Usage: vron floor <min 0..127>')
            return
        if len(p) == 4 and p[1] == 'scale':
            try:
                VR_ON_MODE = 'scale'; VR_ON_MIN = int(p[2]); VR_ON_MAX = int(p[3])
                print(f'Note-On velocity: SCALE {VR_ON_MIN}..{VR_ON_MAX}')
            except: print('Usage: vron scale <min 0..127> <max 0..127>')
            return
        print('Usage: vron off | vron floor <min> | vron scale <min> <max>'); return

    if lo.startswith('vroff'):
        p = lo.split()
        if len(p) == 2 and p[1] == 'off':
            VR_OFF_MODE = 'off'; print('Note-Off velocity: OFF'); return
        if len(p) == 3 and p[1] == 'floor':
            try: VR_OFF_MODE = 'floor'; VR_OFF_MIN = int(p[2]); print(f'Note-Off velocity: FLOOR min={VR_OFF_MIN}')
            except: print('Usage: vroff floor <min 0..127>')
            return
        if len(p) == 4 and p[1] == 'scale':
            try:
                VR_OFF_MODE = 'scale'; VR_OFF_MIN = int(p[2]); VR_OFF_MAX = int(p[3])
                print(f'Note-Off velocity: SCALE {VR_OFF_MIN}..{VR_OFF_MAX}')
            except: print('Usage: vroff scale <min 0..127> <max 0..127>')
            return
        print('Usage: vroff off | vroff floor <min> | vroff scale <min> <max>'); return

    print('Unknown. Try: help')

# ---------- Main loop ----------
last_console = time.time()
while True:
    # Drain serial quickly
    n = ser.in_waiting
    if n:
        data = ser.read(n)
        if data:
            for b in data:
                feed_byte(b)
        continue

    # Poll console ~every 10ms
    now = time.time()
    if now - last_console >= 0.01:
        last_console = now
        r, _, _ = select.select([sys.stdin], [], [], 0)
        if r:
            line = sys.stdin.readline()
            if line:
                handle_cmd(line)

    time.sleep(0.00005)
