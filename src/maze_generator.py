"""
maze_generator.py
Procedural maze generation using iterative DFS (recursive back-tracking).

Each level produces a uniquely seeded, progressively larger maze that always
fills the same pixel area on screen by shrinking the tile size as the
grid grows.

Level progression (logical cells n  →  grid size 2n+1):
    Level 1  →  n= 7  →  15×15  (tile = 40 px)   same as original prototype
    Level 2  →  n= 9  →  19×19  (tile ≈ 31 px)
    Level 3  →  n=11  →  23×23  (tile ≈ 26 px)
    Level 4  →  n=13  →  27×27  (tile ≈ 22 px)
    Level 5  →  n=15  →  31×31  (tile ≈ 19 px)
    ...capped at n=21  →  43×43  (tile ≈ 13 px)
"""
import random
from src.constants import SCREEN_W, SCREEN_H, MAZE_OFF_Y

# Available pixel area for the maze (screen minus HUD bar and margins)
_AVAIL_PX = SCREEN_W - 100                   # 600 px  (50 px side margins)
_AVAIL_H  = SCREEN_H - MAZE_OFF_Y - 28       # 600 px  (below HUD, above bottom)


# ─── Size progression ─────────────────────────────────────────────────────────

def _logical_cells(level: int) -> int:
    """Number of logical corridor cells per axis.  Grid = 2n+1 tiles square."""
    return min(7 + (level - 1) * 2, 21)     # level1→7, level2→9 … cap at 21


# ─── Grid generation — iterative DFS / back-tracking ─────────────────────────

def _make_grid(n: int, seed: int):
    """
    Build a (2n+1)×(2n+1) perfect maze grid.
    1 = wall  |  0 = walkable floor.
    The seed makes every level deterministic and reproducible.
    """
    g    = 2 * n + 1
    grid = [[1] * g for _ in range(g)]
    rng  = random.Random(seed)

    # Start carving from the top-left logical cell (grid coords 1,1)
    grid[1][1] = 0
    stack = [(1, 1)]
    DIRS  = [(0, -1), (0, 1), (-1, 0), (1, 0)]   # unit directions

    while stack:
        cx, cy = stack[-1]
        # Find all unvisited logical neighbours (2 steps away)
        nbrs = []
        for dx, dy in DIRS:
            nx, ny = cx + 2 * dx, cy + 2 * dy
            if 0 < nx < g - 1 and 0 < ny < g - 1 and grid[ny][nx] == 1:
                # wall cell between current and neighbour = 1 step away
                nbrs.append((nx, ny, cx + dx, cy + dy))

        if nbrs:
            nx, ny, wx, wy = rng.choice(nbrs)
            grid[wy][wx] = 0   # carve through the wall
            grid[ny][nx] = 0   # open the neighbour cell
            stack.append((nx, ny))
        else:
            stack.pop()        # dead end — back-track

    return grid


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _nearest_open(grid, col: int, row: int) -> tuple:
    """Return (col, row) if open; scan for the nearest open cell otherwise."""
    if grid[row][col] == 0:
        return (col, row)
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 0:
                return (c, r)
    return (1, 1)   # should never happen in a valid maze


# ─── Public API ───────────────────────────────────────────────────────────────

class MazeConfig:
    """
    All layout parameters for one game level.

    Attributes
    ----------
    grid          : list[list[int]]   2-D grid  (1=wall, 0=floor)
    cols, rows    : int               grid dimensions (square)
    tile_size     : int               pixels per tile on screen
    off_x, off_y  : int               pixel offset of maze top-left corner
    player_start  : (col, row)        guaranteed open cell near top-left
    enemy_start   : (col, row)        guaranteed open cell near centre
    treasure_pos  : (col, row)        guaranteed open cell near bottom-right
    """

    def __init__(self, level: int):
        n    = _logical_cells(level)
        g    = 2 * n + 1
        seed = level * 137 + 42          # deterministic, unique per level

        self.grid = _make_grid(n, seed)
        self.cols = g
        self.rows = g

        # ── Tile size and layout ──────────────────────────────────────────────
        # Tile size is fixed at 40 px for all levels.  Larger mazes simply
        # overflow the viewport — the Camera handles scrolling and clamping.
        # (Shrinking tiles to fit would defeat the point of the camera system.)
        self.tile_size = 40

        # off_x / off_y are 0 in world-space; Camera._mx/_my centres the
        # maze on screen when it is smaller than the viewport.
        self.off_x = 0
        self.off_y = 0

        # Key positions (all guaranteed to be open cells)
        self.player_start = _nearest_open(self.grid, 1, 1)
        self.enemy_start  = _nearest_open(self.grid, g // 2, g // 2)
        self.treasure_pos = _nearest_open(self.grid, g - 2, g - 2)
