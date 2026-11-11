python3 - << 'PY'
import serial, time
for port in ("/dev/serial0","/dev/ttyAMA0","/dev/ttyS0"):
    try:
        ser=serial.Serial(port,31250,timeout=0.1)
        print("Opened",port)
        t=time.time()
        n=0
        while time.time()-t<3:
            b=ser.read(64)
            n+=len(b)
        print(port,"bytes in 3s:",n)
        ser.close()
    except Exception as e:
        print("Error",port,e)
PY
