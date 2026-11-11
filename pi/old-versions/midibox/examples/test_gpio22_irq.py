# test_gpio22_irq.py
import RPi.GPIO as GPIO, time
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(22, GPIO.FALLING, callback=lambda ch: print("EDGE"), bouncetime=1)
print("Briefly short GPIO22 (pin 15) to GND – you should see 'EDGE'. Ctrl+C to quit.")
try:
    while True: time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
