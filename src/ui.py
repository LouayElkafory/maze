"""
ui.py
All UI elements: Button class, HUD, screen-drawing functions, and transitions.

Keeps every visual concern (buttons, overlays, text rendering) out of game.py
so the game logic stays clean.
"""
import pygame
from src.constants import (
    SCREEN_W, SCREEN_H, MAZE_OFF_X, MAZE_OFF_Y,
    BLACK, WHITE, GOLD, DARK_GOLD, SAND, DARK_BG,
)


# ─── Font helper ─────────────────────────────────────────────────────────────

def load_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Return a Papyrus/Arial SysFont with a graceful fallback."""
    for name in ("Papyrus", "Palatino Linotype", "Georgia", "Arial"):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            continue
    return pygame.font.Font(None, size)


# ─── Button ───────────────────────────────────────────────────────────────────

class Button:
    """
    A styled rectangular button with hover glow and drop-shadow.

    Parameters
    ----------
    rect         : (x, y, w, h) or pygame.Rect
    text         : label string
    color        : normal background colour
    hover_color  : background colour when hovered
    text_color   : label colour
    font_size    : point size
    border_radius: corner rounding (px)
    """

    def __init__(
        self,
        rect,
        text: str,
        color        = GOLD,
        hover_color  = WHITE,
        text_color   = BLACK,
        font_size: int = 26,
        border_radius: int = 10,
    ):
        self.rect          = pygame.Rect(rect)
        self.text          = text
        self.color         = color
        self.hover_color   = hover_color
        self.text_color    = text_color
        self.border_radius = border_radius
        self.font          = load_font(font_size, bold=True)

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())

        # ── Drop shadow ──────────────────────────────────────────────────────
        shadow = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 90),
                         shadow.get_rect(), border_radius=self.border_radius)
        surface.blit(shadow, (self.rect.x + 4, self.rect.y + 5))

        # ── Body ─────────────────────────────────────────────────────────────
        col = self.hover_color if hovered else self.color
        pygame.draw.rect(surface, col, self.rect,
                         border_radius=self.border_radius)

        # ── Border ───────────────────────────────────────────────────────────
        border_col = WHITE if hovered else DARK_GOLD
        pygame.draw.rect(surface, border_col, self.rect,
                         width=2, border_radius=self.border_radius)

        # ── Hover glow ───────────────────────────────────────────────────────
        if hovered:
            glow = pygame.Surface(
                (self.rect.w + 12, self.rect.h + 12), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 220, 80, 55),
                             glow.get_rect(), border_radius=self.border_radius + 5)
            surface.blit(glow, (self.rect.x - 6, self.rect.y - 6))

        # ── Label ────────────────────────────────────────────────────────────
        label = self.font.render(self.text, True, self.text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))

    # ── Hit detection ─────────────────────────────────────────────────────────

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """Return True if a left MOUSEBUTTONDOWN event hit this button."""
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# ─── HUD (in-game overlay) ───────────────────────────────────────────────────

class HUD:
    """
    In-game heads-up display: title bar, timer, level label, pause button.
    """

    _PAUSE_BTN_RECT = pygame.Rect(SCREEN_W - 56, 17, 38, 38)

    def __init__(self, assets):
        self.assets   = assets
        self.font_lg  = load_font(24, bold=True)
        self.font_sm  = load_font(18)
        self.pause_rect = self._PAUSE_BTN_RECT

    def draw(self, surface: pygame.Surface, elapsed_secs: int, level: int):
        # ── Dark bar ─────────────────────────────────────────────────────────
        bar = pygame.Surface((SCREEN_W, MAZE_OFF_Y - 2), pygame.SRCALPHA)
        bar.fill((10, 6, 2, 210))
        surface.blit(bar, (0, 0))

        # ── Title ────────────────────────────────────────────────────────────
        title = self.font_lg.render("⚱  Curse of the Pyramids", True, GOLD)
        surface.blit(title, (MAZE_OFF_X, 8))

        # ── Timer ────────────────────────────────────────────────────────────
        mins, secs = divmod(elapsed_secs, 60)
        timer = self.font_sm.render(f"⏱ {mins:02d}:{secs:02d}", True, SAND)
        surface.blit(timer, (MAZE_OFF_X, 40))

        # ── Level ────────────────────────────────────────────────────────────
        lvl = self.font_sm.render(f"Level  {level}", True, GOLD)
        surface.blit(lvl, (SCREEN_W // 2 - lvl.get_width() // 2, 40))

        # ── Pause button ─────────────────────────────────────────────────────
        surface.blit(self.assets.pause_btn, self.pause_rect.topleft)

    def pause_clicked(self, event: pygame.event.Event) -> bool:
        """Return True if the pause-button icon was clicked."""
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.pause_rect.collidepoint(event.pos)
        )


# ─── Shared helpers ───────────────────────────────────────────────────────────

def _dim(surface: pygame.Surface, alpha: int = 150):
    """Draw a semi-transparent black rectangle over the full screen."""
    ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, alpha))
    surface.blit(ov, (0, 0))


def _centred_text(surface, text, font, colour, cy):
    """Render *text* centred horizontally at vertical position *cy*."""
    rendered = font.render(text, True, colour)
    surface.blit(rendered, (SCREEN_W // 2 - rendered.get_width() // 2, cy))


# ─── Screen drawing functions ─────────────────────────────────────────────────

def draw_start_screen(surface: pygame.Surface, assets, buttons: list):
    """Render the start menu (start menu.png + styled buttons)."""
    surface.blit(assets.start_menu, (0, 0))
    for btn in buttons:
        btn.draw(surface)


def draw_pause_screen(surface: pygame.Surface, assets, buttons: list):
    """
    Render the pause overlay on top of the frozen game view.
    Uses a clean dark card — we do NOT blit pause.png because it contains
    baked text ("Continue / PRESS SPACE") that contradicts our buttons.
    """
    # ── Dim the whole game view ───────────────────────────────────────────────
    _dim(surface, alpha=175)

    # ── Draw a centred card ───────────────────────────────────────────────────
    card_w, card_h = 340, 240
    card_x = SCREEN_W // 2 - card_w // 2
    card_y = SCREEN_H // 2 - card_h // 2 - 20

    card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    pygame.draw.rect(card, (30, 20, 10, 230), card.get_rect(), border_radius=14)
    pygame.draw.rect(card, DARK_GOLD, card.get_rect(), width=2, border_radius=14)
    surface.blit(card, (card_x, card_y))

    # ── "PAUSED" title inside the card ───────────────────────────────────────
    title_font = load_font(36, bold=True)
    title      = title_font.render("⏸  PAUSED", True, GOLD)
    surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, card_y + 22))

    # ── Divider ───────────────────────────────────────────────────────────────
    div_y = card_y + 78
    pygame.draw.line(surface, DARK_GOLD,
                     (card_x + 20, div_y), (card_x + card_w - 20, div_y), 1)

    # ── Hint text ────────────────────────────────────────────────────────────
    hint_font = load_font(16)
    hint      = hint_font.render("Press  P  or  ESC  to resume", True, SAND)
    surface.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, card_y + 92))

    for btn in buttons:
        btn.draw(surface)


def draw_win_screen(surface: pygame.Surface, assets, buttons: list, level: int):
    """Render the victory screen (win.png already contains title text)."""
    surface.blit(assets.win_bg, (0, 0))
    # No extra text — win.png already has "YOU WON!" and level info baked in.
    # A very light dim keeps button readability without hiding the image.
    _dim(surface, alpha=40)

    for btn in buttons:
        btn.draw(surface)


def draw_lose_screen(surface: pygame.Surface, assets, buttons: list):
    """Render the game-over / defeat screen (LOSE.png + buttons)."""
    surface.blit(assets.lose_bg, (0, 0))
    _dim(surface, alpha=70)

    for btn in buttons:
        btn.draw(surface)


# ─── Screen transition ────────────────────────────────────────────────────────

def fade_out(screen: pygame.Surface, colour=BLACK, steps: int = 20):
    """Fade the current screen to *colour* over *steps* frames."""
    snapshot = screen.copy()
    fade_surf = pygame.Surface((SCREEN_W, SCREEN_H))
    fade_surf.fill(colour)
    clock = pygame.time.Clock()
    for i in range(steps + 1):
        alpha = int(255 * i / steps)
        fade_surf.set_alpha(alpha)
        screen.blit(snapshot, (0, 0))
        screen.blit(fade_surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)


def draw_settings_screen(surface: pygame.Surface, assets, buttons: list):
    """
    Render the Settings screen.
    Reuses the start_menu image as background with a dark overlay so it
    looks consistent with the rest of the game UI.
    """
    # Background — same image as the start menu keeps visual consistency
    surface.blit(assets.start_menu, (0, 0))
    _dim(surface, alpha=170)

    # ── Title ────────────────────────────────────────────────────────────────
    title_font = load_font(42, bold=True)
    _centred_text(surface, "⚙  Settings", title_font, GOLD, SCREEN_H // 4)

    # ── Divider line ─────────────────────────────────────────────────────────
    line_y = SCREEN_H // 4 + 56
    pygame.draw.line(surface, DARK_GOLD,
                     (SCREEN_W // 4, line_y),
                     (SCREEN_W * 3 // 4, line_y), 2)

    # ── Placeholder info text ─────────────────────────────────────────────────
    info_font = load_font(20)
    _centred_text(surface, "Music and sound effects are always on.",
                  info_font, SAND, SCREEN_H // 4 + 80)
    _centred_text(surface, "Use  P  or  ESC  during gameplay to pause.",
                  info_font, SAND, SCREEN_H // 4 + 112)
    _centred_text(surface, "Arrow keys or WASD to move the explorer.",
                  info_font, SAND, SCREEN_H // 4 + 144)

    # ── Buttons ───────────────────────────────────────────────────────────────
    for btn in buttons:
        btn.draw(surface)

