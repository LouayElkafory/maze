"""
game.py
Main game state machine for Curse of the Pyramids.

State flow:
    MENU  ──[Play]──►  PLAYING  ──[P / pause btn]──►  PAUSED
                          │                               │
                     [reach goal]                   [Resume]──►  PLAYING
                          │                               │
                          ▼                          [Menu]──►  MENU
                         WIN ──[Next Level]──►  PLAYING (bigger maze)
                          │
                     [caught]
                          │
                          ▼
                         LOSE ──[Retry]──►  PLAYING (same seed / layout)
                          └──[Menu]──►  MENU
"""
import time
from typing import Optional
import pygame
from src.constants import (
    SCREEN_W, SCREEN_H, FPS, DARK_BG,
    GOLD, WHITE, BLACK, SAND,
    STATE_MENU, STATE_PLAY, STATE_PAUSE, STATE_WIN, STATE_LOSE, STATE_SETTINGS,
)
from src.camera         import Camera
from src.maze_generator import MazeConfig
from src.asset_loader   import Assets
from src.maze           import Maze
from src.player         import Player
from src.enemy          import Enemy
from src.audio          import AudioManager
from src.ui             import (
    Button, HUD,
    draw_start_screen, draw_pause_screen,
    draw_win_screen, draw_lose_screen, draw_settings_screen,
    fade_out, load_font,
)


class Game:
    """
    Top-level game object.

    Owns the pygame display, clock, all subsystems, and the main loop.
    Call game.run() to start.
    """

    def __init__(self):
        # ── Display ───────────────────────────────────────────────────────────
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("⚱ Curse of the Pyramids")
        self.clock = pygame.time.Clock()

        # ── Static subsystems ─────────────────────────────────────────────────
        self.assets = Assets()
        self.audio  = AudioManager()
        self.hud    = HUD(self.assets)

        # ── Level state ───────────────────────────────────────────────────────
        self.level = 1
        self.cfg   = MazeConfig(self.level)
        self._build_level_objects()

        # ── Game state ────────────────────────────────────────────────────────
        self.state   = STATE_MENU
        self.running = True

        # ── Game timer ────────────────────────────────────────────────────────
        self._t_start: Optional[float] = None
        self._elapsed: int             = 0

        # ── Fonts ─────────────────────────────────────────────────────────────
        self.font    = load_font(22, bold=True)
        self.font_sm = load_font(16)

        # ── Buttons ───────────────────────────────────────────────────────────
        self._build_buttons()

    # ─────────────────────────────────────────────────────────────────────────
    # Level object helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _build_level_objects(self):
        """
        Create/recreate Maze, Player and Enemy from self.cfg.
        Also caches the treasure sprite at the correct size and position.
        """
        cfg = self.cfg
        self.maze   = Maze(self.assets, cfg)
        self.player = Player(self.assets, cfg)
        
        # Multiple enemy support: add a second enemy if level >= 4
        self.enemies = [Enemy(self.assets, cfg, level=self.level)]
        if self.level >= 4:
            self.enemies.append(Enemy(self.assets, cfg, level=self.level, start_pos=cfg.enemy_start_2))

        # Screen dimensions of the entire world (maze)
        self.world_w = cfg.cols * cfg.tile_size
        self.world_h = cfg.rows * cfg.tile_size
        self.camera  = Camera(self.world_w, self.world_h)

        # Treasure rendering cache (world coordinates + scaled sprite)
        ts = cfg.tile_size
        tc, tr = cfg.treasure_pos
        self._tx = tc * ts  # World X
        self._ty = tr * ts  # World Y
        self._treasure_sprite = pygame.transform.smoothscale(
            self.assets.treasure, (ts, ts))

    # ─────────────────────────────────────────────────────────────────────────
    # Button construction
    # ─────────────────────────────────────────────────────────────────────────

    def _build_buttons(self):
        """
        Build all button sets with dynamically computed positions so they
        stay centred regardless of screen size, and each screen only
        receives the buttons that belong to it.
        """
        cx   = SCREEN_W // 2
        bw   = 210          # button width
        bh   = 48           # button height
        gap  = 12           # vertical gap between buttons
        half = bw // 2

        def _btn(y, label, **kw):
            """Shorthand: horizontally-centred button at row y."""
            return Button((cx - half, y, bw, bh), label, font_size=24, **kw)

        def _group_ys(n, anchor_pct):
            """
            Return the y-coordinates for a column of *n* buttons whose
            combined block is centred at (anchor_pct * SCREEN_H).
            """
            total_h = n * bh + (n - 1) * gap
            start   = int(SCREEN_H * anchor_pct) - total_h // 2
            return [start + i * (bh + gap) for i in range(n)]

        # ── Start menu: Play / Settings / Exit ────────────────────────────────
        # start menu.png has "START" and "SETTINGS" banners baked at ~45-70%.
        # Our buttons must sit BELOW those image elements (bottom 20% is clear).
        sy = _group_ys(3, 0.83)
        self.start_btns = [
            _btn(sy[0], "▶   Play"),
            _btn(sy[1], "⚙   Settings",
                 color=(70, 70, 140), hover_color=(110, 110, 210)),
            _btn(sy[2], "✕   Exit",
                 color=(140, 40, 40), hover_color=(200, 65, 65)),
        ]

        # ── Pause: Resume / Main Menu ─────────────────────────────────────────
        # Dark card occupies y≈230-470. Buttons sit just below it.
        py = _group_ys(2, 0.73)
        self.pause_btns = [
            _btn(py[0], "▶   Resume"),
            _btn(py[1], "⌂   Main Menu",
                 color=(70, 70, 150), hover_color=(110, 110, 210)),
        ]

        # ── Win: Next Level / Main Menu ───────────────────────────────────────
        # win.png scroll occupies top ~65%; buttons go in the clear bottom area.
        wy = _group_ys(2, 0.78)
        self.win_btns = [
            _btn(wy[0], "▶   Next Level"),
            _btn(wy[1], "⌂   Main Menu",
                 color=(70, 70, 150), hover_color=(110, 110, 210)),
        ]

        # ── Lose: Retry / Main Menu ───────────────────────────────────────────
        ly = _group_ys(2, 0.78)
        self.lose_btns = [
            _btn(ly[0], "↺   Retry"),
            _btn(ly[1], "⌂   Main Menu",
                 color=(70, 70, 150), hover_color=(110, 110, 210)),
        ]

        # ── Settings: single Back button ──────────────────────────────────────
        self.settings_btns = [
            _btn(int(SCREEN_H * 0.78), "◀   Back"),
        ]

    # ─────────────────────────────────────────────────────────────────────────
    # State transitions
    # ─────────────────────────────────────────────────────────────────────────

    def _start_game(self, level: int = 1):
        """Begin (or restart) a game session at *level* with a fresh maze."""
        self.level = level
        self.cfg   = MazeConfig(level)    # generate the new (larger) maze
        self._build_level_objects()        # rebuild Maze / Player / Enemy
        self._t_start = time.time()
        self._elapsed = 0

        self.audio.play_music()
        fade_out(self.screen)
        self.state = STATE_PLAY

    def _go_menu(self):
        """Return to the main menu."""
        self.audio.stop_music()
        fade_out(self.screen)
        self.state = STATE_MENU

    def _pause(self):
        self.state = STATE_PAUSE
        self.audio.pause_music()

    def _resume(self):
        # Recalibrate start time so elapsed stays accurate across pauses
        self._t_start = time.time() - self._elapsed
        self.state    = STATE_PLAY
        self.audio.resume_music()

    # ─────────────────────────────────────────────────────────────────────────
    # Event handlers (one per state)
    # ─────────────────────────────────────────────────────────────────────────

    def _on_menu(self, event):
        if self.start_btns[0].is_clicked(event):    # Play
            self._start_game(level=1)
        elif self.start_btns[1].is_clicked(event):  # Settings
            self.state = STATE_SETTINGS
        elif self.start_btns[2].is_clicked(event):  # Exit
            self.running = False

    def _on_settings(self, event):
        """Settings screen — only the Back button is active here."""
        if self.settings_btns[0].is_clicked(event):
            self.state = STATE_MENU
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_MENU

    def _on_play(self, event):
        # Pause via HUD icon
        if self.hud.pause_clicked(event):
            self._pause()
            return

        if event.type == pygame.KEYDOWN:
            # Pause via keyboard
            if event.key in (pygame.K_p, pygame.K_ESCAPE):
                self._pause()
                return

            # Movement — WASD and arrow keys
            direction = {
                pygame.K_UP:    "up",    pygame.K_w: "up",
                pygame.K_DOWN:  "down",  pygame.K_s: "down",
                pygame.K_LEFT:  "left",  pygame.K_a: "left",
                pygame.K_RIGHT: "right", pygame.K_d: "right",
            }.get(event.key)
            if direction:
                self.player.move(direction, self.maze)

    def _on_pause(self, event):
        if self.pause_btns[0].is_clicked(event):   # Resume
            self._resume()
        elif self.pause_btns[1].is_clicked(event):  # Main Menu
            self._go_menu()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_p, pygame.K_ESCAPE):
                self._resume()

    def _on_win(self, event):
        if self.win_btns[0].is_clicked(event):     # Next Level → bigger maze
            self._start_game(level=self.level + 1)
        elif self.win_btns[1].is_clicked(event):    # Main Menu
            self._go_menu()

    def _on_lose(self, event):
        if self.lose_btns[0].is_clicked(event):    # Retry → same seed/layout
            self._start_game(level=self.level)
        elif self.lose_btns[1].is_clicked(event):   # Main Menu
            self._go_menu()

    # ─────────────────────────────────────────────────────────────────────────
    # Update (game logic — only while PLAYING)
    # ─────────────────────────────────────────────────────────────────────────

    def _update(self):
        # Accumulate elapsed time
        if self._t_start is not None:
            self._elapsed = int(time.time() - self._t_start)

        # Move entities (smooth world pixel interpolation)
        self.player.update()
        for enemy in self.enemies:
            enemy.update(self.maze, self.player.grid_pos)

        # Update camera based on new player smooth position
        self.camera.update(self.player.px, self.player.py, self.cfg.tile_size)

        # ── Win: player reached the treasure ──────────────────────────────────
        if self.player.grid_pos == self.cfg.treasure_pos:
            self.state = STATE_WIN
            self.audio.play_win()
            return

        # ── Lose: any enemy caught the player ────────────────────────────────
        for enemy in self.enemies:
            if enemy.grid_pos == self.player.grid_pos:
                self.state = STATE_LOSE
                self.audio.play_lose()
                break

    # ─────────────────────────────────────────────────────────────────────────
    # Drawing
    # ─────────────────────────────────────────────────────────────────────────

    def _draw_game(self):
        self.screen.fill(DARK_BG)

        self.maze.draw(self.screen, self.camera)

        tx, ty = self.camera.world_to_screen(self._tx, self._ty)
        self.screen.blit(self._treasure_sprite, (tx, ty))

        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)

        self.hud.draw(self.screen, self._elapsed, self.level)

        # 🔥 PLAYER SCREEN POS FOR LIGHTING
        player_sx, player_sy = self.camera.world_to_screen(
            self.player.px,
            self.player.py
        )

        # 🌫️ FOG OF WAR
        self.camera.apply_lighting(
            self.screen,
            (player_sx, player_sy)
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Main loop
    # ─────────────────────────────────────────────────────────────────────────

    def run(self):
        while self.running:
            # ── Events ───────────────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if   self.state == STATE_MENU:     self._on_menu(event)
                elif self.state == STATE_SETTINGS: self._on_settings(event)
                elif self.state == STATE_PLAY:     self._on_play(event)
                elif self.state == STATE_PAUSE:    self._on_pause(event)
                elif self.state == STATE_WIN:      self._on_win(event)
                elif self.state == STATE_LOSE:     self._on_lose(event)

            # ── Logic update ─────────────────────────────────────────────────
            if self.state == STATE_PLAY:
                self._update()

            # ── Render ───────────────────────────────────────────────────────
            if self.state == STATE_MENU:
                # Menu screen: only start_btns are drawn here
                draw_start_screen(self.screen, self.assets, self.start_btns)

            elif self.state == STATE_SETTINGS:
                # Settings screen: only settings_btns are drawn here
                draw_settings_screen(self.screen, self.assets, self.settings_btns)

            elif self.state in (STATE_PLAY, STATE_PAUSE, STATE_WIN, STATE_LOSE):
                # All in-game states share the same game-view base layer
                self._draw_game()

                if self.state == STATE_PAUSE:
                    # Pause: only pause_btns visible
                    draw_pause_screen(self.screen, self.assets, self.pause_btns)
                elif self.state == STATE_WIN:
                    # Win: only win_btns visible
                    draw_win_screen(self.screen, self.assets, self.win_btns, self.level)
                elif self.state == STATE_LOSE:
                    # Lose: only lose_btns visible
                    draw_lose_screen(self.screen, self.assets, self.lose_btns)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
