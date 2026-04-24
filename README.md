# ⚱️ Curse of the Pyramids

A modern, modular maze chase game built with **Python** and **Pygame**. Navigate procedurally-generated labyrinths while evading intelligent mummy enemies in this progressively challenging dungeon crawler.

---

## 📋 Description

**Curse of the Pyramids** is a fast-paced, level-based maze exploration game where players must navigate from the entrance to the treasure while avoiding mummy enemies that hunt using advanced pathfinding algorithms. Each level increases in difficulty with larger mazes, faster enemies, reduced visibility via fog-of-war, and additional adversaries. The game features smooth animations, responsive controls, and a polished UI with menu systems.

**Target Audience:** Game developers, Python enthusiasts, and players who enjoy strategic puzzle-action games.

---

## 🎮 Demo / Screenshots

![Game Screenshot](assets/Test1.png)
![Game Screenshot](assets/test2.png)
![Game Screenshot](assets/test3.png)
![Game Screenshot](assets/test4.png)


📸 **Full screenshots available in `assets/` folder**

---

## ✨ Features

- 🎲 **Procedural Maze Generation** — DFS-based algorithm with loop carving creates unique, varied layouts each level
- 👾 **Intelligent AI Enemies** — Mummy adversaries use A\* pathfinding with adaptive difficulty scaling
- 👥 **Multiple Enemies** — From level 4+, a second mummy joins the hunt for increased challenge
- 📷 **Dynamic Camera System** — Smooth scrolling viewport centered on player with easing
- 🌑 **Fog of War Lighting** — Darkness layer shrinks as levels progress, reducing player visibility
- 😰 **Panic System** — Screen shake effect triggers when enemies approach, intensifying with level
- 🎬 **Smooth Animations** — LERP-based pixel interpolation provides fluid motion at 60 FPS
- 🎵 **Audio System** — Background music, victory, and defeat sound effects
- 📊 **Progressive Difficulty** — Maze size, enemy speed, pathfinding frequency, and visibility all scale per level
- 🎨 **Polished UI** — Start menu, pause overlay, win/lose screens, settings framework
- ⌨️ **Responsive Controls** — Keyboard (Arrow keys/WASD) and mouse support

---

## 🛠 Tech Stack

| Component        | Technology                           |
| ---------------- | ------------------------------------ |
| **Language**     | Python 3.9+                          |
| **Game Engine**  | Pygame 2.0+                          |
| **Algorithm**    | A\* Pathfinding, DFS Maze Generation |
| **Architecture** | State Machine, Modular OOP           |
| **Animation**    | LERP (Linear Interpolation)          |

---

## 📦 Installation

### Prerequisites

- **Python 3.9** or higher
- **pip** (Python package manager)

### Step-by-Step Setup

1. **Clone or download the project:**

   ```bash
   cd d:\Projects\maze
   # or navigate to your project directory
   ```

2. **Install dependencies:**

   ```bash
   pip install pygame
   ```

3. **Verify installation:**

   ```bash
   python -c "import pygame; print(f'Pygame version: {pygame.version.ver}')"
   ```

4. **Run the game:**
   ```bash
   python main.py
   ```

---

## 🎮 Usage

### Starting the Game

```bash
python main.py
```

### Controls

| Input                      | Action                       |
| -------------------------- | ---------------------------- |
| **↑ ↓ ← →** or **W A S D** | Move player                  |
| **P** or **ESC**           | Pause/Resume                 |
| **Mouse Click**            | Interact with menus/buttons  |
| **Pause Button (Icon)**    | Toggle pause during gameplay |

### Gameplay Flow

1. **Main Menu** → Click "Play" to start
2. **Level 1–3** → Survive and reach the treasure with one mummy chasing
3. **Level 4+** → Two mummies hunt; mazes are larger and darker
4. **Win** → Reach the treasure to advance to the next level
5. **Lose** → Get caught by a mummy; retry or return to menu

### Example Session

```
Game Start
├─ Level 1 (9×9 maze, 1 enemy)
│  └─ Reach treasure → WIN
├─ Level 2 (11×11 maze, 1 enemy, faster)
│  └─ Get caught → LOSE → Retry
├─ Level 2 Retry → WIN
└─ Level 3 (13×13 maze, 1 enemy, even faster)
   └─ Continue or Main Menu
```

---

## 📂 Project Structure

```
d:\Projects\maze\
├── main.py                    ← Entry point (launcher)
├── README.md                  ← Project documentation
├── walkthrough.md             ← Detailed feature walkthrough
├── implementation_plan.md     ← Development roadmap
│
├── assets/                    ← All PNG sprite assets
│   ├── start menu.png
│   ├── win.png
│   ├── LOSE.png
│   ├── wall.png / floor.png
│   ├── player_*.png           ← Directional sprites
│   ├── mummy_*.png            ← Enemy sprites
│   └── treasure.png
│
├── sounds/                    ← Audio files (MP3)
│   ├── Main Sound Track.mp3
│   ├── win sound.mp3
│   └── losing sound.mp3
│
└── src/                       ← Core game modules
    ├── __init__.py
    ├── constants.py           ← Global config (screen size, colors, timing)
    ├── maze_generator.py      ← Procedural maze gen (DFS + loop carving)
    ├── pathfinding.py         ← A* algorithm implementation
    ├── asset_loader.py        ← Image/sound loading manager
    ├── maze.py                ← Maze grid + rendering (baked surface)
    ├── player.py              ← Player class (movement, animation)
    ├── enemy.py               ← Enemy/Mummy AI (A* pathfinding)
    ├── camera.py              ← Viewport, fog of war, screen shake
    ├── audio.py               ← Sound manager (music, SFX)
    ├── ui.py                  ← UI elements (buttons, HUD, overlays)
    └── game.py                ← State machine + main game loop
```

---

## 🔧 Key Architecture Highlights

### Modular Design

- Each system (maze, player, enemy, camera, audio) is self-contained
- Clean separation of concerns via dedicated modules
- Easy to test, extend, and maintain

### State Machine

- Game state (`MENU`, `PLAYING`, `PAUSED`, `WIN`, `LOSE`, `SETTINGS`) drives all logic
- Centralized event dispatch and rendering flow

### Performance Optimizations

- **Baked maze surface** — Tiles rendered once at startup; single `blit()` per frame
- **Efficient A\*** — Set-based open-list lookups (O(1) vs O(n))
- **LERP animation** — Smooth 60 FPS motion without overhead

### Difficulty Scaling

Each level applies cumulative tuning:

- Maze size: `7 + (level - 1) × 2` cells
- Enemy speed: `× 0.85^(level-1)`
- Light radius: Decreases per level
- Panic intensity: `× (level + 2)`

---

## 🚀 Future Improvements

- [ ] **Power-ups** — Speed boost, temporary invisibility, freeze enemy
- [ ] **Lives/Health System** — Multiple hit points instead of instant lose
- [ ] **Leaderboard** — High score tracking and persistence
- [ ] **Difficulty Settings** — Easy/Normal/Hard modes with adjusted parameters

---

## 🤝 Contributing Guidelines

Contributions are welcome! To contribute:

1. **Fork** the repository or create a feature branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and test thoroughly:

   ```bash
   python main.py
   ```

3. **Follow code style:**
   - PEP 8 conventions
   - Clear function/variable names
   - Docstrings for modules and classes
   - Comments for complex logic

4. **Commit with meaningful messages:**

   ```bash
   git commit -m "Add feature: brief description"
   ```

5. **Submit a pull request** with a description of your changes

### Reporting Issues

- Use GitHub Issues for bug reports
- Include steps to reproduce
- Attach screenshots/logs if relevant

---

## 📄 License

This project is released under the **MIT License**. See LICENSE file for details.

You are free to use, modify, and distribute this project for personal and commercial purposes, provided attribution is given.

---

## 👤 Author

Louay Mohamed,
Lama Diaa,
Sohila Ihab

## 🙏 Acknowledgments

- **Pygame** community for the excellent game development framework
- **A\* Pathfinding** algorithm pioneers
- Inspired by classic maze games and roguelikes

---

## 📞 Support

For questions, bug reports, or suggestions:

- 📝 Open an issue on GitHub
- 💬 Start a discussion
- 📧 Contact the author directly

---

**Happy gaming! 🎮✨**
