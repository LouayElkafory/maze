"""
camera.py
Scroll camera for Curse of the Pyramids.

Tracks the player's world-space pixel position and computes how to offset
all world render calls so the player stays centred in the game viewport.

Coordinate conventions
----------------------
World  (wx, wy) — pixel inside the maze surface, (0,0) = tile (col=0, row=0)
Screen (sx, sy) — pixel on the pygame display surface
"""
import pygame
from src.constants import SCREEN_W, SCREEN_H, MAZE_OFF_Y

# ── Viewport dimensions (the game area below the HUD bar) ────────────────────
VP_LEFT = 0
VP_TOP  = MAZE_OFF_Y              # 72 px  (HUD bar height)
VP_W    = SCREEN_W                # 700 px
VP_H    = SCREEN_H - MAZE_OFF_Y  # 628 px


class Camera:
    """
    2-D scroll camera for a tile maze.

    Behaviour
    ---------
    • When the maze is SMALLER than the viewport, it is centred with static
      margins and no scrolling occurs (level 1 at ts=40 fits exactly).
    • When the maze is LARGER than the viewport, the camera clamps to
      [0, world_size − viewport_size] and smoothly follows the player.

    Usage
    -----
        camera = Camera(world_w, world_h)
        # each frame:
        camera.update(player.px, player.py, tile_size)
        # drawing:
        camera.apply(screen, maze_surface)           # maze
        sx, sy = camera.world_to_screen(wx, wy)     # entities / treasure
    """

    def __init__(self, world_w: int, world_h: int):
        """
        Parameters
        ----------
        world_w, world_h : maze surface dimensions in pixels (cols*ts × rows*ts)
        """
        self.world_w = world_w
        self.world_h = world_h
        self.cam_x   = 0.0    # world x currently at the viewport left edge
        self.cam_y   = 0.0    # world y currently at the viewport top  edge

        # Static centering margin when maze < viewport (no scrolling needed)
        self._mx = max(0, (VP_W - world_w) // 2)
        self._my = max(0, (VP_H - world_h) // 2)

    # ── Public API ────────────────────────────────────────────────────────────

    def update(self, player_wx: float, player_wy: float, ts: int):
        """
        Move the camera to centre on the player's world pixel position.

        Parameters
        ----------
        player_wx, player_wy : world pixel position of the player sprite (top-left)
        ts                   : tile size in pixels (used to offset to tile centre)
        """
        half = ts * 0.5   # aim at tile centre, not tile top-left

        if self.world_w > VP_W:
            target = player_wx + half - VP_W * 0.5
            self.cam_x = max(0.0, min(target, float(self.world_w - VP_W)))
        else:
            self.cam_x = 0.0  # maze fits horizontally → no scroll

        if self.world_h > VP_H:
            target = player_wy + half - VP_H * 0.5
            self.cam_y = max(0.0, min(target, float(self.world_h - VP_H)))
        else:
            self.cam_y = 0.0  # maze fits vertically → no scroll

    def world_to_screen(self, wx: float, wy: float) -> tuple:
        """
        Convert a world-space pixel coordinate to a screen-space coordinate.
        """
        sx = wx - self.cam_x + self._mx + VP_LEFT
        sy = wy - self.cam_y + self._my + VP_TOP
        return int(sx), int(sy)

    def apply(self, screen: pygame.Surface, world_surface: pygame.Surface):
        """
        Blit the entire world_surface onto *screen* at the camera-shifted
        position.  pygame clips the blit to the screen boundary automatically,
        so only the visible portion is actually drawn.
        """
        bx = int(-self.cam_x + self._mx + VP_LEFT)
        by = int(-self.cam_y + self._my + VP_TOP)
        screen.blit(world_surface, (bx, by))

    @property
    def viewport_rect(self) -> pygame.Rect:
        """Pygame Rect covering the full game viewport (below HUD)."""
        return pygame.Rect(VP_LEFT, VP_TOP, VP_W, VP_H)
