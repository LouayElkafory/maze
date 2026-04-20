"""
asset_loader.py
Centralised image and sound loading for Curse of the Pyramids.

All assets are loaded ONCE at startup via the Assets class and shared
across all game modules — no module-level pygame.image.load() calls elsewhere.
"""
import os
import pygame
from src.constants import ASSETS_DIR, TILE_SIZE, SCREEN_W, SCREEN_H


# ─── Low-level helpers ────────────────────────────────────────────────────────

def load_image(filename: str, size: tuple = None, alpha: bool = True) -> pygame.Surface:
    """
    Load an image from the assets directory.

    Parameters
    ----------
    filename : str   – file name only, not a full path
    size     : tuple – (width, height) to scale to, or None to keep original
    alpha    : bool  – True → convert_alpha(), False → convert() (no transparency)

    Returns a pygame.Surface, or a bright-magenta placeholder on failure.
    """
    path = os.path.join(ASSETS_DIR, filename)
    try:
        img = pygame.image.load(path).convert_alpha() if alpha \
              else pygame.image.load(path).convert()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except (pygame.error, FileNotFoundError) as exc:
        print(f"[AssetLoader] ⚠ Could not load '{filename}': {exc}")
        surf = pygame.Surface(size or (TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill((255, 0, 255, 220))   # hot-pink placeholder
        return surf


# ─── Assets container ─────────────────────────────────────────────────────────

class Assets:
    """
    Loads and holds every game asset exactly once.

    Usage:
        assets = Assets()
        screen.blit(assets.wall, (x, y))
    """

    def __init__(self):
        tile = (TILE_SIZE, TILE_SIZE)
        full = (SCREEN_W, SCREEN_H)

        # ── Maze tiles ────────────────────────────────────────────────────────
        self.wall  = load_image("wall.png",  size=tile, alpha=False)
        self.floor = load_image("floor.png", size=tile, alpha=False)

        # ── Player directional sprites ────────────────────────────────────────
        self.player = {
            "up":    load_image("player up.png",       size=tile),
            "down":  load_image("player down.png",     size=tile),
            "left":  load_image("player go left.png",  size=tile),
            "right": load_image("player go right.png", size=tile),
        }

        # ── Mummy (enemy) directional sprites ─────────────────────────────────
        self.mummy = {
            "up":    load_image("mummy up.png",       size=tile),
            "down":  load_image("mummy down.png",     size=tile),
            "left":  load_image("mummy go left.png",  size=tile),
            "right": load_image("mummy go right.png", size=tile),
            "idle":  load_image("mummy.png",           size=tile),
        }

        # ── Goal ──────────────────────────────────────────────────────────────
        self.treasure = load_image("treasure.png", size=tile)

        # ── HUD pause button icon ─────────────────────────────────────────────
        self.pause_btn = load_image("PauseButton.png", size=(38, 38))

        # ── Full-screen screen backgrounds ────────────────────────────────────
        self.start_menu = load_image("start menu.png", size=full, alpha=False)
        self.pause_bg   = load_image("pause.png",      size=full, alpha=False)
        self.win_bg     = load_image("win.png",        size=full, alpha=False)
        self.lose_bg    = load_image("LOSE.png",       size=full, alpha=False)

        print("[AssetLoader] ✓ All assets loaded successfully.")
