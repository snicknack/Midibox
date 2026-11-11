#!/usr/bin/env python3
# Fatar MIDI v10: Hard-Press Only (Vel >0x37 On) + Strict Noise Filter
# 500ms Debounce for Off/Unknowns. Run: sudo python3 uart_sniffer_midi_v10.py

import serial
import time
import sys
import csv

CURRENT_BAUD = 38400
PORT = '/dev/serial0'
READ_TIMEOUT = 0.2
CSV_FILE = "keybed_midi_v10.csv"
UNKNOWN_FILE = "unknown_vels.txt"

KEY_MAP = {
    0x29: 21,  # A0 light
    0x38: 21,  # A0 medium
    0x3E: 108, # C8 medium
    0x3F: 108, # C8 hard
    0x2F: 21,  # A0/C8 off (assumed)
}

PADDING_VELS = {0x20, 0x21, 0x30, 0x31, 0x37}  # Ignore noise

class Debouncer:
    def __init__(self, cooldown_ms):
        self.last_time = 0
        self.cooldown = cooldown_ms / 1000.0

    def ready(self, now):
        if now - self.last_time > self.cooldown:
            self.last_time = now
            return True
        return False
