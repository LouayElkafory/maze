"""
camera.py
Scroll camera + lighting system (Fog of War) for Curse of the Pyramids.
"""

import pygame
import random
from src.constants import SCREEN_W, SCREEN_H, MAZE_OFF_Y

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

        # centering offset when maze is smaller than screen
        self._mx = max(0, (VP_W - world_w) // 2)
        self._my = max(0, (VP_H - world_h) // 2)

        # ── Lighting system (Fog of War) ────────────────────────────────
        self.darkness = pygame.Surface((VP_W, VP_H), pygame.SRCALPHA)

        self.light_radius = 140        # inner visible area
        self.soft_radius  = 220        # fade area

        # ── Camera shake ────────────────────────────────────────────────
        self.shake = 0
        self.shake_intensity = 2

    # ────────────────────────────────────────────────────────────────────────

    def update(self, player_wx: float, player_wy: float, ts: int):

        half = ts * 0.5

        # ── horizontal ───────────────────────────────────────────────
        if self.world_w > VP_W:
            target_x = player_wx + half - VP_W * 0.5
            self.cam_x = max(0.0, min(target_x, self.world_w - VP_W))
        else:
            self.cam_x = 0.0

        # ── vertical ─────────────────────────────────────────────────
        if self.world_h > VP_H:
            target_y = player_wy + half - VP_H * 0.5
            self.cam_y = max(0.0, min(target_y, self.world_h - VP_H))
        else:
            self.cam_y = 0.0

        # ── screen shake decay ────────────────────────────────────────
        if self.shake > 0:
            self.shake -= 1

    # ────────────────────────────────────────────────────────────────────────

    def world_to_screen(self, wx: float, wy: float):
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
    # 🔥 LIGHTING SYSTEM (Fog of War)
    # ────────────────────────────────────────────────────────────────────────

    def apply_lighting(self, screen: pygame.Surface, player_screen_pos: tuple):

        # full darkness layer
        self.darkness.fill((0, 0, 0, 230))

        px, py = player_screen_pos

        # inner bright circle (clear vision)
        pygame.draw.circle(
            self.darkness,
            (0, 0, 0, 0),
            (px, py),
            self.light_radius
        )

        # soft fade outer glow (less harsh edge)
        pygame.draw.circle(
            self.darkness,
            (0, 0, 0, 120),
            (px, py),
            self.soft_radius
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