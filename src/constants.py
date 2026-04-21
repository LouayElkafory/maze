"""
constants.py
Global configuration for Curse of the Pyramids.
Edit this file to tweak display size, tile size, colours, and gameplay tuning.
"""
import os
import sys

# ─── Paths ────────────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    BASE_DIR = sys._MEIPASS
else:
    # Running in a normal Python environment
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")

# ─── Display ──────────────────────────────────────────────────────────────────
TILE_SIZE  = 40           # Square size for each maze cell
COLS       = 15           # Default columns (scaled via level)
ROWS       = 15           # Default rows (scaled via level)

MAZE_OFF_X = 75           # Horizontal margin for centering logic
MAZE_OFF_Y = 100          # Top height for the HUD bar area

SCREEN_W   = 850          # Final display width
SCREEN_H   = 700          # Final display height
FPS        = 60

# ─── Colours ──────────────────────────────────────────────────────────────────
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
GOLD       = (212, 175,  55)
DARK_GOLD  = (139, 101,   8)
SAND       = (194, 154,  82)
RED        = (200,  30,  30)
GREEN      = ( 30, 200,  80)
DARK_BG    = ( 18,  12,   6)   # very dark desert-brown background

# ─── Game States ──────────────────────────────────────────────────────────────
STATE_MENU     = "MENU"
STATE_PLAY     = "PLAYING"
STATE_PAUSE    = "PAUSED"
STATE_WIN      = "WIN"
STATE_LOSE     = "LOSE"
STATE_SETTINGS = "SETTINGS"

# ─── Gameplay positions (col, row) ────────────────────────────────────────────
PLAYER_START  = (1, 1)    # top-left open cell
ENEMY_START   = (7, 7)    # centre of the maze
TREASURE_POS  = (13, 13)  # bottom-right open cell

# ─── Enemy AI tuning ──────────────────────────────────────────────────────────
# How many frames between A* recalculations (base = level 1)
ENEMY_PATH_INTERVAL_BASE = 45
# How many frames between enemy moves (base = level 1)
ENEMY_MOVE_DELAY_BASE    = 30
# Multiplier applied per level (< 1  →  faster each level)
ENEMY_SPEED_SCALE        = 0.85
