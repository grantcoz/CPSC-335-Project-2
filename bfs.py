"""
bfs.py

Breadth-First Search (BFS) maze solver.

This module provides a BFS-based solver for a 2D maze represented as a
list of lists of characters.

Maze symbols:
    S = start
    E = end
    # = wall
    . = open path

BFS is guaranteed to find the shortest path in number of steps
for an unweighted grid when a path exists.
"""

from collections import deque
import time


def find_start_end(maze):
    """
    Locate the start and end positions in the maze.

    Args:
        maze (list[list[str]]): 2D maze grid.

    Returns:
        tuple[tuple[int, int], tuple[int, int]]:
            A tuple containing:
            - start position as (row, col)
            - end position as (row, col)

    Raises:
        ValueError: If the maze does not contain exactly one S and one E.
    """
    start = None
    end = None

    # Scan every cell in the maze to locate S and E.
    for r, row in enumerate(maze):
        for c, cell in enumerate(row):
            if cell == 'S':
                start = (r, c)
            elif cell == 'E':
                end = (r, c)

    # Both start and end must exist for solving to work.
    if start is None or end is None:
        raise ValueError("Maze must contain exactly one S and one E.")

    return start, end


def get_neighbors(maze, row, col):
    """
    Return all valid walkable neighboring cells from a given position.

    Valid movement is 4-directional only:
        up, down, left, right

    Args:
        maze (list[list[str]]): 2D maze grid.
        row (int): Current row.
        col (int): Current column.

    Returns:
        list[tuple[int, int]]: List of valid neighboring coordinates.
    """
    # Movement directions: Up, Down, Left, Right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    rows = len(maze)
    cols = len(maze[0])

    neighbors = []

    for dr, dc in directions:
        nr, nc = row + dr, col + dc

        # Check boundaries first.
        if 0 <= nr < rows and 0 <= nc < cols:
            # Only add cells that are not walls.
            if maze[nr][nc] != '#':
                neighbors.append((nr, nc))

    return neighbors


def reconstruct_path(parent, start, end):
    """
    Reconstruct the path from start to end using a parent dictionary.

    The parent dictionary stores, for each visited cell, the cell
    from which it was first reached during BFS.

    Args:
        parent (dict): Maps child cell -> parent cell.
        start (tuple[int, int]): Start position.
        end (tuple[int, int]): End position.

    Returns:
        list[tuple[int, int]]:
            The path from start to end, inclusive.
            Returns an empty list if no path exists.
    """
    # If end was never reached and start != end, then there is no path.
    if end not in parent and end != start:
        return []

    path = []
    current = end

    # Walk backward from end to start using the parent map.
    while current != start:
        path.append(current)
        current = parent[current]

    # Include start and reverse to get start -> end order.
    path.append(start)
    path.reverse()

    return path


def solve_bfs(maze):
    """
    Solve the maze using Breadth-First Search (BFS).

    BFS explores the maze level by level. In an unweighted maze,
    this guarantees the shortest path in number of steps.

    Args:
        maze (list[list[str]]): 2D maze grid.

    Returns:
        tuple:
            path (list[tuple[int, int]]):
                List of (row, col) cells from start to end.
                Empty if no path exists.
            visited_count (int):
                Number of cells expanded/processed by BFS.
            runtime_ms (float):
                Runtime in milliseconds.
    """
    # Start timing the algorithm.
    start_time = time.perf_counter()

    # Find the start and end cells.
    start, end = find_start_end(maze)

    # Queue for BFS frontier.
    queue = deque([start])

    # Set of already discovered cells.
    visited = {start}

    # Parent map used to reconstruct the path once the end is reached.
    parent = {}

    # Counts how many cells BFS actually removes from the queue and expands.
    visited_count = 0

    while queue:
        # Remove the next cell in FIFO order.
        current = queue.popleft()
        visited_count += 1

        # If we reached the end, reconstruct and return the path.
        if current == end:
            path = reconstruct_path(parent, start, end)
            runtime_ms = (time.perf_counter() - start_time) * 1000
            return path, visited_count, runtime_ms

        # Visit all valid neighbors.
        for neighbor in get_neighbors(maze, current[0], current[1]):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    # If BFS finishes without finding the end, there is no path.
    runtime_ms = (time.perf_counter() - start_time) * 1000
    return [], visited_count, runtime_ms