#!/usr/bin/env python3
"""
pi_uart_plan_a.py

UART RX-only bridge for STM32 keybed scanner (Plan A):
 - Read raw stream on serial (31_250 bps)
 - Reconstruct velocity from status-nibble + 3rd byte (nibble hack)
 - Optionally force all events to MIDI channel 1
 - Optionally ignore velocity (use constant) or scale the reconstructed velocity
 - Output to ALSA virtual MIDI via mido.

Usage:
  python3 pi_uart_plan_a.py
  or
  UART=/dev/ttyS0 python3 pi_uart_plan_a.py
  or
  python3 pi_uart_plan_a.py /dev/ttyS0
"""

import os, sys, time
import serial
import mido
from mido import Message

# --------- Config (edit only these) ----------
# UART selection (env override or CLI arg allowed)
CANDIDATE_PORTS = [
    os.environ.get("UART", "").strip(),
    sys.argv[1].strip() if len(sys.argv) > 1 else "",
    "/dev/serial0", "/dev/ttyS0", "/dev/ttyAMA0"
]
BAUD = 31250
SERIAL_TIMEOUT = 0  # non-blocking

# MIDI out
MIDI_PORT_NAME = "PiKeybed Out"   # virtual ALSA port name

# Behaviour toggles
FORCE_CHANNEL = True    # True -> send everything on CHANNEL_NUMBER; False -> pass-through channel nibble
CHANNEL_NUMBER = 1      # 1..16 (only used if FORCE_CHANNEL True)

IGNORE_VELOCITY = False   # True -> use FIXED_VELOCITY_FOR_ALL; ignores incoming vel entirely
FIXED_VELOCITY_FOR_ALL = 100

# Nibble velocity reconstruction
# STM32 seems to encode MSB part in status low nibble inverted (15 - nibble)
# LSB bits come from the 3rd byte (choose 3 or 4 bits)
LSB_BITS = 3            # 3 or 4
# After reconstruction we optionally scale into a smaller range:
SCALE_VELOCITY = True
SCALE_MIN = 10         # minimum after scaling (for Note-On)
SCALE_MAX = 110        # maximum after scaling (for Note-On)
# Separate scaling for Note-Off (release velocity)
SCALE_VELOCITY_OFF = False
SCALE_OFF_MIN = 1
SCALE_OFF_MAX = 64

# Performance / debug
MONITOR = False         # True -> print raw & tuned messages (slow)
PRINT_RAW = False       # prints raw incoming bytes
# ---------------------------------------------

# ---------- helpers ----------
def pick_port():
    for p in CANDIDATE_PORTS:
        if p and os.path.exists(p):
            return p
    raise SystemExit("No UART device found. Enable serial in raspi-config or pass device as argument or UART env var.")

def clamp(v): 
    return 0 if v < 0 else (127 if v > 127 else int(v))

def reconstruct_velocity_from_frame(status_byte, byte3):
    """
    status_byte: full status, e.g., 0x9F
    byte3: the 3rd byte in the frame (0..127)
    Returns: 0..127 reconstructed velocity
    """
    # pull nibble, invert (observed pattern: harder -> lower nibble)
    nibble = status_byte & 0x0F   # 0..15
    msb = 15 - nibble             # invert so harder -> larger
    # combine
    if LSB_BITS == 4:
        lsb_mask = 0x0F
        vel = (msb << 4) | (byte3 & lsb_mask)
    else:
        lsb_mask = 0x07
        vel = (msb << 3) | (byte3 & lsb_mask)
    return clamp(vel)

def scale_velocity(v, is_note_on=True):
    # Optionally scale reconstructed velocity into custom min..max,
    # preserving 0 as note-off indicator when appropriate.
    if v <= 0:
        return 0
    if is_note_on:
        if not SCALE_VELOCITY: return v
        a,b = SCALE_MIN, SCALE_MAX
    else:
        if not SCALE_VELOCITY_OFF: return v
        a,b = SCALE_OFF_MIN, SCALE_OFF_MAX
    # linear map 1..127 -> a..b
    v_lin = (v / 127.0)
    vv = int(round(a + v_lin * (b - a)))
    return clamp(vv)

def force_channel_status_byte(status_byte):
    if not (0x80 <= status_byte <= 0xEF): 
        return status_byte
    if not FORCE_CHANNEL:
        return status_byte
    ch = (CHANNEL_NUMBER - 1) & 0x0F
    return (status_byte & 0xF0) | ch

# ---------- open serial & midi ----------
SERIAL_PORT = pick_port()
print(f"Opening serial port {SERIAL_PORT} @ {BAUD} bps (RX-only)")
ser = serial.Serial(SERIAL_PORT, BAUD, timeout=SERIAL_TIMEOUT, write_timeout=0)

try:
    midi_out = mido.open_output(MIDI_PORT_NAME, virtual=True)
except Exception as e:
    print("Warning: couldn't open virtual MIDI port via mido:", e)
    print("Attempting default output instead.")
    midi_out = mido.open_output()

print(f"MIDI out: {midi_out.name}")

# ---------- MIDI parsing state ----------
RUN = None       # current running status (status byte)
NEED = 0         # how many data bytes remaining (1 or 2)
D1 = None        # first data byte for 3-byte messages

def status_data_length(status):
    # return number of data bytes expected for this status (not counting realtime)
    if status >= 0xF8:
        return 0
    if status >= 0xF0:
        # system common: handle minimally (we mostly ignore)
        # for our purpose treat as 0
        return 0
    t = status & 0xF0
    if t == 0xC0 or t == 0xD0:
        return 1
    return 2

def send_midi_to_alsa(status_byte, d1=None, d2=None):
    st = force_channel_status_byte(status_byte)
    t = st & 0xF0
    ch = st & 0x0F  # mido channels 0..15
    try:
        if 0x90 == t:   # note on
            if d1 is None: return
            vel = d2 if d2 is not None else 0
            # if we are configured to ignore velocity
            if IGNORE_VELOCITY:
                vel = FIXED_VELOCITY_FOR_ALL
            # otherwise we assume already reconstructed/scaled before calling
            midi_out.send(Message('note_on', channel=ch, note=d1, velocity=vel))
        elif 0x80 == t:
            if d1 is None: return
            vel = d2 if d2 is not None else 0
            if IGNORE_VELOCITY:
                vel = FIXED_VELOCITY_FOR_ALL
            midi_out.send(Message('note_off', channel=ch, note=d1, velocity=vel))
        elif 0xB0 == t:
            if d1 is None or d2 is None: return
            midi_out.send(Message('control_change', channel=ch, control=d1, value=d2))
        elif 0xC0 == t:
            if d1 is None: return
            midi_out.send(Message('program_change', channel=ch, program=d1))
        elif 0xD0 == t:
            if d1 is None: return
            midi_out.send(Message('aftertouch', channel=ch, value=d1))
        elif 0xE0 == t:
            if d1 is None or d2 is None: return
            pb = ((d2 & 0x7F) << 7) | (d1 & 0x7F)
            midi_out.send(Message('pitchwheel', channel=ch, pitch=pb - 8192))
        # ignore system messages here
    except Exception as e:
        # avoid crashing on mido errors
        if MONITOR:
            print("MIDI send error:", e)

# ---------- main loop ----------
print("Starting RX parse loop. Press Ctrl-C to stop.")
try:
    while True:
        n = ser.in_waiting
        if n:
            data = ser.read(n)
            if PRINT_RAW:
                sys.stdout.write("RAW: " + " ".join(f"{b:02X}" for b in data) + "\n")
            for b in data:
                # real-time (single-byte) messages (we ignore for now)
                if 0xF8 <= b <= 0xFF:
                    # optionally you could forward clocks etc.
                    continue

                # status byte?
                if b & 0x80:
                    # system common or status
                    if b >= 0xF0:
                        # reset running status for simplicity
                        RUN = None
                        NEED = 0
                        D1 = None
                        continue
                    RUN = b
                    NEED = status_data_length(RUN)
                    D1 = None
                    continue

                # data byte
                if RUN is None:
                    # stray data — ignore
                    continue

                if NEED == 0:
                    # this occurs for 1-byte status messages but shouldn't happen here
                    continue

                if NEED == 2:
                    # first data byte of 3-byte message
                    D1 = b
                    NEED = 1
                    continue

                # NEED == 1 -> final data byte
                # Now we have RUN (status), D1 (first data), b (second data)
                status_byte = RUN
                d1 = D1
                d2 = b
                # process Note On special-case to reconstruct velocity
                t = status_byte & 0xF0
                if t == 0x90:
                    # raw incoming velocity is in d2 but also the status nibble contains MSB info
                    if IGNORE_VELOCITY:
                        final_vel = FIXED_VELOCITY_FOR_ALL
                    else:
                        # reconstruct
                        reconstructed = reconstruct_velocity_from_frame(status_byte, d2)
                        final_vel = scale_velocity(reconstructed, is_note_on=True)
                    # if reconstructed velocity == 0, treat as note off
                    if final_vel == 0:
                        out_status = force_channel_status_byte(0x80 | (status_byte & 0x0F))
                        send_midi_to_alsa(out_status, d1, 0)
                    else:
                        out_status = force_channel_status_byte(0x90 | (status_byte & 0x0F))
                        send_midi_to_alsa(out_status, d1, final_vel)
                elif t == 0x80:
                    # explicit note off: optionally scale release vel
                    if IGNORE_VELOCITY:
                        final_vel = FIXED_VELOCITY_FOR_ALL
                    else:
                        final_vel = scale_velocity(d2, is_note_on=False)
                    out_status = force_channel_status_byte(status_byte)
                    send_midi_to_alsa(out_status, d1, final_vel)
                else:
                    # other message types: simply forward (optionally force ch)
                    out_status = force_channel_status_byte(status_byte)
                    send_midi_to_alsa(out_status, d1, d2)

                # reset running status handling per standard running status behaviour:
                # many devices allow running status; we preserve RUN but NEED will be recalculated on next status
                RUN = RUN  # keep running status until changed by a new status byte
                D1 = None
        else:
            # nothing to read
            time.sleep(0.00005)

except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    try:
        ser.close()
    except:
        pass
    print("Closed serial. Exiting.")
