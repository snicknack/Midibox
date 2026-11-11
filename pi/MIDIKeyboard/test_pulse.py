#!/usr/bin/env python3
import RPi.GPIO as GPIO, time
CS = 22  # BCM numbering
GPIO.setmode(GPIO.BCM)
GPIO.setup(CS, GPIO.OUT, initial=GPIO.LOW)  # LOW = idle (CS released)
print("Driving GPIO22 HIGH for 10 ms to pull /CS low...")
GPIO.output(CS, GPIO.HIGH)
time.sleep(0.010)
GPIO.output(CS, GPIO.LOW)
GPIO.cleanup()
