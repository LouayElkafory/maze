"""
enemy.py
Mummy enemy AI using A* pathfinding.

px / py are stored in WORLD coordinates. The Camera provides screen
coordinates during the draw() step.
"""
import pygame
from src.constants import (
    ENEMY_PATH_INTERVAL_BASE, ENEMY_MOVE_DELAY_BASE, ENEMY_SPEED_SCALE,
)
from src.pathfinding import a_star


class Enemy:
    """
    The mummy enemy.

    Parameters
    ----------
    assets : Assets     – shared asset container
    cfg    : MazeConfig – layout for the current level
    level  : int        – current level (1-based); higher → faster
    """

    LERP_SPEED = 0.20

    def __init__(self, assets, cfg, level: int = 1, start_pos: tuple = None):
        self.assets = assets
        self._apply_cfg(cfg, level, start_pos)

    # ── Config application ────────────────────────────────────────────────────

    def _apply_cfg(self, cfg, level: int, start_pos: tuple = None):
        self.tile_size = cfg.tile_size
        self.cols      = cfg.cols
        self.rows      = cfg.rows

        # Use provided start_pos or default to cfg.enemy_start
        self.col, self.row = start_pos if start_pos else cfg.enemy_start

        self.direction     = "down"
        self.path: list    = []

        self._path_timer = 0
        self._move_timer = 0

        # World-space pixel position
        self.px = float(self.col * self.tile_size)
        self.py = float(self.row * self.tile_size)

        # Speed scaling
        self.level = level
        scale = ENEMY_SPEED_SCALE ** (level - 1)
        self.path_interval = max(12, int(ENEMY_PATH_INTERVAL_BASE * scale))
        self.move_delay    = max(6,  int(ENEMY_MOVE_DELAY_BASE    * scale))

        # Pre-scale sprites
        ts = self.tile_size
        self._sprites = {
            d: pygame.transform.smoothscale(self.assets.mummy[d], (ts, ts))
            for d in ("up", "down", "left", "right", "idle")
        }

    # ── Public API ────────────────────────────────────────────────────────────

    def reset(self, cfg, level: int = 1, start_pos: tuple = None):
        self._apply_cfg(cfg, level, start_pos)

    def update(self, maze, player_pos: tuple):
        """Called once per frame while PLAYING."""
        self._path_timer += 1
        self._move_timer += 1

        # ── Recalculate A* path ───────────────────────────────────────────────
        if self._path_timer >= self.path_interval or not self.path:
            self._path_timer = 0
            self.path = a_star(
                maze.grid,
                (self.col, self.row),
                player_pos,
                self.cols, self.rows,
            )

        # ── Move one step ─────────────────────────────────────────────────────
        if self._move_timer >= self.move_delay and self.path:
            self._move_timer = 0
            nc, nr = self.path.pop(0)
            dc, dr = nc - self.col, nr - self.row
            if   dc ==  1: self.direction = "right"
            elif dc == -1: self.direction = "left"
            elif dr ==  1: self.direction = "down"
            elif dr == -1: self.direction = "up"
            self.col, self.row = nc, nr

        # ── Smooth pixel interpolation (world space) ──────────────────────────
        target_x = float(self.col * self.tile_size)
        target_y = float(self.row * self.tile_size)
        self.px += (target_x - self.px) * self.LERP_SPEED
        self.py += (target_y - self.py) * self.LERP_SPEED

    def draw(self, screen: pygame.Surface, camera):
        """Convert world pixel position to screen position, then blit."""
        sprite = self._sprites.get(self.direction, self._sprites["idle"])
        sx, sy = camera.world_to_screen(self.px, self.py)
        screen.blit(sprite, (sx, sy))

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def grid_pos(self) -> tuple:
        return (self.col, self.row)

    #-----
