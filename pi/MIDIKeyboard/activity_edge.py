#!/usr/bin/env python3
import pigpio, time

PIN_DATA = 25      # input from board (MOSI-out)
PIN_LED  = 17      # drives LED
HOLD_MS  = 50

pi = pigpio.pi()
assert pi.connected, "sudo pigpiod first"

pi.set_mode(PIN_DATA, pigpio.INPUT)
pi.set_mode(PIN_LED,  pigpio.OUTPUT)
pi.write(PIN_LED, 0)

last = 0
def on_edge(gpio, level, tick):
    global last
    last = tick
    pi.write(PIN_LED, 1)

cb = pi.callback(PIN_DATA, pigpio.EITHER_EDGE, on_edge)

try:
    while True:
        # turn LED off if no edges for HOLD_MS
        if last and pigpio.tickDiff(last, pi.get_current_tick()) > HOLD_MS*1000:
            pi.write(PIN_LED, 0)
        time.sleep(0.005)
except KeyboardInterrupt:
    pass
finally:
    cb.cancel()
    pi.stop()
