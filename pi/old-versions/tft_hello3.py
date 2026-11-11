import digitalio
import board
from PIL import Image, ImageDraw
from adafruit_rgb_display import ili9341

# SPI + pins
spi = board.SPI()
cs_pin = digitalio.DigitalInOut(board.CE0)    # GPIO8
dc_pin = digitalio.DigitalInOut(board.D24)    # GPIO24
rst_pin = digitalio.DigitalInOut(board.D25)   # GPIO25

# Init display
disp = ili9341.ILI9341(spi, cs=cs_pin, dc=dc_pin, rst=rst_pin, baudrate=32000000)

# Create an image
image = Image.new("RGB", (disp.width, disp.height), (0, 40, 80))
draw = ImageDraw.Draw(image)

# Draw text
draw.text((40, 100), "Hello MIDI Box!", fill=(255, 255, 0))

# Send to display
disp.image(image)
