import RPi.GPIO as GPIO, time
CS = 22
GPIO.setmode(GPIO.BCM)
GPIO.setup(CS, GPIO.OUT, initial=GPIO.LOW)
print("LOW for 2s...")
time.sleep(2)
GPIO.output(CS, GPIO.HIGH)
print("HIGH for 2s...")
time.sleep(2)
GPIO.cleanup()
