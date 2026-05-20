# renderer.py — OLED drawing engine (portrait mode 64×128)
#
# Layout:
# ┌──────────────────┐  64px
# │ ┌──────────┐ NXT │
# │ │  BOARD   │ ██  │
# │ │  10×20   │ HLD │  128px
# │ │  4px/blk │ ██  │
# │ └──────────┘     │
# │ SCR:xxxxx        │
# │ LV:x  LN:xx     │
# └──────────────────┘

import config


# Custom 4×6 pixel mini font for compact stats display
MINI_FONT = {
    '0': [0b0110, 0b1001, 0b1001, 0b1001, 0b0110, 0b0000],
    '1': [0b0010, 0b0110, 0b0010, 0b0010, 0b0111, 0b0000],
    '2': [0b0110, 0b1001, 0b0010, 0b0100, 0b1111, 0b0000],
    '3': [0b1110, 0b0001, 0b0110, 0b0001, 0b1110, 0b0000],
    '4': [0b1001, 0b1001, 0b1111, 0b0001, 0b0001, 0b0000],
    '5': [0b1111, 0b1000, 0b1110, 0b0001, 0b1110, 0b0000],
    '6': [0b0110, 0b1000, 0b1110, 0b1001, 0b0110, 0b0000],
    '7': [0b1111, 0b0001, 0b0010, 0b0100, 0b0100, 0b0000],
    '8': [0b0110, 0b1001, 0b0110, 0b1001, 0b0110, 0b0000],
    '9': [0b0110, 0b1001, 0b0111, 0b0001, 0b0110, 0b0000],
    'A': [0b0110, 0b1001, 0b1111, 0b1001, 0b1001, 0b0000],
    'B': [0b1110, 0b1001, 0b1110, 0b1001, 0b1110, 0b0000],
    'C': [0b0111, 0b1000, 0b1000, 0b1000, 0b0111, 0b0000],
    'D': [0b1110, 0b1001, 0b1001, 0b1001, 0b1110, 0b0000],
    'E': [0b1111, 0b1000, 0b1110, 0b1000, 0b1111, 0b0000],
    'F': [0b1111, 0b1000, 0b1110, 0b1000, 0b1000, 0b0000],
    'G': [0b0110, 0b1000, 0b1011, 0b1001, 0b0110, 0b0000],
    'H': [0b1001, 0b1001, 0b1111, 0b1001, 0b1001, 0b0000],
    'I': [0b1110, 0b0100, 0b0100, 0b0100, 0b1110, 0b0000],
    'K': [0b1001, 0b1010, 0b1100, 0b1010, 0b1001, 0b0000],
    'L': [0b1000, 0b1000, 0b1000, 0b1000, 0b1111, 0b0000],
    'M': [0b1001, 0b1111, 0b1111, 0b1001, 0b1001, 0b0000],
    'N': [0b1001, 0b1101, 0b1011, 0b1001, 0b1001, 0b0000],
    'O': [0b0110, 0b1001, 0b1001, 0b1001, 0b0110, 0b0000],
    'P': [0b1110, 0b1001, 0b1110, 0b1000, 0b1000, 0b0000],
    'R': [0b1110, 0b1001, 0b1110, 0b1010, 0b1001, 0b0000],
    'S': [0b0111, 0b1000, 0b0110, 0b0001, 0b1110, 0b0000],
    'T': [0b1111, 0b0010, 0b0010, 0b0010, 0b0010, 0b0000],
    'U': [0b1001, 0b1001, 0b1001, 0b1001, 0b0110, 0b0000],
    'V': [0b1001, 0b1001, 0b1001, 0b0110, 0b0110, 0b0000],
    'W': [0b1001, 0b1001, 0b1111, 0b1111, 0b1001, 0b0000],
    'X': [0b1001, 0b0110, 0b0110, 0b0110, 0b1001, 0b0000],
    'Y': [0b1001, 0b1001, 0b0110, 0b0010, 0b0010, 0b0000],
    ':': [0b0000, 0b0100, 0b0000, 0b0100, 0b0000, 0b0000],
    ' ': [0b0000, 0b0000, 0b0000, 0b0000, 0b0000, 0b0000],
    '-': [0b0000, 0b0000, 0b1111, 0b0000, 0b0000, 0b0000],
    '.': [0b0000, 0b0000, 0b0000, 0b0000, 0b0100, 0b0000],
}


def draw_mini(display, text, x, y, color=1):
    """Draw text using the 4×6 mini font (5px pitch)."""
    cx = x
    for ch in text:
        bitmap = MINI_FONT.get(ch.upper())
        if bitmap is None:
            cx += 5
            continue
        for ri in range(6):
            row_bits = bitmap[ri]
            for ci in range(4):
                if row_bits & (0b1000 >> ci):
                    display.pixel(cx + ci, y + ri, color)
        cx += 5


class GameRenderer:
    """Draws game state to the OLED (portrait 64×128)."""

    def __init__(self, display):
        self.display = display

    def render(self, game):
        self.display.fill(0)
        self._draw_border()
        self._draw_board(game)
        self._draw_ghost(game)
        self._draw_current(game)
        self._draw_next(game)
        self._draw_hold(game)
        self._draw_stats(game)
        self.display.show()

    def _draw_border(self):
        x = config.BOARD_X - 1
        y = config.BOARD_Y - 1
        w = config.BOARD_PIXEL_W + 2
        h = config.BOARD_PIXEL_H + 2
        self.display.rect(x, y, w, h, 1)

    def _draw_board(self, game):
        bs = config.BLOCK_SIZE
        ox, oy = config.BOARD_X, config.BOARD_Y
        for row in range(config.BOARD_ROWS):
            for col in range(config.BOARD_COLS):
                if game.board[row][col]:
                    self.display.fill_rect(ox + col * bs, oy + row * bs, bs, bs, 1)

    def _draw_current(self, game):
        shape = game.get_current_shape()
        if shape is None:
            return
        bs = config.BLOCK_SIZE
        ox, oy = config.BOARD_X, config.BOARD_Y
        for r in range(4):
            for c in range(4):
                if shape[r][c]:
                    bx, by = game.current_x + c, game.current_y + r
                    if 0 <= bx < config.BOARD_COLS and 0 <= by < config.BOARD_ROWS:
                        self.display.fill_rect(ox + bx * bs, oy + by * bs, bs, bs, 1)

    def _draw_ghost(self, game):
        shape = game.get_current_shape()
        if shape is None:
            return
        ghost_y = game.get_ghost_y()
        if ghost_y == game.current_y:
            return
        bs = config.BLOCK_SIZE
        ox, oy = config.BOARD_X, config.BOARD_Y
        for r in range(4):
            for c in range(4):
                if shape[r][c]:
                    bx, by = game.current_x + c, ghost_y + r
                    if 0 <= bx < config.BOARD_COLS and 0 <= by < config.BOARD_ROWS:
                        self.display.rect(ox + bx * bs, oy + by * bs, bs, bs, 1)

    def _draw_next(self, game):
        ox, oy = config.PANEL_X, config.NEXT_Y
        draw_mini(self.display, "NXT", ox, oy)
        shape = game.get_next_shape()
        if shape is None:
            return
        bs = 3
        sy = oy + 8
        for r in range(4):
            for c in range(4):
                if shape[r][c]:
                    self.display.fill_rect(ox + c * bs, sy + r * bs, bs, bs, 1)

    def _draw_hold(self, game):
        ox, oy = config.PANEL_X, config.HOLD_Y
        draw_mini(self.display, "HLD", ox, oy)
        shape = game.get_hold_shape()
        if shape is None:
            self.display.rect(ox, oy + 8, 12, 12, 1)
            return
        bs = 3
        sy = oy + 8
        for r in range(4):
            for c in range(4):
                if shape[r][c]:
                    self.display.fill_rect(ox + c * bs, sy + r * bs, bs, bs, 1)
        if game.hold_used:
            draw_mini(self.display, "X", ox + 14, oy)

    def _draw_stats(self, game):
        y = config.BOTTOM_Y
        draw_mini(self.display, "SCR:" + str(game.score), 2, y)
        draw_mini(self.display, "LV:" + str(game.level), 2, y + 8)
        draw_mini(self.display, "LN:" + str(game.lines_cleared), 2, y + 16)

    def draw_pause_menu(self, selected=0):
        self.display.fill(0)
        self.display.text("PAUSED", 8, 10, 1)
        self.display.hline(8, 20, 48, 1)

        items = ["RESUME", "RETRY", "MENU"]
        ys = 30
        for i, item in enumerate(items):
            y = ys + i * 16
            if i == selected:
                self.display.text(">", 2, y, 1)
                self.display.text(item, 14, y, 1)
                self.display.hline(14, y + 9, len(item) * 8, 1)
            else:
                self.display.text(item, 14, y, 1)

        draw_mini(self.display, "L:UP R:DN", 2, 118)
        self.display.show()

    def draw_game_over(self, game, selected=0):
        self.display.fill(0)
        self.display.text("GAME", 16, 4, 1)
        self.display.text("OVER!", 12, 16, 1)
        self.display.hline(8, 26, 48, 1)

        draw_mini(self.display, "SCR:" + str(game.score), 4, 32)
        draw_mini(self.display, "LV:" + str(game.level), 4, 40)
        draw_mini(self.display, "LN:" + str(game.lines_cleared), 4, 48)

        items = ["RETRY", "MENU"]
        ys = 62
        for i, item in enumerate(items):
            y = ys + i * 16
            if i == selected:
                self.display.text(">", 2, y, 1)
                self.display.text(item, 14, y, 1)
                self.display.hline(14, y + 9, len(item) * 8, 1)
            else:
                self.display.text(item, 14, y, 1)

        self.display.show()
