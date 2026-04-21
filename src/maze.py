"""
maze.py
Maze rendering — driven by a MazeConfig instance.

The maze surface is baked once per level (single blit = single draw call).
draw() now accepts a Camera so the viewport scrolls correctly.
"""
import pygame


class Maze:
    """Holds the current level's maze grid and handles tile rendering."""

    def __init__(self, assets, cfg):
        self.grid      = cfg.grid
        self.cols      = cfg.cols
        self.rows      = cfg.rows
        self.tile_size = cfg.tile_size
        self.assets    = assets

        # Bake every tile onto one surface — draw() is a single blit
        self._surface = pygame.Surface(
            (cfg.cols * cfg.tile_size, cfg.rows * cfg.tile_size))
        self._bake()

    def _bake(self):
        ts    = self.tile_size
        wall  = pygame.transform.smoothscale(self.assets.wall,  (ts, ts))
        floor = pygame.transform.smoothscale(self.assets.floor, (ts, ts))
        for row in range(self.rows):
            for col in range(self.cols):
                tile = wall if self.grid[row][col] == 1 else floor
                self._surface.blit(tile, (col * ts, row * ts))

    # ── Public API ────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface, camera):
        """
        Blit the maze surface at the correct camera-offset position.
        camera.apply() shifts the world surface so only the visible
        portion appears inside the game viewport.
        """
        camera.apply(screen, self._surface)

    def is_wall(self, col: int, row: int) -> bool:
        if col < 0 or col >= self.cols or row < 0 or row >= self.rows:
            return True
        return self.grid[row][col] == 1
