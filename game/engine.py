# engine.py — Tetris game engine with Bastet AI
# Bastet AI selects the worst piece for the player

import time

try:
    from urandom import getrandbits, randint
except ImportError:
    from random import getrandbits, randint

from game.pieces import PIECES, PIECE_NAMES
import config


class BastetGame:
    """Core game engine: board management, piece control, scoring, Bastet AI."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset game state."""
        self.board = [[0] * config.BOARD_COLS for _ in range(config.BOARD_ROWS)]
        self.score = 0
        self.lines_cleared = 0
        self.level = 0

        self.current_piece = None
        self.current_name = None
        self.current_rot = 0
        self.current_x = 0
        self.current_y = 0

        self.next_name = None
        self.next_piece = None

        self.hold_name = None
        self.hold_piece = None
        self.hold_used = False

        self.game_over = False
        self.paused = False

        self.last_drop = time.ticks_ms()
        self.drop_interval = config.LEVEL_SPEEDS[0]

        self.next_name = self._bastet_choose()
        self.next_piece = PIECES[self.next_name]
        self._spawn_piece()

    # === Bastet AI ===

    def _bastet_choose(self):
        """Pick the worst piece for the player.

        Evaluates all 7 tetrominoes at every rotation/position,
        ranks them by best achievable score, then selects from the
        bottom of the ranking with weighted probability.
        """
        scored = []

        for name in PIECE_NAMES:
            best_score = -999999
            piece_rots = PIECES[name]

            for rot in range(len(piece_rots)):
                shape = piece_rots[rot]
                for x in range(-2, config.BOARD_COLS + 2):
                    y = 0
                    while not self._check_collision_sim(shape, x, y + 1):
                        y += 1
                    if self._check_collision_sim(shape, x, y):
                        continue
                    test_board = self._simulate_place(shape, x, y)
                    s = self._evaluate_board(test_board)
                    if s > best_score:
                        best_score = s

            scored.append((name, best_score))

        scored.sort(key=lambda x: x[1])

        weights = config.BASTET_WEIGHTS
        r = randint(1, 100)
        cumulative = 0
        for i, w in enumerate(weights):
            cumulative += w
            if r <= cumulative and i < len(scored):
                return scored[i][0]

        return scored[0][0]

    def _check_collision_sim(self, shape, px, py):
        """Check collision for a shape at given position."""
        for row in range(4):
            for col in range(4):
                if shape[row][col]:
                    bx = px + col
                    by = py + row
                    if bx < 0 or bx >= config.BOARD_COLS:
                        return True
                    if by < 0 or by >= config.BOARD_ROWS:
                        return True
                    if self.board[by][bx]:
                        return True
        return False

    def _simulate_place(self, shape, px, py):
        """Place shape on a board copy and return it."""
        test = [row[:] for row in self.board]
        for row in range(4):
            for col in range(4):
                if shape[row][col]:
                    bx = px + col
                    by = py + row
                    if 0 <= bx < config.BOARD_COLS and 0 <= by < config.BOARD_ROWS:
                        test[by][bx] = 1
        return test

    def _evaluate_board(self, board):
        """Score a board state. Higher = better for the player."""
        total_height = 0
        holes = 0
        complete_lines = 0
        bumpiness = 0
        col_heights = []

        for col in range(config.BOARD_COLS):
            h = 0
            for row in range(config.BOARD_ROWS):
                if board[row][col]:
                    h = config.BOARD_ROWS - row
                    break
            col_heights.append(h)
            total_height += h

            found_block = False
            for row in range(config.BOARD_ROWS):
                if board[row][col]:
                    found_block = True
                elif found_block:
                    holes += 1

        for row in range(config.BOARD_ROWS):
            if all(board[row]):
                complete_lines += 1

        for i in range(len(col_heights) - 1):
            bumpiness += abs(col_heights[i] - col_heights[i + 1])

        return (config.WEIGHT_HEIGHT * total_height +
                config.WEIGHT_HOLES * holes +
                config.WEIGHT_BUMPINESS * bumpiness +
                config.WEIGHT_LINES * complete_lines)

    # === Piece management ===

    def _spawn_piece(self):
        """Activate next piece and generate a new next piece."""
        self.current_name = self.next_name
        self.current_piece = self.next_piece
        self.current_rot = 0
        self.current_x = config.BOARD_COLS // 2 - 2
        self.current_y = 0
        self.hold_used = False

        self.next_name = self._bastet_choose()
        self.next_piece = PIECES[self.next_name]

        shape = self.current_piece[self.current_rot]
        if self._check_collision_sim(shape, self.current_x, self.current_y):
            self.game_over = True

        self.last_drop = time.ticks_ms()

    def get_current_shape(self):
        if self.current_piece is None:
            return None
        return self.current_piece[self.current_rot]

    def get_next_shape(self):
        if self.next_piece is None:
            return None
        return self.next_piece[0]

    def get_hold_shape(self):
        if self.hold_piece is None:
            return None
        return self.hold_piece[0]

    def get_ghost_y(self):
        """Calculate where the piece would land."""
        shape = self.get_current_shape()
        if shape is None:
            return self.current_y
        y = self.current_y
        while not self._check_collision_sim(shape, self.current_x, y + 1):
            y += 1
        return y

    # === Player controls ===

    def move_left(self):
        if self.game_over or self.paused:
            return False
        shape = self.get_current_shape()
        if not self._check_collision_sim(shape, self.current_x - 1, self.current_y):
            self.current_x -= 1
            return True
        return False

    def move_right(self):
        if self.game_over or self.paused:
            return False
        shape = self.get_current_shape()
        if not self._check_collision_sim(shape, self.current_x + 1, self.current_y):
            self.current_x += 1
            return True
        return False

    def move_down(self):
        """Move piece down one row. Lock if collision."""
        if self.game_over or self.paused:
            return False
        shape = self.get_current_shape()
        if not self._check_collision_sim(shape, self.current_x, self.current_y + 1):
            self.current_y += 1
            self.last_drop = time.ticks_ms()
            return True
        else:
            self._lock_and_clear()
            return False

    def rotate_cw(self):
        if self.game_over or self.paused:
            return False
        new_rot = (self.current_rot + 1) % 4
        shape = self.current_piece[new_rot]
        for dx in [0, -1, 1, -2, 2]:  # wall-kick offsets
            if not self._check_collision_sim(shape, self.current_x + dx, self.current_y):
                self.current_x += dx
                self.current_rot = new_rot
                return True
        return False

    def rotate_ccw(self):
        if self.game_over or self.paused:
            return False
        new_rot = (self.current_rot - 1) % 4
        shape = self.current_piece[new_rot]
        for dx in [0, -1, 1, -2, 2]:
            if not self._check_collision_sim(shape, self.current_x + dx, self.current_y):
                self.current_x += dx
                self.current_rot = new_rot
                return True
        return False

    def hold_swap(self):
        """Swap active piece with hold. Once per piece."""
        if self.game_over or self.paused or self.hold_used:
            return False

        self.hold_used = True
        old_hold_name = self.hold_name

        self.hold_name = self.current_name
        self.hold_piece = PIECES[self.hold_name]

        if old_hold_name is not None:
            self.current_name = old_hold_name
            self.current_piece = PIECES[self.current_name]
            self.current_rot = 0
            self.current_x = config.BOARD_COLS // 2 - 2
            self.current_y = 0

            shape = self.current_piece[self.current_rot]
            if self._check_collision_sim(shape, self.current_x, self.current_y):
                self.game_over = True
        else:
            self._spawn_piece()

        self.last_drop = time.ticks_ms()
        return True

    def hard_drop(self):
        """Instantly drop piece to bottom."""
        if self.game_over or self.paused:
            return
        shape = self.get_current_shape()
        while not self._check_collision_sim(shape, self.current_x, self.current_y + 1):
            self.current_y += 1
            self.score += 2
        self._lock_and_clear()

    def toggle_pause(self):
        self.paused = not self.paused

    # === Internal mechanics ===

    def _lock_and_clear(self):
        """Lock piece onto board, clear lines, spawn next."""
        shape = self.get_current_shape()

        for row in range(4):
            for col in range(4):
                if shape[row][col]:
                    bx = self.current_x + col
                    by = self.current_y + row
                    if 0 <= bx < config.BOARD_COLS and 0 <= by < config.BOARD_ROWS:
                        self.board[by][bx] = 1

        cleared = self._clear_lines()
        if cleared > 0:
            self.lines_cleared += cleared
            self.score += config.LINE_SCORES[min(cleared, 4)] * (self.level + 1)

            new_level = self.lines_cleared // config.LINES_PER_LEVEL
            if new_level != self.level:
                self.level = new_level
                idx = min(self.level, len(config.LEVEL_SPEEDS) - 1)
                self.drop_interval = config.LEVEL_SPEEDS[idx]

        self._spawn_piece()

    def _clear_lines(self):
        """Remove completed rows, insert empty rows at top."""
        cleared = 0
        row = config.BOARD_ROWS - 1
        while row >= 0:
            if all(self.board[row]):
                del self.board[row]
                self.board.insert(0, [0] * config.BOARD_COLS)
                cleared += 1
            else:
                row -= 1
        return cleared

    def update(self):
        """Per-frame update: gravity tick."""
        if self.game_over or self.paused:
            return
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_drop) >= self.drop_interval:
            self.move_down()
            self.last_drop = now
