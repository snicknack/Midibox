# File: max7219_display.py
"""
Helper module for FC-16 (MAX7219) 8x8 LED matrix chains on Raspberry Pi.

• Uses luma.led_matrix for painless SPI control
• Defaults for a 4×8×8 chain (common FC-16)

Wiring (typical on Pi):
  VCC → 5V, GND → GND, DIN → MOSI (GPIO10), CLK → SCLK (GPIO11), CS → CE0 (GPIO8)

Install deps on the Pi:
  pip install luma.led_matrix pillow

"""
from __future__ import annotations

import time
from typing import Iterable, List, Sequence

from luma.core.interface.serial import spi
from luma.led_matrix.device import max7219
from luma.core.render import canvas
from luma.core.legacy import show_message, text
from luma.core.legacy.font import CP437_FONT, TINY_FONT, proportional


class Max7219Display:
    def __init__(
        self,
        num_matrices: int = 4,
        spi_port: int = 0,
        spi_device: int = 0,  # CE0
        rotate: int = 0,
        block_orientation: int = 90,
        brightness: int = 8,
    ) -> None:
        """Create a MAX7219 device.

        Args:
            num_matrices: number of 8×8 tiles daisy-chained (FC-16 4-pack → 4)
            spi_port: SPI bus (Pi default 0)
            spi_device: SPI device (CE line) 0→CE0, 1→CE1
            rotate: 0/1/2/3 quarter turns (depends on how your modules are mounted)
            block_orientation: 0 or 90 – FC-16 boards usually need 90
            brightness: 0..15 (mapped to device contrast 0..255)
        """
        self._serial = spi(port=spi_port, device=spi_device, gpio=None, cs_high=False)
        self.device = max7219(
            self._serial,
            cascaded=num_matrices,
            rotate=rotate,
            block_orientation=block_orientation,
        )
        self.set_brightness(brightness)
        self.cols = num_matrices * 8
        self.rows = 8

    # --------------------- utilities ---------------------
    def set_brightness(self, level: int) -> None:
        """Set brightness 0..15 (maps to 0..255 contrast)."""
        level = max(0, min(15, int(level)))
        contrast = int((level / 15.0) * 255)
        self.device.contrast(contrast)

    def clear(self) -> None:
        self.device.clear()

    # --------------------- drawing -----------------------
    def draw_text(self, message: str, x: int = 0, y: int = 0) -> None:
        """Draw static text (no scrolling)."""
        with canvas(self.device) as draw:
            text(draw, (x, y), message, fill="white", font=proportional(CP437_FONT))

    def scroll_text(self, message: str, speed: float = 0.05, font: str = "cp437") -> None:
        """Scroll a message across the matrices.

        Args:
            message: text to scroll
            speed: delay per pixel shift (lower → faster)
            font: "cp437" (taller, readable) or "tiny"
        """
        fnt = proportional(CP437_FONT) if font == "cp437" else proportional(TINY_FONT)
        show_message(self.device, message, fill="white", font=fnt, scroll_delay=speed)

    def draw_bargraph(self, value: float) -> None:
        """Render a left-to-right bargraph (value 0.0..1.0)."""
        value = max(0.0, min(1.0, float(value)))
        cols_on = int(round(value * self.cols))
        with canvas(self.device) as draw:
            for x in range(cols_on):
                # full-height column
                draw.line((x, 0, x, self.rows - 1), fill="white")

    def draw_columns(self, heights: Sequence[int]) -> None:
        """Draw individual column heights (0..8 for each column)."""
        with canvas(self.device) as draw:
            for x, h in enumerate(heights[: self.cols]):
                h = max(0, min(8, int(h)))
                if h:
                    draw.line((x, self.rows - h, x, self.rows - 1), fill="white")

    def draw_bitmap(self, bitmap_rows: Sequence[Sequence[int]]) -> None:
        """Draw a raw bitmap (list of rows, each row list of 0/1 of length cols)."""
        with canvas(self.device) as draw:
            for y, row in enumerate(bitmap_rows[: self.rows]):
                for x, px in enumerate(row[: self.cols]):
                    if px:
                        draw.point((x, y), fill="white")


