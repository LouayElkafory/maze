"""
audio.py
Sound manager for Curse of the Pyramids.

Wraps pygame.mixer with graceful fallbacks so the game still runs if
audio files are missing or the mixer fails to initialise.
"""
import os
from typing import Optional
import pygame
from src.constants import SOUNDS_DIR


class AudioManager:
    """
    Manages background music (streaming) and one-shot SFX.

    Usage
    -----
        audio = AudioManager()
        audio.play_music()          # start BG loop
        audio.play_win()            # victory jingle + stops BG
        audio.pause_music()         # pause while game is paused
        audio.resume_music()        # unpause
    """

    _MUSIC = os.path.join(SOUNDS_DIR, "Main Sound TRack.mp3")
    _WIN   = os.path.join(SOUNDS_DIR, "win sound.mp3")
    _LOSE  = os.path.join(SOUNDS_DIR, "losing sound.mp3")

    def __init__(self):
        self._ok             = pygame.mixer.get_init() is not None
        self._music_loaded   = False
        self._win_sfx:  Optional[pygame.mixer.Sound] = None
        self._lose_sfx: Optional[pygame.mixer.Sound] = None

        if self._ok:
            self._win_sfx  = self._load_sfx(self._WIN,  volume=0.85)
            self._lose_sfx = self._load_sfx(self._LOSE, volume=0.85)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _load_sfx(self, path: str, volume: float = 1.0):
        if not os.path.exists(path):
            print(f"[Audio] ⚠ SFX not found: {path}")
            return None
        try:
            sfx = pygame.mixer.Sound(path)
            sfx.set_volume(volume)
            return sfx
        except pygame.error as exc:
            print(f"[Audio] ⚠ Could not load SFX '{path}': {exc}")
            return None

    # ── Background music ──────────────────────────────────────────────────────

    def play_music(self):
        """Load and start looping the background soundtrack."""
        if not self._ok:
            return
        if not os.path.exists(self._MUSIC):
            print(f"[Audio] ⚠ Music not found: {self._MUSIC}")
            return
        try:
            pygame.mixer.music.load(self._MUSIC)
            pygame.mixer.music.set_volume(0.45)
            pygame.mixer.music.play(-1)   # -1 = loop forever
            self._music_loaded = True
        except pygame.error as exc:
            print(f"[Audio] ⚠ Could not play music: {exc}")

    def pause_music(self):
        """Pause the background music (use during Pause screen)."""
        if self._ok and self._music_loaded:
            pygame.mixer.music.pause()

    def resume_music(self):
        """Resume paused background music."""
        if self._ok and self._music_loaded:
            pygame.mixer.music.unpause()

    def stop_music(self):
        """Stop music entirely (e.g. before playing a SFX)."""
        if self._ok:
            pygame.mixer.music.stop()
            self._music_loaded = False

    # ── Sound effects ─────────────────────────────────────────────────────────

    def play_win(self):
        """Stop music and play the victory sound effect."""
        self.stop_music()
        if self._win_sfx:
            self._win_sfx.play()

    def play_lose(self):
        """Stop music and play the defeat sound effect."""
        self.stop_music()
        if self._lose_sfx:
            self._lose_sfx.play()
