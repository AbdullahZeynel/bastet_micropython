# menu.py — Main menu (3-button, portrait mode)
# LEFT = up, RIGHT = down, MID = select

import time
import config


class MainMenu:
    """OLED main menu for portrait 64×128 display."""

    ITEMS = ["NEW GAME", "ABOUT"]

    def __init__(self, display, buttons):
        self.display = display
        self.buttons = buttons
        self.selected = 0
        self.blink_state = True
        self.last_blink = time.ticks_ms()

    def update(self):
        """Process button input. Returns selected index or None."""
        self.buttons.update()

        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_blink) > 300:
            self.blink_state = not self.blink_state
            self.last_blink = now

        if self.buttons.is_single_right():
            self.selected = (self.selected + 1) % len(self.ITEMS)
        if self.buttons.is_single_left():
            self.selected = (self.selected - 1) % len(self.ITEMS)
        if self.buttons.is_single_middle():
            return self.selected
        return None

    def draw(self):
        self.display.fill(0)

        self.display.text("BASTET", 8, 10, 1)
        self.display.text("PICO 2", 8, 22, 1)
        self.display.hline(4, 34, 56, 1)

        y_start = 45
        for i, item in enumerate(self.ITEMS):
            y = y_start + i * 20
            if i == self.selected:
                marker = ">" if self.blink_state else " "
                self.display.text(marker, 2, y, 1)
                self.display.text(item, 14, y, 1)
                self.display.hline(14, y + 9, len(item) * 8, 1)
            else:
                self.display.text(item, 14, y, 1)

        self.display.show()
