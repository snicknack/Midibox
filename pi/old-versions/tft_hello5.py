import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341

# Config pins (match your wiring!)
cs_pin = digitalio.DigitalInOut(board.D5)     # LCD_CS
dc_pin = digitalio.DigitalInOut(board.D6)     # LCD_RS/DC
reset_pin = digitalio.DigitalInOut(board.D9)  # LCD_RST

# Setup SPI
spi = board.SPI()

# Create the display
disp = ili9341.ILI9341(spi, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=16000000, rotation=180 )

#double fill-frame write
def fill(color):
	img = Image.new("RGB", (disp.width, disp.height), color)
	disp.image(img)
	
fill((0, 0, 0))
fill((32, 32, 32))


# Clear display
disp.fill(0)

# Pillow image for drawing
width = disp.width
height = disp.height
image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)

# Background
draw.rectangle((0, 0, width-1, height-1), outline=0, fill=(200, 200, 200))

# Text
font = ImageFont.load_default()
draw.text((100, 100), "HELLO MIDI BOX!", font=font, fill=(0, 255, 0))

# Show it
disp.image(image)
