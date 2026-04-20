"""
maze_generator.py
Procedural maze generation using iterative DFS (recursive backtracking)
+ loop carving for multiple paths (chasing-friendly maze)
"""

import random
from src.constants import SCREEN_W, SCREEN_H, MAZE_OFF_Y

_AVAIL_PX = SCREEN_W - 100
_AVAIL_H  = SCREEN_H - MAZE_OFF_Y - 28


# ─── Size progression ─────────────────────────────────────────────────────────

def _logical_cells(level: int) -> int:
    return min(7 + (level - 1) * 2, 21)


# ─── Grid generation ──────────────────────────────────────────────────────────

def _make_grid(n: int, seed: int):
    g    = 2 * n + 1
    grid = [[1] * g for _ in range(g)]
    rng  = random.Random(seed)

    # start
    grid[1][1] = 0
    stack = [(1, 1)]
    DIRS  = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    # ── DFS maze generation (perfect base) ────────────────────────────────
    while stack:
        cx, cy = stack[-1]
        nbrs = []

        for dx, dy in DIRS:
            nx, ny = cx + 2 * dx, cy + 2 * dy
            if 0 < nx < g - 1 and 0 < ny < g - 1 and grid[ny][nx] == 1:
                nbrs.append((nx, ny, cx + dx, cy + dy))

        if nbrs:
            nx, ny, wx, wy = rng.choice(nbrs)
            grid[wy][wx] = 0
            grid[ny][nx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()

    # ── LOOP CARVING (IMPORTANT CHANGE) ────────────────────────────────────
    # This converts "perfect maze" → "chasing maze with multiple routes"

    loop_chance = 0.15  # 👈 زوّدها = طرق أكتر / قللها = صعوبة أعلى

    for y in range(1, g - 1):
        for x in range(1, g - 1):

            if grid[y][x] == 1:

                # connect horizontal corridors
                if grid[y][x - 1] == 0 and grid[y][x + 1] == 0:
                    if rng.random() < loop_chance:
                        grid[y][x] = 0

                # connect vertical corridors
                elif grid[y - 1][x] == 0 and grid[y + 1][x] == 0:
                    if rng.random() < loop_chance:
                        grid[y][x] = 0

    return grid


# ─── Helpers ────────────────────────────────────────────────────────────────

def _nearest_open(grid, col: int, row: int):
    if grid[row][col] == 0:
        return (col, row)

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 0:
                return (c, r)

    return (1, 1)


# ─── Public API ─────────────────────────────────────────────────────────────

class MazeConfig:

    def __init__(self, level: int):

        n    = _logical_cells(level)
        g    = 2 * n + 1
        seed = level * 137 + 42

        self.grid = _make_grid(n, seed)
        self.cols = g
        self.rows = g

        self.tile_size = 40

        self.off_x = 0
        self.off_y = 0

        self.player_start = _nearest_open(self.grid, 1, 1)
        self.enemy_start  = _nearest_open(self.grid, g // 2, g // 2)
        self.treasure_pos = _nearest_open(self.grid, g - 2, g - 2)