# screens.py — Splash and About screens (portrait 64×128)

import time
import config


class SplashScreen:
    """Power-on splash screen."""

    @staticmethod
    def show(display):
        display.fill(0)
        display.rect(2, 2, 60, 124, 1)
        display.text("BASTET", 8, 30, 1)
        display.text("PICO 2", 8, 50, 1)
        display.hline(8, 68, 48, 1)
        display.text("v2.0", 16, 80, 1)
        display.show()
        time.sleep_ms(config.SPLASH_DURATION_MS)


class AboutScreen:
    """About / info screen."""

    @staticmethod
    def show(display, buttons):
        display.fill(0)
        display.text("BASTET", 8, 6, 1)
        display.text("PICO", 16, 18, 1)
        display.hline(4, 30, 56, 1)
        display.text("Tetris", 8, 38, 1)
        display.text("but AI", 8, 50, 1)
        display.text("picks", 8, 62, 1)
        display.text("worst", 8, 74, 1)
        display.text("piece", 8, 86, 1)
        display.text(":)", 24, 98, 1)
        display.text("MID=OK", 4, 116, 1)
        display.show()

        time.sleep_ms(200)
        while True:
            buttons.update()
            if buttons.is_single_middle():
                break
            time.sleep_ms(50)
