import mido
import time

print("Available MIDI outputs:")
outs = mido.get_output_names()
for i, name in enumerate(outs):
    print(f"[{i}] {name}")

if not outs:
    print("❌ No MIDI outputs found!")
    exit(1)

# Pick the first device (change index if needed)
idx = int(input("Select device index: "))
port_name = outs[idx]

print(f"Opening: {port_name}")
with mido.open_output(port_name) as out:
    note = 60  # Middle C
    print(f"Sending NOTE ON {note}")
    out.send(mido.Message('note_on', note=note, velocity=100))
    time.sleep(1.0)
    print(f"Sending NOTE OFF {note}")
    out.send(mido.Message('note_off', note=note, velocity=0))

print("✅ Done")
