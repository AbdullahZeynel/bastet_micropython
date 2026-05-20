# display.py — Rotated display wrapper
# Maps logical 64×128 portrait → physical 128×64 landscape
# Transform: logical (lx, ly) → physical (ly, 63 - lx)

import framebuf


class RotatedDisplay:
    """90° CW rotated display. Logical 64×128 → Physical 128×64."""

    def __init__(self, display):
        self._d = display
        self.width = 64
        self.height = 128
        self._cbuf = bytearray(8)
        self._cfb = framebuf.FrameBuffer(self._cbuf, 8, 8, framebuf.MONO_VLSB)

    def fill(self, color):
        self._d.fill(color)

    def show(self):
        self._d.show()

    def pixel(self, x, y, color):
        self._d.pixel(y, 63 - x, color)

    def hline(self, x, y, w, color):
        self._d.vline(y, 64 - x - w, w, color)

    def vline(self, x, y, h, color):
        self._d.hline(y, 63 - x, h, color)

    def fill_rect(self, x, y, w, h, color):
        self._d.fill_rect(y, 64 - x - w, h, w, color)

    def rect(self, x, y, w, h, color):
        self._d.rect(y, 64 - x - w, h, w, color)

    def text(self, string, x, y, color=1):
        """Render text character-by-character, rotating each 90° CW."""
        for i, ch in enumerate(string):
            lx = x + i * 8
            for j in range(8):
                self._cbuf[j] = 0
            self._cfb.text(ch, 0, 0, 1)
            for cy in range(8):
                for cx in range(8):
                    if self._cfb.pixel(cx, cy):
                        self._d.pixel(y + cy, 63 - (lx + cx), color)
