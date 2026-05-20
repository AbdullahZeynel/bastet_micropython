# config.py — Hardware pins, I2C settings, and game constants
# Portrait mode: 128x64 OLED rotated 90° CW → 64x128 logical

# I2C
I2C_ID = 0
I2C_FREQ = 400_000

# OLED pins (SH1106 I2C)
PIN_SCL = 1
PIN_SDA = 0
I2C_ADDR = 0x3C

# Physical display
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

# Logical display (90° CW rotated portrait)
LOGICAL_W = 64
LOGICAL_H = 128

# Button pins
PIN_BTN_LEFT = 2
PIN_BTN_MIDDLE = 3
PIN_BTN_RIGHT = 4

# Button timing (ms)
DEBOUNCE_MS = 50
REPEAT_DELAY_MS = 200
REPEAT_RATE_MS = 50
LONG_PRESS_MS = 500
COMBO_WINDOW_MS = 80

# Board dimensions
BOARD_COLS = 10
BOARD_ROWS = 20
BLOCK_SIZE = 4

# Board screen position (portrait)
BOARD_X = 2
BOARD_Y = 2
BOARD_PIXEL_W = BOARD_COLS * BLOCK_SIZE  # 40px
BOARD_PIXEL_H = BOARD_ROWS * BLOCK_SIZE  # 80px

# Right panel (next/hold preview)
PANEL_X = 45
NEXT_Y = 2
HOLD_Y = 40

# Bottom panel (score)
BOTTOM_Y = 86

# Drop speed per level (ms)
LEVEL_SPEEDS = [
    800, 720, 630, 550, 470,
    380, 300, 220, 140, 100,
    80,
]

# Scoring
LINE_SCORES = [0, 100, 300, 500, 800]  # 0-4 lines
LINES_PER_LEVEL = 10

# Bastet AI weights
WEIGHT_HEIGHT = -0.5
WEIGHT_HOLES = -3.5
WEIGHT_BUMPINESS = -0.2
WEIGHT_LINES = 1.0

# Bastet AI piece selection distribution (%)
BASTET_WEIGHTS = [80, 12, 6, 2]

# Splash screen
SPLASH_DURATION_MS = 2000
