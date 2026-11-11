#!/usr/bin/env python3
# midibox_play.py  –  Raspberry Pi 4 bridge: STM32 UART (31 250 baud) → USB MIDI
import serial, time, signal, sys, mido

# ---------- CONFIG ----------
SERIAL_PORT    = '/dev/serial0'
SERIAL_BAUD    = 31250
SER_TIMEOUT    = 0.000

VIRTUAL_NAME   = 'Midibox Keyboard'
AUTO_ROUTE_TO  = 'Crave'      # substring to auto-connect hardware out; '' to disable

FORCE_CH       = 0            # 0 = MIDI ch1 (force all msgs to this channel)
TRANSPOSE_SEMI = 0
OCTAVE_SHIFT   = 0

VEL_CURVE      = 's-curve'    # 'linear','soft','hard','expo2','s-curve','fixed'
VEL_FIXED_VAL  = 100
VEL_MIN, VEL_MAX = 1,127

AT_EMA_ALPHA   = 0.35
DEDUP_MS       = 2
# ----------------------------

REALTIME = {0xF8,0xFA,0xFB,0xFC,0xFE,0xFF}
DATA_LEN = {0x80:2,0x90:2,0xA0:2,0xB0:2,0xC0:1,0xD0:1,0xE0:2}

def vel_map(v):
    v=max(0,min(127,v)); x=v/127.0
    if   VEL_CURVE=='soft':   y=x**0.7
    elif VEL_CURVE=='hard':   y=x**1.4
    elif VEL_CURVE=='expo2':  y=x**0.5
    elif VEL_CURVE=='s-curve':y=1/(1+2.71828**(-8*(x-0.5)))
    elif VEL_CURVE=='fixed':  return VEL_FIXED_VAL
    else:                     y=x
    return int(max(VEL_MIN,min(VEL_MAX,round(127*y))))

def clamp_note(n): return max(0,min(127,n))
def send_all(outs,msg): [o.send(msg) for o in outs]

def open_outputs():
    outs=[mido.open_output(VIRTUAL_NAME,virtual=True)]
    print(f"✅  virtual port '{VIRTUAL_NAME}' created")
    if AUTO_ROUTE_TO:
        for name in mido.get_output_names():
            if AUTO_ROUTE_TO.lower() in name.lower():
                try:
                    outs.append(mido.open_output(name))
                    print(f"🔗  routed to '{name}'")
                    break
                except Exception as e:
                    print("⚠️  could not open:",e)
    return outs

def panic(outs):
    print("\n⚠️  All Notes Off")
    for ch in range(16):
        send_all(outs,mido.Message('control_change',control=123,value=0,channel=ch))
        for n in range(128):
            send_all(outs,mido.Message('note_off',note=n,velocity=0,channel=ch))

def main():
    outs=open_outputs()
    ser=serial.Serial(SERIAL_PORT,SERIAL_BAUD,timeout=SER_TIMEOUT)
    print(f"🎛  Listening on {SERIAL_PORT}@{SERIAL_BAUD} — Ctrl+C for PANIC+exit\n")

    running=None; need=0; buf=bytearray(); at_prev=0; last_evt={}
    pedal_state = 0  # debounced sustain (0 or 127)

    def dedup(key):
        t=time.time()*1000; d=t-last_evt.get(key,0)
        if d<DEDUP_MS: return True
        last_evt[key]=t; return False

    def dispatch(st,data):
        nonlocal at_prev, pedal_state
        cmd=st&0xF0
        ch = FORCE_CH  # force every message to one channel

        # --- Sustain (CC 64) debounce: only send on state change across 64 ---
        if cmd==0xB0 and data[0]==64:
            val = 127 if data[1] >= 64 else 0
            if val != pedal_state:
                pedal_state = val
                send_all(outs, mido.Message('control_change', control=64, value=val, channel=ch))
            return

        if cmd==0x90:
            note,vel=data; note=clamp_note(note+TRANSPOSE_SEMI+12*OCTAVE_SHIFT)
            if vel>0:
                vel=vel_map(vel)
                if not dedup(('on',note,ch)):
                    send_all(outs,mido.Message('note_on',note=note,velocity=vel,channel=ch))
            else:
                if not dedup(('off',note,ch)):
                    send_all(outs,mido.Message('note_off',note=note,velocity=0,channel=ch))
        elif cmd==0x80:
            note,_=data; note=clamp_note(note+TRANSPOSE_SEMI+12*OCTAVE_SHIFT)
            if not dedup(('off',note,ch)):
                send_all(outs,mido.Message('note_off',note=note,velocity=0,channel=ch))
        elif cmd==0xD0:
            val=data[0]; at_prev=int(round(at_prev+AT_EMA_ALPHA*(val-at_prev)))
            send_all(outs,mido.Message('aftertouch',value=at_prev,channel=ch))
        elif cmd==0xA0:
            note,val=data; note=clamp_note(note+TRANSPOSE_SEMI+12*OCTAVE_SHIFT)
            send_all(outs,mido.Message('polytouch',note=note,value=val,channel=ch))
        elif cmd==0xB0:
            send_all(outs,mido.Message('control_change',control=data[0],value=data[1],channel=ch))
        elif cmd==0xC0:
            send_all(outs,mido.Message('program_change',program=data[0],channel=ch))
        elif cmd==0xE0:
            val=(data[1]<<7)|data[0]
            send_all(outs,mido.Message('pitchwheel',pitch=val-8192,channel=ch))

    def sigint(_s,_f):
        panic(outs); sys.exit(0)
    signal.signal(signal.SIGINT,sigint)

    while True:
        chunk=ser.read(64)
        if not chunk: continue
        for b in chunk:
            if b in REALTIME:  # ignore clock/active-sense
                continue
            if 0xF0<=b<=0xF7:   # drop sysex/system-common & reset parser
                running=None; need=0; buf.clear(); continue
            if 0x80<=b<=0xEF:  # status
                running=b; need=DATA_LEN.get(b&0xF0,0); buf.clear(); continue
            if b>0x7F or running is None:  # stray / no context
                buf.clear(); continue
            buf.append(b)
            if len(buf)==need:
                dispatch(running,buf); buf.clear()

if __name__=='__main__':
    try: main()
    except KeyboardInterrupt: pass
