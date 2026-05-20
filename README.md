<p align="center">
  <img src="https://img.shields.io/badge/platform-Raspberry%20Pi%20Pico%202-A22846?style=for-the-badge&logo=raspberrypi&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/language-MicroPython-306998?style=for-the-badge&logo=python&logoColor=white" alt="Language">
  <img src="https://img.shields.io/badge/display-SH1106%20OLED-000000?style=for-the-badge" alt="Display">
  <img src="https://img.shields.io/badge/license-GPL--3.0-blue?style=for-the-badge" alt="License">
</p>

# 🎮 Bastet Pico 2

**Bastard Tetris** — A Tetris clone where the AI deliberately picks the **worst possible piece** for the player. Built from scratch for the **Raspberry Pi Pico 2** with a 128×64 OLED display and 3-button controls.

> *"Bastet" stands for **Ba**stard **Tet**ris. Instead of choosing pieces randomly, the game's AI evaluates every possible piece across all rotations and positions, then selects the one that leaves you in the worst situation. Good luck.*

---

## ✨ Features

- **Bastet AI Engine** — Evaluates all 7 tetrominoes × 4 rotations × every column position per turn, then picks the worst piece with weighted probability (80% worst / 12% second-worst / 6% third / 2% fourth)
- **Portrait OLED Display** — 128×64 SH1106 display rotated 90° CW to create a 64×128 portrait viewport, maximizing vertical space for the Tetris board
- **3-Button Combo Controls** — Full game control with only 3 buttons using combo inputs for rotation and hard drop
- **Hold / Swap Mechanic** — Reserve a piece for strategic use (once per drop)
- **Ghost Piece** — Outlined preview showing where the current piece will land
- **Custom 4×6 Mini Font** — Hand-crafted bitmap font for compact stats rendering on the tiny display
- **11 Speed Levels** — Progressive difficulty with automatic level-up every 10 lines
- **NES-Style Scoring** — Line-clear multipliers scaled by level (100 / 300 / 500 / 800 points)
- **Zero Dependencies** — Runs entirely on the Pico 2 with no network or external services required

---

## 🛠 Hardware Requirements

| Component | Specification | Qty |
|-----------|--------------|:---:|
| **MCU** | Raspberry Pi Pico 2 (RP2350, MicroPython) | 1 |
| **Display** | SH1106 1.3" OLED, 128×64, I2C (4-pin: VCC, GND, SCL, SDA) | 1 |
| **Buttons** | 6mm tactile push buttons (momentary) | 3 |
| **Breadboard** | 830-point standard breadboard | 1 |
| **Jumper wires** | Male-to-male, assorted colors | ~10 |
| **USB cable** | Micro-USB (power + programming) | 1 |

---

## ⚡ Wiring Diagram

### OLED Display (I2C)

| OLED Pin | Pico Pin | GPIO | Physical Pin | Wire Color |
|----------|----------|------|:------------:|:----------:|
| **VCC** | 3V3(OUT) | — | Pin 36 | 🔴 Red |
| **GND** | GND | — | Pin 38 | ⚫ Black |
| **SCL** | GP1 | GPIO1 | Pin 2 | 🟡 Yellow |
| **SDA** | GP0 | GPIO0 | Pin 1 | 🔵 Blue |

**I2C Configuration:** Bus I2C0 · 400 kHz (Fast Mode) · Address `0x3C`

### Buttons

Each button connects between a GPIO pin and GND. **No external resistors needed** — internal pull-ups are enabled in software.

| Button | GPIO | Physical Pin | Function |
|--------|------|:------------:|----------|
| **LEFT** | GP2 | Pin 4 | Move left / Menu up |
| **MIDDLE** | GP3 | Pin 5 | Hold-swap / Select / Pause (long press) |
| **RIGHT** | GP4 | Pin 6 | Move right / Menu down |

```
Button wiring (each button):

   Pico GPIO ─────┐
                   │
              ┌────┴────┐
              │  BUTTON  │
              └────┬────┘
                   │
   Pico GND ──────┘

   Internal pull-up: 3.3V ──[~50kΩ]── GPIO
   Released → HIGH (1)
   Pressed  → LOW  (0)
```

### Full Pin Map

```
Raspberry Pi Pico 2 — Pin Assignment
═══════════════════════════════════════

           ┌───────────────────┐
  GP0  ────┤ 1   (I2C SDA)  40 ├──── VBUS (5V USB)
  GP1  ────┤ 2   (I2C SCL)  39 ├──── VSYS
  GND  ────┤ 3              38 ├──── GND ◄── OLED GND
  GP2  ────┤ 4   (LEFT)     37 ├────
  GP3  ────┤ 5   (MIDDLE)   36 ├──── 3V3(OUT) ◄── OLED VCC
  GP4  ────┤ 6   (RIGHT)    35 ├────
  GP5  ────┤ 7              34 ├────
  GND  ────┤ 8              33 ├──── GND
  GP6  ────┤ 9              32 ├────
  GP7  ────┤ 10             31 ├────
           ┤ ...            ...├
           └───────────────────┘

  Used pins:
  ● GP0  → I2C0 SDA (OLED data)
  ● GP1  → I2C0 SCL (OLED clock)
  ● GP2  → LEFT button
  ● GP3  → MIDDLE button
  ● GP4  → RIGHT button
  ● 3V3  → OLED VCC (power)
  ● GND  → OLED GND + all buttons GND
```

> **Note:** The display is physically mounted in landscape orientation but software-rotated 90° clockwise to portrait mode (64×128). Mount the display accordingly.

---

## 🎮 Controls

| Input | Action |
|-------|--------|
| **LEFT** | Move piece left |
| **RIGHT** | Move piece right |
| **MIDDLE** (tap) | Hold / swap piece |
| **MIDDLE + RIGHT** (simultaneous) | Rotate clockwise |
| **MIDDLE + LEFT** (simultaneous) | Rotate counter-clockwise |
| **ALL THREE** (simultaneous) | Hard drop |
| **MIDDLE** (hold 500ms) | Open pause menu |

---

## 🧠 How the Bastet AI Works

The Bastet algorithm runs every time a new piece needs to be spawned:

1. **Simulate** — For each of the 7 tetrominoes, test every rotation (up to 4) at every valid column position
2. **Evaluate** — Score each simulated board state using a weighted heuristic:
   - **Aggregate Height** (×−0.5) — Penalizes tall stacks
   - **Hole Count** (×−3.5) — Heavily penalizes buried gaps
   - **Bumpiness** (×−0.2) — Penalizes uneven surfaces
   - **Complete Lines** (×+1.0) — Rewards line clears
3. **Rank** — Find each piece's *best achievable* score (the player's optimal placement)
4. **Select** — Pick from the bottom of the ranking with weighted probability:

| Rank | Probability | Meaning |
|:----:|:-----------:|---------|
| Worst | 80% | Almost always chosen |
| 2nd worst | 12% | Occasional mercy |
| 3rd worst | 6% | Rare reprieve |
| 4th worst | 2% | Near-miracle |

This ensures the player *usually* gets the worst possible piece, but occasional variance keeps the game technically beatable.

---

## 📁 Project Structure

```
bastet_micropython/
├── boot.py              # GC initialization on power-up
├── main.py              # Entry point — game loop, menu routing
├── config.py            # Hardware pins, I2C settings, game constants
├── display.py           # 90° CW rotation wrapper for SH1106
├── game/
│   ├── __init__.py
│   ├── engine.py        # Tetris mechanics + Bastet AI piece selection
│   ├── input.py         # 3-button polling, combos, debounce, long-press
│   ├── pieces.py        # 7 tetrominoes × 4 rotation states (4×4 matrices)
│   └── renderer.py      # Board/UI drawing, ghost piece, custom mini font
├── ui/
│   ├── __init__.py
│   ├── menu.py          # Main menu with animated cursor
│   └── screens.py       # Splash screen and about screen
├── lib/
│   └── sh1106.py        # SH1106 I2C/SPI display driver (MIT, robert-hh)
├── LICENSE              # GPL-3.0
└── README.md
```

---

## 🚀 Installation & Deployment

### Prerequisites

- **MicroPython firmware** v1.24+ flashed onto the Pico 2
  - Download from [micropython.org/download/RPI_PICO2](https://micropython.org/download/RPI_PICO2/)
  - Hold **BOOTSEL** while connecting USB, drag the `.uf2` file to the mounted drive
- **Thonny IDE** (recommended) or any MicroPython-compatible tool (mpremote, rshell, ampy)

### Step-by-Step Setup

#### 1. Flash MicroPython Firmware

```bash
# Hold BOOTSEL button on the Pico 2 while plugging in USB
# A drive named RPI-RP2 will appear
# Copy the downloaded .uf2 firmware file to this drive
# The Pico will reboot automatically
```

#### 2. Wire the Hardware

Follow the [wiring diagram](#-wiring-diagram) above. Quick reference:

```
GP0 → SDA     GP1 → SCL     3V3 → VCC     GND → GND
GP2 → LEFT    GP3 → MIDDLE  GP4 → RIGHT   (each button to GND)
```

#### 3. Upload Files to the Pico

Using **Thonny IDE** (easiest method):

1. Open Thonny → Select interpreter: *MicroPython (Raspberry Pi Pico)*
2. Create the directory structure on the device:
   ```
   /lib/sh1106.py
   /game/__init__.py
   /game/engine.py
   /game/input.py
   /game/pieces.py
   /game/renderer.py
   /ui/__init__.py
   /ui/menu.py
   /ui/screens.py
   ```
3. Upload all `.py` files preserving the directory structure
4. Upload `boot.py`, `main.py`, `config.py`, and `display.py` to the root `/`

Using **mpremote** (command line):

```bash
# Install mpremote
pip install mpremote

# Create directories
mpremote mkdir :lib
mpremote mkdir :game
mpremote mkdir :ui

# Upload all files
mpremote cp lib/sh1106.py :lib/sh1106.py
mpremote cp game/__init__.py :game/__init__.py
mpremote cp game/engine.py :game/engine.py
mpremote cp game/input.py :game/input.py
mpremote cp game/pieces.py :game/pieces.py
mpremote cp game/renderer.py :game/renderer.py
mpremote cp ui/__init__.py :ui/__init__.py
mpremote cp ui/menu.py :ui/menu.py
mpremote cp ui/screens.py :ui/screens.py
mpremote cp boot.py :boot.py
mpremote cp main.py :main.py
mpremote cp config.py :config.py
mpremote cp display.py :display.py
```

#### 4. Power Cycle

Disconnect and reconnect USB (or use an external power source). The game starts automatically:

`boot.py` → `main.py` → Splash Screen → Main Menu

---

## 🔧 Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| No display output | VCC/GND reversed | Check wiring polarity |
| Image is sideways | Display not rotated | Mount the OLED physically at 90° CW |
| I2C scan returns empty | SDA/SCL swapped | Verify GP0↔SDA and GP1↔SCL |
| Button not responding | Missing GND connection | Check button GND leg |
| Combos not registering | Timing mismatch | Press both buttons simultaneously |
| `main.py` won't start | Import error | Run manually via REPL to see traceback |
| Can't connect to Pico | `main.py` in loop | Hold BOOTSEL while plugging in USB |
| `ModuleNotFoundError: sh1106` | Driver not uploaded | Copy `sh1106.py` to `/lib/` on the device |

---

## 📐 Configuration

All hardware and game parameters are defined in [`config.py`](config.py). Key values:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `I2C_FREQ` | 400,000 | I2C bus speed (Hz) |
| `BOARD_COLS` × `BOARD_ROWS` | 10 × 20 | Standard Tetris board |
| `BLOCK_SIZE` | 4 | Pixels per block |
| `LONG_PRESS_MS` | 500 | Hold duration for pause (ms) |
| `COMBO_WINDOW_MS` | 80 | Simultaneous press tolerance (ms) |
| `BASTET_WEIGHTS` | [80, 12, 6, 2] | AI piece selection distribution (%) |

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** — see the [LICENSE](LICENSE) file for details.

The SH1106 display driver (`lib/sh1106.py`) is licensed under **MIT** by [robert-hh](https://github.com/robert-hh/SH1106).
