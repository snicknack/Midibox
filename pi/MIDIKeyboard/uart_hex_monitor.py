import serial, time
ser = serial.Serial("/dev/ttyS0", 31250, timeout=0.05)
print("Listening on /dev/ttyS0 @31250...  (Ctrl-C to stop)")
while True:
    data = ser.read(128)
    if data:
        print(" ".join(f"{b:02X}" for b in data))
