"""
camera.py
Scroll camera + lighting system (Fog of War) for Curse of the Pyramids.
Enhanced with smoother easing and improved viewport handling.
"""

import pygame
import random
import math
from src.constants import SCREEN_W, SCREEN_H, MAZE_OFF_Y, TILE_SIZE

# ── Viewport ────────────────────────────────────────────────────────────────
VP_LEFT = 0
VP_TOP  = MAZE_OFF_Y
VP_W    = SCREEN_W
VP_H    = SCREEN_H - MAZE_OFF_Y


class Camera:

    def __init__(self, world_w: int, world_h: int):
        self.world_w = world_w
        self.world_h = world_h

        self.cam_x = 0.0
        self.cam_y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0

        # centering offset when maze is smaller than screen
        self._mx = max(0, (VP_W - world_w) // 2)
        self._my = max(0, (VP_H - world_h) // 2)

        # ── Camera easing (smoother follow) ────────────────────────────
        self.easing_factor = 0.10  # Lower = smoother follow (0.05-0.15)

        # ── Lighting system (Fog of War) - scaled for bigger tiles ─────
        self.darkness = pygame.Surface((VP_W, VP_H), pygame.SRCALPHA)

        # Scale lighting radii with tile size
        self.light_radius = int(TILE_SIZE * 2.5)    # 175 at 70 tile size
        self.soft_radius  = int(TILE_SIZE * 2.8)    # 196 at 70 tile size

        # ── Camera shake ────────────────────────────────────────────────
        self.shake = 0
        self.shake_intensity = 3

    # ────────────────────────────────────────────────────────────────────────

    def update(self, player_wx: float, player_wy: float, ts: int):
        """
        Enhanced camera update with smooth easing and proper bounds checking.
        """

        half = ts * 0.5

        # ── Calculate target position (centered on player) ─────────────
        if self.world_w > VP_W:
            self.target_x = player_wx + half - VP_W * 0.5
            self.target_x = max(0.0, min(self.target_x, self.world_w - VP_W))
        else:
            self.target_x = 0.0

        if self.world_h > VP_H:
            self.target_y = player_wy + half - VP_H * 0.5
            self.target_y = max(0.0, min(self.target_y, self.world_h - VP_H))
        else:
            self.target_y = 0.0

        # ── Smooth easing to target (exponential smoothing) ────────────
        self.cam_x = self.cam_x + (self.target_x - self.cam_x) * self.easing_factor
        self.cam_y = self.cam_y + (self.target_y - self.cam_y) * self.easing_factor

        # ── Screen shake decay ────────────────────────────────────────
        if self.shake > 0:
            self.shake -= 1

    # ────────────────────────────────────────────────────────────────────────

    def world_to_screen(self, wx: float, wy: float):
        """Convert world coordinates to screen coordinates."""
        sx = wx - self.cam_x + self._mx + VP_LEFT
        sy = wy - self.cam_y + self._my + VP_TOP

        # apply shake
        if self.shake > 0:
            sx += random.randint(-self.shake_intensity, self.shake_intensity)
            sy += random.randint(-self.shake_intensity, self.shake_intensity)

        return int(sx), int(sy)

    # ────────────────────────────────────────────────────────────────────────

    def apply(self, screen: pygame.Surface, world_surface: pygame.Surface):
        bx = int(-self.cam_x + self._mx + VP_LEFT)
        by = int(-self.cam_y + self._my + VP_TOP)
        screen.blit(world_surface, (bx, by))

    # ────────────────────────────────────────────────────────────────────────
    # 🔥 LIGHTING SYSTEM (Fog of War) - Improved gradient
    # ────────────────────────────────────────────────────────────────────────

    def apply_lighting(self, screen: pygame.Surface, player_screen_pos: tuple):
        """
        Apply smooth lighting and fog of war effect around the player.
        Uses radial gradient for better visual quality.
        """

        # full darkness layer
        self.darkness.fill((0, 0, 0, 240))

        px, py = player_screen_pos

        # inner bright circle (clear vision)
        pygame.draw.circle(
            self.darkness,
            (0, 0, 0, 0),
            (px, py),
            self.light_radius
        )

        # intermediate fade (smoother transition)
        fade_steps = 5
        for i in range(fade_steps, 0, -1):
            radius = self.light_radius + (self.soft_radius - self.light_radius) * (i / fade_steps)
            alpha = int(100 * (i / fade_steps))
            pygame.draw.circle(
                self.darkness,
                (0, 0, 0, alpha),
                (px, py),
                int(radius)
            )

        screen.blit(self.darkness, (0, 0))

    # ────────────────────────────────────────────────────────────────────────

    def trigger_shake(self, intensity: int = 10):
        """
        Call this from enemy when it gets close to player.
        """
        self.shake = intensity

    # ────────────────────────────────────────────────────────────────────────

    @property
    def viewport_rect(self):
        return pygame.Rect(VP_LEFT, VP_TOP, VP_W, VP_H)