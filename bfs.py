from collections import deque
import time


def find_start_end(maze):
    start = None
    end = None

    for r, row in enumerate(maze):
        for c, cell in enumerate(row):
            if cell == 'S':
                start = (r, c)
            elif cell == 'E':
                end = (r, c)

    if start is None or end is None:
        raise ValueError("Maze must contain exactly one S and one E.")

    return start, end


def get_neighbors(maze, row, col):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    rows = len(maze)
    cols = len(maze[0])

    neighbors = []
    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            if maze[nr][nc] != '#':
                neighbors.append((nr, nc))
    return neighbors


def reconstruct_path(parent, start, end):
    if end not in parent and end != start:
        return []

    path = []
    current = end
    while current != start:
        path.append(current)
        current = parent[current]
    path.append(start)
    path.reverse()
    return path


def solve_bfs(maze):
    """
    Returns:
        path: list of (row, col)
        visited_count: int
        runtime_ms: float
    """
    start_time = time.perf_counter()

    start, end = find_start_end(maze)

    queue = deque([start])
    visited = {start}
    parent = {}
    visited_count = 0

    while queue:
        current = queue.popleft()
        visited_count += 1

        if current == end:
            path = reconstruct_path(parent, start, end)
            runtime_ms = (time.perf_counter() - start_time) * 1000
            return path, visited_count, runtime_ms

        for neighbor in get_neighbors(maze, current[0], current[1]):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    runtime_ms = (time.perf_counter() - start_time) * 1000
    return [], visited_count, runtime_ms
