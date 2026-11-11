import serial, time

# open the Pi's UART or USB serial port
ser = serial.Serial('/dev/serial0', 115200, timeout=1)
time.sleep(2)  # give ESP32 time to boot

# send a test message to ESP32
ser.write(b'ui_t1Arc1:100\n')

# listen for messages coming back
while True:
    line = ser.readline().decode(errors='ignore').strip()
    if line:
        print("ESP says:", line)
