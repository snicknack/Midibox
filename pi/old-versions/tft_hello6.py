import board, digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341

# Pins
cs_pin  = digitalio.DigitalInOut(board.CE0)   # GPIO8
dc_pin  = digitalio.DigitalInOut(board.D24)   # GPIO24
rst_pin = digitalio.DigitalInOut(board.D25)   # GPIO25

spi = board.SPI()

# LOWER BAUDRATE
disp = ili9341.ILI9341(spi, cs=cs_pin, dc=dc_pin, rst=rst_pin,
                       baudrate=16000000, rotation=180)

# Double full-frame write
def fill(color):
    img = Image.new("RGB", (disp.width, disp.height), color)
    disp.image(img)

fill((500, 500,500))
fill((32, 32, 32))  # grey background pass 2

# Draw UI layer
img = Image.new("RGB", (disp.width, disp.height), (32,32,32))
draw = ImageDraw.Draw(img)
font = ImageFont.load_default()
draw.text((20, 20), "HELLO MIDI BOX!", font=font, fill=(0,255,0))
disp.image(img)
