"""
pathfinding.py
A* pathfinding used by the enemy AI.

Coordinates are (col, row) tuples throughout.
maze[row][col] == 1  →  wall (impassable)
maze[row][col] == 0  →  floor (walkable)
"""
import heapq


def heuristic(a: tuple, b: tuple) -> int:
    """Manhattan-distance heuristic (admissible for a grid with unit costs)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(maze, start: tuple, goal: tuple, cols: int, rows: int) -> list:
    """
    Find the shortest path from *start* to *goal* on *maze*.

    Returns a list of (col, row) cells from the cell AFTER start up to and
    including goal, or an empty list if no path exists.
    """
    if start == goal:
        return []

    # heap: (f_score, g_score, node)  – g_score breaks f-score ties
    open_heap: list = []
    heapq.heappush(open_heap, (0, 0, start))

    came_from: dict  = {}
    g_score:   dict  = {start: 0}
    in_open:   set   = {start}

    # 4-directional movement: (Δcol, Δrow)
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    while open_heap:
        _, _, current = heapq.heappop(open_heap)
        in_open.discard(current)

        if current == goal:
            # Reconstruct path (start excluded)
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dc, dr in directions:
            nc, nr = current[0] + dc, current[1] + dr
            neighbour = (nc, nr)

            # Bounds check
            if not (0 <= nc < cols and 0 <= nr < rows):
                continue
            # Wall check
            if maze[nr][nc] == 1:
                continue

            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(neighbour, float("inf")):
                came_from[neighbour] = current
                g_score[neighbour]   = tentative_g
                f = tentative_g + heuristic(neighbour, goal)
                heapq.heappush(open_heap, (f, tentative_g, neighbour))
                in_open.add(neighbour)

    return []   # no path found
