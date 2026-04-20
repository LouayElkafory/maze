# Curse of the Pyramids — Full Rebuild Plan

## Overview

The existing code is a **single-file prototype** (~174 lines) with broken asset paths, no menus, no audio, no animations, and hardcoded player sprites. The Tiled map file (`labyrinthos_map.tmj`) exists but is unused. The goal is to rebuild this into a **complete, polished, modular Maze Game**.

---

## Asset Inventory

| Asset | File | Used For |
|---|---|---|
| Start Menu background | `start menu.png` | Start screen |
| Pause overlay | `pause.png` | Pause screen |
| Win screen | `win.png` | Victory screen |
| Lose screen | `LOSE.png` | Defeat screen |
| Settings | `setteings.png` | (decorative/UI) |
| Pause button | `PauseButton.png` | In-game HUD |
| Floor tile | `floor.png` | Maze floor |
| Wall tile | `wall.png` | Maze walls |
| Maze image | `maze.jpeg` | Background reference |
| Player sprites | `player up/down/left/right.png` | Animated player |
| Mummy sprites | `mummy up/down/left/right.png` | Animated enemy |
| Mummy static | `mummy.png` | Fallback |
| Treasure | `treasure.png` | Goal/exit |
| **Sounds** | `Main Sound TRack.mp3` | BG music loop |
| | `win sound.mp3` | Victory SFX |
| | `losing sound.mp3` | Defeat SFX |

---

## Proposed File Structure

```
d:\Projects\maze\
├── main.py                    ← Entry point (replaces CurseOfPyramids.py)
├── assets\                    ← (existing - kept as-is)
├── sounds\                    ← (existing - kept as-is)
└── src\
    ├── __init__.py
    ├── constants.py           ← Screen size, colors, timing config
    ├── asset_loader.py        ← Centralized image/audio loading
    ├── maze.py                ← Maze grid data + rendering
    ├── player.py              ← Player class (movement, animation)
    ├── enemy.py               ← Mummy class (A* AI, animation)
    ├── pathfinding.py         ← A* algorithm (extracted)
    ├── audio.py               ← Sound manager
    ├── ui.py                  ← Button class, screen overlays
    └── game.py                ← Main game state machine
```

---

## Proposed Changes

### Entry Point

#### [NEW] [main.py](file:///d:/Projects/maze/main.py)
Simple launcher that initializes pygame and runs the game.

---

### Source Modules (`src/`)

#### [NEW] [constants.py](file:///d:/Projects/maze/src/constants.py)
- `SCREEN_W`, `SCREEN_H` = 750, 750
- `TILE_SIZE` = 40 (15×15 = 600px maze, centered with sidebar)
- `COLS`, `ROWS` = 15, 15
- `FPS` = 60
- Game states: `MENU`, `PLAYING`, `PAUSED`, `WIN`, `LOSE`
- Colors, animation speeds

#### [NEW] [pathfinding.py](file:///d:/Projects/maze/src/pathfinding.py)
Extracted and improved A* from existing code with proper open-set tracking.

#### [NEW] [asset_loader.py](file:///d:/Projects/maze/src/asset_loader.py)
- `load_image(path, scale=None, alpha=True)` — safe load with error fallback
- `load_sound(path)` — safe sound load
- Loads **all** assets at startup into a dict; individual classes don't load files

#### [NEW] [maze.py](file:///d:/Projects/maze/src/maze.py)
- `MAZE_GRID` — the 15×15 grid from existing code (kept intact)
- `Maze` class with `draw(surface)`, `is_wall(col, row)`, `get_floor_cells()`

#### [NEW] [player.py](file:///d:/Projects/maze/src/player.py)
- `Player` class: grid coordinates
- Directional sprites: up/down/left/right
- `move(direction, maze)` — wall-collision check
- `draw(surface)` — animated (frame cycling)
- `get_pixel_pos()` — smooth lerp toward target for visual polish

#### [NEW] [enemy.py](file:///d:/Projects/maze/src/enemy.py)
- `Enemy` (Mummy) class
- Uses `pathfinding.a_star()` every N frames
- Speed increases per level (difficulty scaling)
- Directional sprite switching based on movement direction

#### [NEW] [audio.py](file:///d:/Projects/maze/src/audio.py)
- `AudioManager` class
- `play_music()`, `pause_music()`, `resume_music()`, `stop_music()`
- `play_sfx(name)` for win/lose sounds
- Graceful fallback if audio files missing

#### [NEW] [ui.py](file:///d:/Projects/maze/src/ui.py)
- `Button` class — rect, hover glow effect, click detection
- `draw_start_screen(surface, assets)` — blits `start menu.png`, draws styled buttons
- `draw_pause_screen(surface, assets)` — semi-transparent overlay + `pause.png`
- `draw_win_screen(surface, assets)` — `win.png` full-screen + replay/menu buttons
- `draw_lose_screen(surface, assets)` — `LOSE.png` full-screen + retry/menu buttons
- Fade-in transition helper

#### [NEW] [game.py](file:///d:/Projects/maze/src/game.py)
- `Game` class — main loop owner
- State machine: `MENU → PLAYING ↔ PAUSED → WIN/LOSE → MENU`
- `handle_events()`, `update()`, `draw()`
- Pause button in HUD (uses `PauseButton.png`)
- Timer/score display
- Level counter for difficulty scaling

---

## Gameplay Design

| Feature | Implementation |
|---|---|
| Maze | 15×15 hardcoded grid (from original code) |
| Player start | Top-left open cell `(1,1)` |
| Treasure (goal) | Bottom-right open cell `(13,13)` |
| Enemy start | `(7,7)` (center), so player has a head start |
| Enemy AI | A* pathfinding, recalculates every 30 frames |
| Win condition | Player reaches treasure cell |
| Lose condition | Enemy reaches same cell as player |
| Levels | After win → next level with faster enemy |
| Pause | `P` key or mouse click on Pause button |
| Restart | From Win/Lose screens via button |

---

## Verification Plan

### Automated
- Run `python main.py` — verify no import errors
- Confirm all screens render (manual click through)

### Manual
- Test all keyboard controls (arrow keys)
- Test pause/resume (P key + button click)
- Confirm audio plays/stops correctly
- Confirm enemy chases player correctly
- Confirm win/lose screens appear with correct assets
- Test "Play Again" and "Main Menu" buttons
