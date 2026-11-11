# midibox/io/encoders_sx1509_poll.py
import time, threading
from .sx1509 import SX1509

_Q = {0b0001:+1,0b0011:+1,0b0110:+1,0b0100:+1,0b0010:-1,0b0111:-1,0b1110:-1,0b1100:-1}

class SX1509Encoders:
    def __init__(self, address=0x3E, i2c_bus=1, poll_hz=1000, enc_maps=None):
        if enc_maps is None:
            enc_maps=[{"name":"ENC1","a":8,"b":9,"sw":10}]  # <-- your board
        self.ic = SX1509(address=address, i2c_bus=i2c_bus)
        self.encs=[]
        pins=[]
        for e in enc_maps:
            self.encs.append({**e, "state":0, "count":0, "pressed":False, "last_sw":1})
            pins += [e["a"], e["b"], e["sw"]]
        mask = 0
        for p in pins: mask |= (1<<p)
        self.ic.set_dir_inputs(mask); self.ic.enable_pullups(mask)

        port = self.ic.read_inputs()
        for e in self.encs:
            a=(port>>e["a"])&1; b=(port>>e["b"])&1; sw=(port>>e["sw"])&1
            e["state"] = a | (b<<1); e["last_sw"]=sw

        self._stop=False
        self._period = 1.0/float(poll_hz)
        self._t = threading.Thread(target=self._loop, daemon=True); self._t.start()

    def _loop(self):
        while not self._stop:
            port = self.ic.read_inputs()
            for e in self.encs:
                a=(port>>e["a"])&1; b=(port>>e["b"])&1; now=a | (b<<1)
                e["count"] += _Q.get((e["state"]<<2)|now, 0)
                e["state"]=now
                sw=(port>>e["sw"])&1
                if sw!=e["last_sw"]:
                    e["pressed"]=(sw==0); e["last_sw"]=sw
            time.sleep(self._period)

    def read_and_zero(self):
        out=[]
        for e in self.encs:
            c=e["count"]; e["count"]=0
            out.append((e["name"], c, e["pressed"]))
        return out

    def stop(self):
        self._stop=True; self._t.join(timeout=0.5)
