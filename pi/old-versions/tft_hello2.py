import board, busio, digitalio
import displayio
from adafruit_display_text import label
import terminalio
import adafruit_ili9341

# Free any previous displays
displayio.release_displays()

# SPI and control pins
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
tft_cs   = digitalio.DigitalInOut(board.CE0)   # GPIO8
tft_dc   = digitalio.DigitalInOut(board.D24)   # GPIO24
tft_rst  = digitalio.DigitalInOut(board.D25)   # GPIO25

# Create the 4-wire display bus, then the display
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs,
                                 reset=tft_rst, baudrate=32000000)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

# Build a simple scene
splash = displayio.Group()
display.show(splash)

# Solid background
bg_bitmap = displayio.Bitmap(320, 240, 1)
bg_palette = displayio.Palette(1)
bg_palette[0] = 0x103050   # dark blue
bg = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)
splash.append(bg)

# Text
txt = label.Label(terminalio.FONT, text="Hello MIDI Box!", color=0xFFFF00)
txt.x = 20; txt.y = 120
splash.append(txt)

# Keep showing
while True:
    pass
