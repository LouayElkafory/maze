"""
main.py
Entry point for Curse of the Pyramids.

Run this file to launch the game:
    python main.py
"""
import sys
import pygame
from src.game import Game


def main():
    pygame.init()
    pygame.mixer.init()

    game = Game()
    game.run()

    sys.exit(0)


if __name__ == "__main__":
    main()
