import serial, time
ser = serial.Serial('/dev/serial0',115200,timeout=1)
for v in [0,32,64,96,127,0]:
    ser.write(f"uic_pitchBar:{v}\n".encode()); ser.flush(); time.sleep(0.2)
    ser.write(f"uic_ModBar:{v}\n".encode());   ser.flush(); time.sleep(0.2)
