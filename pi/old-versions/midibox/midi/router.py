import mido

# Global state shared by pages
MIDI_CHANNEL = 1   # 1..16
TRANSPOSE    = 0   # -36..+36

class MidiRouter:
    def __init__(self):
        self.port_name = None
        self.out = None
        self.ensure_port()

    def ensure_port(self):
        try:
            if self.port_name:
                if self.out: self.out.close()
                self.out = mido.open_output(self.port_name)
                return
        except Exception as e:
            print("Failed to open MIDI port:", self.port_name, e)
        # fallback to virtual
        if self.out: self.out.close()
        self.out = mido.open_output("Touch GUI", virtual=True)
        self.port_name = None

    def list_ports(self):
        return mido.get_output_names()

    def set_port(self, name):
        self.port_name = name
        self.ensure_port()

    # send helpers
    def note_on(self, note, vel=110, ch=0):
        self.out.send(mido.Message('note_on', note=note, velocity=vel, channel=ch))

    def note_off(self, note, ch=0):
        self.out.send(mido.Message('note_off', note=note, velocity=0, channel=ch))

    def cc(self, cc, val, ch=0):
        self.out.send(mido.Message('control_change', control=cc, value=val, channel=ch))

    def pitchbend(self, value, ch=0):
        # value: 0..16383 (center=8192); mido pitch is -8192..+8191
        self.out.send(mido.Message('pitchwheel', pitch=int(value)-8192, channel=ch))

# Singleton-style router for simplicity
MIDI = MidiRouter()
