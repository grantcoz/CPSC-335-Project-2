"""
dfs.py

Depth-First Search (DFS) maze solver.

This module provides a recursive DFS-based solver for a 2D maze
represented as a list of lists of characters.

Maze symbols:
    S = start
    E = end
    # = wall
    . = open path

DFS is not guaranteed to return the shortest path, but it is correct:
if a path exists, DFS can find one as long as visited cells are tracked.
"""

import time
from typing import List, Tuple, Set, Optional, Callable

# Type aliases to improve readability.
Cell = Tuple[int, int]     # A maze position: (row, col)
Grid = List[List[str]]     # A 2D maze grid

# Allowed movement directions: Up, Down, Left, Right
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def find_start_end(grid: Grid) -> Tuple[Optional[Cell], Optional[Cell]]:
    """
    Find the start and end cells in the maze.

    Args:
        grid (Grid): 2D maze grid.

    Returns:
        tuple:
            start (Cell or None): Position of 'S'
            end (Cell or None): Position of 'E'
    """
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
    """
    Print the maze grid to the console.

    Useful for terminal debugging or console-based visualization.

    Args:
        grid (Grid): 2D maze grid.
    """
    for row in grid:
        print("".join(row))
    print()


def visualize_step(grid: Grid, r: int, c: int, delay: float = 0.0):
    """
    Visually mark one DFS exploration step in the console.

    This function is optional and mainly intended for console demos.
    In GUI use, this is usually unnecessary.

    Args:
        grid (Grid): Maze grid copy used for visualization.
        r (int): Current row.
        c (int): Current column.
        delay (float): Delay in seconds after printing each step.
    """
    # Do not overwrite special cells or walls.
    if grid[r][c] not in ('S', 'E', '#'):
        grid[r][c] = '.'

    print_grid(grid)

    if delay > 0:
        time.sleep(delay)


# ---------------------------------------------------------
# DFS Solver
# ---------------------------------------------------------

def solve_dfs(
    grid: Grid,
    visualize: bool = False,
    delay: float = 0.0,
    step_callback: Optional[Callable[[int, int], None]] = None,
) -> Tuple[List[Cell], int, float]:
    """
    Solve the maze using recursive Depth-First Search (DFS).

    DFS explores one branch as far as possible before backtracking.
    It does not guarantee the shortest path, but it will find a valid
    path if one exists.

    Args:
        grid (Grid): 2D maze grid.
        visualize (bool):
            If True, console visualization is enabled.
        delay (float):
            Time delay in seconds between visualization steps.
        step_callback (callable or None):
            Optional callback function called as step_callback(row, col)
            each time a cell is visited. Useful for GUI animation hooks.

    Returns:
        tuple:
            path (list[Cell]):
                The discovered path from S to E, inclusive.
                Empty if no path exists.
            visited_count (int):
                Number of distinct cells visited by DFS.
            runtime_ms (float):
                Runtime in milliseconds.

    Raises:
        ValueError: If the maze does not contain exactly one S and one E.
    """
    # Handle empty grid safely.
    if not grid or not grid[0]:
        return [], 0, 0.0

    rows, cols = len(grid), len(grid[0])

    # Locate the start and end cells.
    start, end = find_start_end(grid)

    if start is None or end is None:
        raise ValueError("Maze must contain exactly one S and one E")

    # Stores all visited cells to avoid infinite loops and repeated work.
    visited: Set[Cell] = set()

    # Stores the current DFS path. Cells are added as DFS goes deeper,
    # and removed when backtracking from dead ends.
    path: List[Cell] = []

    # Use a copy of the maze if console visualization is enabled so the
    # original maze is not modified.
    vis_grid = [row[:] for row in grid] if visualize else None

    # Start timing the DFS algorithm.
    start_time = time.perf_counter()

    def dfs(r: int, c: int) -> bool:
        """
        Recursive helper function for DFS.

        Args:
            r (int): Current row.
            c (int): Current column.

        Returns:
            bool:
                True if a path from this cell to E exists.
                False otherwise.
        """
        # Mark the current cell as visited.
        visited.add((r, c))

        # Add the current cell to the path currently being explored.
        path.append((r, c))

        # Optional console visualization.
        if visualize and vis_grid is not None:
            visualize_step(vis_grid, r, c, delay)

        # Optional hook for GUI or external tracing.
        if step_callback is not None:
            step_callback(r, c)

        # Base case: if we reached the end, the path is complete.
        if (r, c) == end:
            return True

        # Explore all 4-direction neighbors.
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc

            # Check bounds and whether the neighbor is walkable and unvisited.
            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr][nc] != '#' and (nr, nc) not in visited:
                    if dfs(nr, nc):
                        return True

        # If none of the neighbors lead to the exit, backtrack:
        # remove this cell from the current path.
        path.pop()
        return False

    # Start DFS from the start cell.
    found = dfs(start[0], start[1])

    # Stop timing.
    runtime_ms = (time.perf_counter() - start_time) * 1000

    # If DFS failed to reach E, return no path.
    if not found:
        return [], len(visited), runtime_ms

    return path, len(visited), runtime_ms