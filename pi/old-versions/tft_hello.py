import board
import digitalio
import adafruit_ili9341

spi = board.SPI()  # SCK/MOSI/MISO = 11/10/9

cs   = digitalio.DigitalInOut(board.CE0)   # GPIO8  pin 24
dc   = digitalio.DigitalInOut(board.D24)   # GPIO24 pin 18
rst  = digitalio.DigitalInOut(board.D25)   # GPIO25 pin 22

display = adafruit_ili9341.ILI9341(spi, cs, dc, rst=rst, baudrate=32000000)

# Fill solid red (RGB565: 0xF800)
display.fill(0xF800)
