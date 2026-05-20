# main.py — Bastet Pico entry point
# Runs automatically after boot.py on power-up
#
# 3-Button controls:
#   LEFT         → Move left / Menu up
#   RIGHT        → Move right / Menu down
#   MID (tap)    → Hold-swap / Menu select
#   MID + RIGHT  → Rotate CW
#   MID + LEFT   → Rotate CCW
#   ALL THREE    → Hard drop
#   MID (hold)   → Pause menu

import gc
import time
from machine import Pin, I2C

import config
import sys

sys.path.insert(0, '/lib')

from sh1106 import SH1106_I2C
from display import RotatedDisplay
from game.engine import BastetGame
from game.input import ButtonReader
from game.renderer import GameRenderer
from ui.menu import MainMenu
from ui.screens import SplashScreen, AboutScreen


def init_hardware():
    """Initialize I2C, OLED display and buttons."""
    i2c = I2C(
        config.I2C_ID,
        scl=Pin(config.PIN_SCL),
        sda=Pin(config.PIN_SDA),
        freq=config.I2C_FREQ,
    )

    devices = i2c.scan()
    if devices:
        print(f"I2C: {[hex(d) for d in devices]}")
    else:
        print("WARNING: No I2C device found!")

    raw_display = SH1106_I2C(
        config.SCREEN_WIDTH,
        config.SCREEN_HEIGHT,
        i2c,
        addr=config.I2C_ADDR,
    )

    display = RotatedDisplay(raw_display)
    buttons = ButtonReader()
    return display, buttons


def run_pause_menu(display, buttons, renderer):
    """Pause menu: RESUME / RESTART / MENU."""
    selected = 0
    num_items = 3
    time.sleep_ms(100)
    buttons.update()

    while True:
        buttons.update()
        if buttons.is_single_left():
            selected = (selected - 1) % num_items
        if buttons.is_single_right():
            selected = (selected + 1) % num_items
        if buttons.is_single_middle():
            if selected == 0:
                return 'resume'
            elif selected == 1:
                return 'restart'
            elif selected == 2:
                return 'menu'
        renderer.draw_pause_menu(selected)
        time.sleep_ms(33)


def run_game_over(display, buttons, renderer, game):
    """Game over menu: RESTART / MENU."""
    selected = 0
    num_items = 2
    time.sleep_ms(200)
    buttons.update()

    while True:
        buttons.update()
        if buttons.is_single_left():
            selected = (selected - 1) % num_items
        if buttons.is_single_right():
            selected = (selected + 1) % num_items
        if buttons.is_single_middle():
            if selected == 0:
                return 'restart'
            elif selected == 1:
                return 'menu'
        renderer.draw_game_over(game, selected)
        time.sleep_ms(33)


def run_game(display, buttons):
    """Run a single game session."""
    game = BastetGame()
    renderer = GameRenderer(display)

    while True:
        buttons.update()

        if game.game_over:
            return run_game_over(display, buttons, renderer, game)

        if buttons.long_press_middle:
            game.paused = True
            result = run_pause_menu(display, buttons, renderer)
            if result == 'resume':
                game.paused = False
                game.last_drop = time.ticks_ms()
            elif result == 'restart':
                return 'restart'
            elif result == 'menu':
                return 'menu'
            continue

        if buttons.combo_hard_drop:
            game.hard_drop()
        elif buttons.combo_rotate_cw:
            game.rotate_cw()
        elif buttons.combo_rotate_ccw:
            game.rotate_ccw()
        else:
            if buttons.is_single_left():
                game.move_left()
            if buttons.is_single_right():
                game.move_right()
            if buttons.is_single_middle():
                game.hold_swap()

        game.update()
        renderer.render(game)
        time.sleep_ms(33)
        gc.collect()


def main():
    """Main program loop."""
    display, buttons = init_hardware()
    SplashScreen.show(display)

    while True:
        menu = MainMenu(display, buttons)
        while True:
            selection = menu.update()
            menu.draw()
            if selection is not None:
                if selection == 0:
                    gc.collect()
                    while True:
                        result = run_game(display, buttons)
                        if result == 'restart':
                            gc.collect()
                            continue
                        else:
                            break
                    break
                elif selection == 1:
                    AboutScreen.show(display, buttons)
            time.sleep_ms(33)


main()
