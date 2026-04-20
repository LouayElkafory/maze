"""
player.py
Player-controlled character for Curse of the Pyramids.

px / py are stored in WORLD coordinates (col * tile_size, row * tile_size).
The Camera converts them to screen coordinates inside draw().
"""
import pygame


class Player:
    """
    The player character.

    Attributes
    ----------
    col, row   : int   – current grid position
    direction  : str   – 'up' | 'down' | 'left' | 'right'
    px, py     : float – smooth WORLD pixel position (LERP toward grid target)
    """

    LERP_SPEED = 0.22

    def __init__(self, assets, cfg):
        self.assets = assets
        self._apply_cfg(cfg)

    # ── Config ────────────────────────────────────────────────────────────────

    def _apply_cfg(self, cfg):
        self.tile_size = cfg.tile_size
        self.col, self.row = cfg.player_start
        self.direction     = "down"

        # World-space pixel position (camera will convert to screen)
        self.px = float(self.col * self.tile_size)
        self.py = float(self.row * self.tile_size)

        # Pre-scale sprites to tile_size once per level
        ts = self.tile_size
        self._sprites = {
            d: pygame.transform.smoothscale(self.assets.player[d], (ts, ts))
            for d in ("up", "down", "left", "right")
        }

    def reset(self, cfg):
        """Reinitialise for a new level or retry."""
        self._apply_cfg(cfg)

    # ── Movement ──────────────────────────────────────────────────────────────

    def move(self, direction: str, maze) -> bool:
        self.direction = direction
        dc, dr = {"up": (0, -1), "down": (0, 1),
                  "left": (-1, 0), "right": (1, 0)}[direction]
        nc, nr = self.col + dc, self.row + dr
        if not maze.is_wall(nc, nr):
            self.col, self.row = nc, nr
            return True
        return False

    # ── Per-frame ─────────────────────────────────────────────────────────────

    def update(self):
        """LERP world-space pixel position toward the grid target."""
        target_x = float(self.col * self.tile_size)
        target_y = float(self.row * self.tile_size)
        self.px += (target_x - self.px) * self.LERP_SPEED
        self.py += (target_y - self.py) * self.LERP_SPEED

    def draw(self, screen: pygame.Surface, camera):
        """
        Convert world pixel position to screen position via the camera,
        then blit the directional sprite.
        """
        sx, sy = camera.world_to_screen(self.px, self.py)
        screen.blit(self._sprites[self.direction], (sx, sy))

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def grid_pos(self) -> tuple:
        return (self.col, self.row)
