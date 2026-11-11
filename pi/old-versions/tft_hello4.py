import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_ili9341

# Release any previous displays
displayio.release_displays()

# SPI setup
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
tft_cs = board.D5       # Chip Select
tft_dc = board.D6       # Data/Command
tft_rst = board.D9      # Reset

# Create the display bus
display_bus = displayio.FourWire(
    spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst
)

# Init display
display = adafruit_ili9341.ILI9341(
    display_bus, width=240, height=320, rotation=180
)

# Make a main display group
splash = displayio.Group()
display.show(splash)

# Draw a background color
color_bitmap = displayio.Bitmap(240, 320, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x003366  # dark blue
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Add a label
text = "HELLO MIDI BOX!"
text_area = label.Label(
    terminalio.FONT, text=text, color=0xFFFFFF, x=20, y=160
)
splash.append(text_area)

while True:
    pass
