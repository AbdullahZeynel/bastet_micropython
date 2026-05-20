# input.py — 3-button polling with combos and long-press
#
# Controls:
#   LEFT         → Move left
#   RIGHT        → Move right
#   MID (tap)    → Hold/reserve
#   MID + RIGHT  → Rotate CW
#   MID + LEFT   → Rotate CCW
#   ALL THREE    → Hard drop
#   MID (hold)   → Pause menu

from machine import Pin
import time

import config


class Button:
    """Single button with debounce and auto-repeat."""

    def __init__(self, pin_num):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self.last_state = 1
        self.pressed = False
        self.held = False
        self.raw_down = False
        self.press_time = 0
        self.last_repeat = 0
        self.repeat_started = False
        self.hold_duration = 0

    def update(self):
        now = time.ticks_ms()
        current = self.pin.value()
        self.pressed = False
        self.raw_down = (current == 0)

        if current == 0 and self.last_state == 1:
            # New press — debounce check
            if time.ticks_diff(now, self.press_time) > config.DEBOUNCE_MS:
                self.pressed = True
                self.held = True
                self.press_time = now
                self.last_repeat = now
                self.repeat_started = False
                self.hold_duration = 0

        elif current == 0 and self.last_state == 0:
            # Held down
            self.held = True
            self.hold_duration = time.ticks_diff(now, self.press_time)

            if not self.repeat_started:
                if self.hold_duration > config.REPEAT_DELAY_MS:
                    self.repeat_started = True
                    self.pressed = True
                    self.last_repeat = now
            else:
                if time.ticks_diff(now, self.last_repeat) > config.REPEAT_RATE_MS:
                    self.pressed = True
                    self.last_repeat = now

        elif current == 1:
            # Released
            self.held = False
            self.repeat_started = False
            self.hold_duration = 0

        self.last_state = current


class ButtonReader:
    """3-button system with combo detection."""

    def __init__(self):
        self.left = Button(config.PIN_BTN_LEFT)
        self.middle = Button(config.PIN_BTN_MIDDLE)
        self.right = Button(config.PIN_BTN_RIGHT)

        self._all = [self.left, self.middle, self.right]

        self.combo_rotate_cw = False
        self.combo_rotate_ccw = False
        self.combo_hard_drop = False
        self.long_press_middle = False

        self._combo_consumed = False
        self._long_press_fired = False

    def update(self):
        """Poll all buttons and detect combos. Call once per frame."""
        for btn in self._all:
            btn.update()

        self.combo_rotate_cw = False
        self.combo_rotate_ccw = False
        self.combo_hard_drop = False
        self.long_press_middle = False
        self._combo_consumed = False

        # Triple combo: hard drop
        if self.left.raw_down and self.middle.raw_down and self.right.raw_down:
            self.combo_hard_drop = True
            self._combo_consumed = True
            return

        # Double combos
        if self.middle.raw_down and self.right.raw_down:
            if self.middle.pressed or self.right.pressed:
                self.combo_rotate_cw = True
            self._combo_consumed = True
            return

        if self.middle.raw_down and self.left.raw_down:
            if self.middle.pressed or self.left.pressed:
                self.combo_rotate_ccw = True
            self._combo_consumed = True
            return

        # Long press: middle only
        if (self.middle.held and
            not self.left.raw_down and
            not self.right.raw_down and
            self.middle.hold_duration >= config.LONG_PRESS_MS):
            if not self._long_press_fired:
                self.long_press_middle = True
                self._long_press_fired = True
            return

        if not self.middle.held:
            self._long_press_fired = False

    def is_single_left(self):
        return self.left.pressed and not self._combo_consumed

    def is_single_right(self):
        return self.right.pressed and not self._combo_consumed

    def is_single_middle(self):
        return (self.middle.pressed and
                not self._combo_consumed and
                not self._long_press_fired)

    def any_pressed(self):
        return any(btn.pressed for btn in self._all)
