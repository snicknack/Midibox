import board, digitalio
from PIL import Image
import adafruit_rgb_display.ili9341 as ili9341

class Display:
    def __init__(self, rotation=180, baud=32_000_000):
        spi = board.SPI()
        cs  = digitalio.DigitalInOut(board.CE0)   # GPIO8
        dc  = digitalio.DigitalInOut(board.D24)   # GPIO24
        rst = digitalio.DigitalInOut(board.D25)   # GPIO25
        self.disp = ili9341.ILI9341(spi, cs=cs, dc=dc, rst=rst,
                                    baudrate=baud, rotation=rotation)
        self.W, self.H = self.disp.width, self.disp.height

    def size(self):
        return self.W, self.H

    def new_frame(self, color=(28,28,32)):
        return Image.new("RGB", (self.W, self.H), color)

    def show(self, image):
        self.disp.image(image)
