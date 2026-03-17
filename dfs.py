import time
from typing import List, Tuple, Set, Optional, Callable

Cell = Tuple[int, int]
Grid = List[List[str]]

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def find_start_end(grid: Grid) -> Tuple[Optional[Cell], Optional[Cell]]:
    start = None
    end = None

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 'S':
                start = (r, c)
            elif grid[r][c] == 'E':
                end = (r, c)

    return start, end


def print_grid(grid: Grid):
    for row in grid:
        print("".join(row))
    print()


def visualize_step(grid: Grid, r: int, c: int, delay: float = 0.0):
    """
    Optional console visualization.
    For GUI use, keep delay=0.0 and avoid mutating the original maze.
    """
    if grid[r][c] not in ('S', 'E', '#'):
        grid[r][c] = '.'
    print_grid(grid)
    if delay > 0:
        time.sleep(delay)


# ---------------------------------------------------------
# DFS Solver (Recursive + GUI-safe)
# ---------------------------------------------------------

def solve_dfs(
    grid: Grid,
    visualize: bool = False,
    delay: float = 0.0,
    step_callback: Optional[Callable[[int, int], None]] = None,
) -> Tuple[List[Cell], int, float]:
    """
    Solve the maze using recursive DFS.

    Maze symbols expected:
        '#' = wall
        '.' = open
        'S' = start
        'E' = end

    Returns:
        path: list of (row, col) cells from S to E
        visited_count: number of explored cells
        runtime_ms: runtime in milliseconds
    """
    if not grid or not grid[0]:
        return [], 0, 0.0

    rows, cols = len(grid), len(grid[0])
    start, end = find_start_end(grid)

    if start is None or end is None:
        raise ValueError("Maze must contain exactly one S and one E")

    visited: Set[Cell] = set()
    path: List[Cell] = []

    # Make a copy only if doing console visualization
    vis_grid = [row[:] for row in grid] if visualize else None

    start_time = time.perf_counter()

    def dfs(r: int, c: int) -> bool:
        visited.add((r, c))
        path.append((r, c))

        if visualize and vis_grid is not None:
            visualize_step(vis_grid, r, c, delay)

        if step_callback is not None:
            step_callback(r, c)

        if (r, c) == end:
            return True

        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc

            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr][nc] != '#' and (nr, nc) not in visited:
                    if dfs(nr, nc):
                        return True

        # backtrack if dead end
        path.pop()
        return False

    found = dfs(start[0], start[1])
    runtime_ms = (time.perf_counter() - start_time) * 1000

    if not found:
        return [], len(visited), runtime_ms

    return path, len(visited), runtime_ms