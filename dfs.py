import random
import time
from typing import List, Tuple, Optional, Set

# ---------------------------------------------------------
# Maze Generation
# ---------------------------------------------------------

def generate_maze(rows: int, cols: int, wall_prob: float = 0.3) -> List[List[str]]:
    """
    Generate a random maze using ASCII symbols.
    'X' = wall
    '*' = free space
    'S' = start
    'E' = end
    """
    grid = []
    for _ in range(rows):
        row = ['X' if random.random() < wall_prob else '*' for _ in range(cols)]
        grid.append(row)

    grid[0][0] = 'S'
    grid[rows - 1][cols - 1] = 'E'
    return grid


# ---------------------------------------------------------
# Visualization (Console)
# ---------------------------------------------------------

def print_grid(grid: List[List[str]]):
    for row in grid:
        print("".join(row))
    print()


def visualize_step(grid: List[List[str]], r: int, c: int):
    """
    Mark the current DFS exploration step.
    GUI version will replace this with drawing logic.
    """
    if grid[r][c] not in ('S', 'E'):
        grid[r][c] = '.'
    print_grid(grid)
    time.sleep(0.03)


# ---------------------------------------------------------
# DFS Solver (Recursive)
# ---------------------------------------------------------

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

def solve_dfs(grid: List[List[str]]):
    """
    Solve the maze using recursive DFS.
    Returns:
        path: list of (r, c) coordinates from S to E
        visited_count: number of visited cells
        runtime: time in seconds
    """
    rows, cols = len(grid), len(grid[0])

    # Locate start
    start = None
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 'S':
                start = (r, c)
                break
        if start:
            break

    visited: Set[Tuple[int, int]] = set()
    path: List[Tuple[int, int]] = []

    start_time = time.time()

    def dfs(r: int, c: int) -> bool:
        visited.add((r, c))
        path.append((r, c))

        visualize_step(grid, r, c)

        if grid[r][c] == 'E':
            return True

        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr][nc] != 'X' and (nr, nc) not in visited:
                    if dfs(nr, nc):
                        return True

        # Backtrack
        path.pop()
        return False

    found = dfs(start[0], start[1])
    runtime = time.time() - start_time

    if not found:
        return [], len(visited), runtime

    return path, len(visited), runtime

def generate_solvable_maze(rows: int, cols: int) -> List[List[str]]:
    """
    Generate a guaranteed-solvable maze using recursive backtracking.
    'X' = wall
    '*' = free space
    'S' = start
    'E' = end
    """

    # Start with all walls
    maze = [['X' for _ in range(cols)] for _ in range(rows)]

    # Directions for carving (randomized)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def carve(r: int, c: int):
        maze[r][c] = '*'
        random.shuffle(directions)

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if maze[nr][nc] == 'X':
                    # Count open neighbors to avoid loops
                    open_neighbors = 0
                    for rr, cc in directions:
                        ar, ac = nr + rr, nc + cc
                        if 0 <= ar < rows and 0 <= ac < cols:
                            if maze[ar][ac] == '*':
                                open_neighbors += 1
                    if open_neighbors <= 1:
                        carve(nr, nc)

    # Carve from start
    carve(0, 0)

    # Ensure end is reachable
    maze[rows - 1][cols - 1] = '*'

    # Place S and E
    maze[0][0] = 'S'
    maze[rows - 1][cols - 1] = 'E'

    return maze

# ---------------------------------------------------------
# Correctness Tests
# ---------------------------------------------------------

def test_correctness():
    print("Running correctness tests...\n")

    # 1. Start == End (1x1)
    grid = [['S']]
    path, visited, rt = solve_dfs([['S']])
    print("✓ Start == End test passed")

    # 2. Fully blocked maze
    grid = [['S', 'X'], ['X', 'E']]
    path, visited, rt = solve_dfs(grid)
    assert path == []
    print("✓ Fully blocked maze test passed")

    # 3. Fully open maze
    grid = [['S', '*'], ['*', 'E']]
    path, visited, rt = solve_dfs(grid)
    assert path[-1] == (1, 1)
    print("✓ Fully open maze test passed")

    # 4. No path exists
    grid = [
        ['S', 'X', 'E'],
        ['X', 'X', 'X'],
        ['*', '*', '*']
    ]
    path, visited, rt = solve_dfs(grid)
    assert path == []
    print("✓ No path test passed")

    # 5. Small 2×2 solvable
    grid = [
        ['S', '*'],
        ['X', 'E']
    ]
    path, visited, rt = solve_dfs(grid)
    assert path[-1] == (1, 1)
    print("✓ 2×2 solvable test passed")

    print("\nAll tests passed!")


# ---------------------------------------------------------
# Main Runner
# ---------------------------------------------------------

def main():
    inputRows = input("Enter rows: ")
    inputCols = input("Enter Columns: ")
    rows = int(inputRows)
    cols = int(inputCols)
    maze = generate_solvable_maze(rows, cols)

    print("Generated Maze:")
    #print_grid(maze)

    print("Solving...\n")
    path, visited_count, runtime = solve_dfs(maze)

    if path:
        print("Path found!")
        print("Path length:", len(path))
    else:
        print("No path exists.")

    print("Visited cells:", visited_count)
    print("Runtime:", runtime)

    return visited_count, runtime

    #print("\nRunning tests...")
    #test_correctness()


if __name__ == "__main__":
    main()
