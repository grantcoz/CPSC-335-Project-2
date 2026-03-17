"""
gui.py

Tkinter-based GUI for solving mazes with BFS or DFS.

This application allows the user to:
    - Load a maze from a text file
    - Generate a random maze of adjustable size
    - Choose BFS or DFS as the solving algorithm
    - Solve the maze and display the final path
    - Optionally animate the search process
    - Zoom in and out on the maze display

Maze symbol rules:
    S = Start cell
    E = End/Exit cell
    # = Wall (blocked)
    . = Open path (walkable)

Expected solver behavior:
    - BFS should return a shortest path in number of steps
    - DFS should return a valid path if one exists
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import random
from collections import deque
import time


# Default drawing size for each maze cell in pixels.
CELL_SIZE = 30

# Limits for zooming.
MIN_CELL_SIZE = 10
MAX_CELL_SIZE = 60


class MazeApp:
    """
    Main GUI application class for the maze solver.

    This class is responsible for:
        - building the Tkinter interface
        - loading and generating mazes
        - validating maze input
        - solving mazes using BFS or DFS
        - animating search progress
        - drawing the maze and solution path
    """

    def __init__(self, root):
        """
        Initialize the application window and state.

        Args:
            root (tk.Tk): The main Tkinter root window.
        """
        self.root = root
        self.root.title("Maze Solver - BFS / DFS")

        # Maze data currently loaded in the GUI.
        self.maze = []

        # Final solution path returned by BFS or DFS.
        self.path = []

        # Cells explored during the search, used for optional animation.
        self.explored = []

        # Current cell size for zooming.
        self.current_cell_size = CELL_SIZE

        # Animation control flags.
        self.animating = False
        self.after_id = None

        # Tkinter variables connected to UI widgets.
        self.algorithm_var = tk.StringVar(value="BFS")
        self.size_var = tk.IntVar(value=12)
        self.animate_var = tk.BooleanVar(value=True)
        self.speed_var = tk.IntVar(value=30)  # milliseconds per animation step

        # Build all widgets.
        self.build_ui()

    def build_ui(self):
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        # ---------------- Row 0: Algorithm + File ----------------
        tk.Label(control_frame, text="Algorithm:").grid(row=0, column=0, sticky="w")

        tk.Radiobutton(control_frame, text="BFS", variable=self.algorithm_var, value="BFS").grid(row=0, column=1, sticky="w")
        tk.Radiobutton(control_frame, text="DFS", variable=self.algorithm_var, value="DFS").grid(row=0, column=2, sticky="w")

        tk.Button(control_frame, text="Load .txt File", command=self.load_maze_from_file)\
            .grid(row=0, column=3, padx=15)

        # ---------------- Row 1: Maze Generation ----------------
        tk.Label(control_frame, text="Grid Size:").grid(row=1, column=0, pady=10, sticky="w")

        tk.Spinbox(control_frame, from_=8, to=100, textvariable=self.size_var, width=5)\
            .grid(row=1, column=1, pady=10, sticky="w")

        tk.Button(control_frame, text="Generate Random Maze", command=self.generate_random_maze)\
            .grid(row=1, column=2, columnspan=2, pady=10, padx=10)

        # ---------------- Row 2: Solve Controls ----------------
        tk.Button(control_frame, text="Solve", command=self.solve_maze, bg="lightgreen")\
            .grid(row=2, column=1, pady=5, padx=5)

        tk.Button(control_frame, text="Clear Path", command=self.clear_path)\
            .grid(row=2, column=2, pady=5, padx=5)

        # ---------------- Row 3: Animation ----------------
        tk.Checkbutton(control_frame, text="Animate Search", variable=self.animate_var)\
            .grid(row=3, column=0, pady=10, sticky="w")

        tk.Label(control_frame, text="Speed:").grid(row=3, column=1, sticky="e")

        tk.Scale(control_frame, from_=1, to=200, orient=tk.HORIZONTAL,
                variable=self.speed_var, length=200)\
            .grid(row=3, column=2, columnspan=2, sticky="w")

        # ---------------- Row 4: Zoom ----------------
        tk.Button(control_frame, text="Zoom +", command=self.zoom_in)\
            .grid(row=4, column=1, pady=10)

        tk.Button(control_frame, text="Zoom -", command=self.zoom_out)\
            .grid(row=4, column=2, pady=10)

        # ---------------- Stats ----------------
        self.stats_label = tk.Label(
            self.root,
            text="Load a maze and click Solve.",
            anchor="w",
            justify="left",
            padx=10
        )
        self.stats_label.pack(fill=tk.X)

        # ---------------- Canvas ----------------
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg="white",
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)

    def cancel_animation(self):
        """
        Cancel any scheduled animation callback.

        This is useful when:
            - loading a new maze
            - generating a new maze
            - clearing the path
            - solving again before a previous animation is finished
        """
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.animating = False

    def zoom_in(self):
        """
        Increase the size of drawn maze cells, up to MAX_CELL_SIZE.
        """
        self.current_cell_size = min(MAX_CELL_SIZE, self.current_cell_size + 5)
        self.draw_maze()

    def zoom_out(self):
        """
        Decrease the size of drawn maze cells, down to MIN_CELL_SIZE.
        """
        self.current_cell_size = max(MIN_CELL_SIZE, self.current_cell_size - 5)
        self.draw_maze()

    def validate_maze(self, maze):
        """
        Validate that the maze follows the assignment rules.

        A valid maze must:
            - not be empty
            - have equal row lengths
            - contain only S, E, #, .
            - contain exactly one S
            - contain exactly one E

        Args:
            maze (list[str] or list[list[str]]): Maze rows to validate.

        Returns:
            tuple[bool, str]:
                - True and empty message if valid
                - False and error message if invalid
        """
        if not maze:
            return False, "Maze is empty."

        row_length = len(maze[0])
        start_count = 0
        end_count = 0

        for row in maze:
            if len(row) != row_length:
                return False, "Maze rows must all be the same length."

            for cell in row:
                if cell not in {'S', 'E', '#', '.'}:
                    return False, "Maze contains invalid characters."

                if cell == 'S':
                    start_count += 1
                elif cell == 'E':
                    end_count += 1

        if start_count != 1 or end_count != 1:
            return False, "Maze must contain exactly one S and exactly one E."

        return True, ""

    def load_maze_from_file(self):
        """
        Open a file picker, load a maze from a .txt file, validate it,
        and display it on the canvas.
        """
        self.cancel_animation()

        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [line.rstrip("\n") for line in f if line.strip()]

            valid, msg = self.validate_maze(lines)
            if not valid:
                messagebox.showerror("Invalid Maze", msg)
                return

            self.maze = [list(row) for row in lines]
            self.path = []
            self.explored = []
            self.draw_maze()
            self.stats_label.config(text=f"Loaded maze from file: {file_path}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_random_maze(self):
        """
        Generate a random maze of the selected size.

        Behavior:
            - border cells become walls
            - interior cells become walls with probability 0.28
            - start is placed at (1, 1)
            - end is placed at (size - 2, size - 2)
            - nearby cells around start/end are opened for a better chance
              of solvability

        Note:
            This does not guarantee the maze is solvable.
        """
        self.cancel_animation()

        size = self.size_var.get()
        maze = [['.' for _ in range(size)] for _ in range(size)]

        # Create border walls.
        for r in range(size):
            maze[r][0] = '#'
            maze[r][size - 1] = '#'
        for c in range(size):
            maze[0][c] = '#'
            maze[size - 1][c] = '#'

        # Randomly place interior walls.
        for r in range(1, size - 1):
            for c in range(1, size - 1):
                if random.random() < 0.28:
                    maze[r][c] = '#'

        # Place start and end cells.
        maze[1][1] = 'S'
        maze[size - 2][size - 2] = 'E'

        # Open nearby cells around S and E to reduce immediate trapping.
        for rr, cc in [(1, 2), (2, 1), (size - 2, size - 3), (size - 3, size - 2)]:
            if 0 <= rr < size and 0 <= cc < size:
                maze[rr][cc] = '.'

        self.maze = maze
        self.path = []
        self.explored = []
        self.draw_maze()
        self.stats_label.config(text=f"Generated random {size}x{size} maze")

    def clear_path(self):
        """
        Clear the currently displayed path and explored cells,
        then redraw the original maze layout.
        """
        self.cancel_animation()
        self.path = []
        self.explored = []
        self.draw_maze()
        self.stats_label.config(text="Path cleared.")

    def find_start_end(self, grid):
        """
        Find the start and end coordinates in the given maze grid.

        Args:
            grid (list[list[str]]): Maze grid.

        Returns:
            tuple:
                start (tuple[int, int] or None)
                end (tuple[int, int] or None)
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

    def reconstruct_path(self, parent, end):
        """
        Reconstruct a path from a parent dictionary.

        Args:
            parent (dict): Maps each cell to the cell it came from.
            end (tuple[int, int]): End cell.

        Returns:
            list[tuple[int, int]]: Reconstructed path from start to end.
        """
        path = []
        cur = end

        while cur is not None:
            path.append(cur)
            cur = parent[cur]

        path.reverse()
        return path

    def run_bfs_with_trace(self):
        """
        Solve the current maze using BFS and record the order of exploration.

        BFS uses a queue and guarantees the shortest path in number of steps
        in an unweighted grid.

        Returns:
            tuple:
                path (list[tuple[int, int]])
                visited_count (int)
                runtime_ms (float)
                explored_order (list[tuple[int, int]])
        """
        rows, cols = len(self.maze), len(self.maze[0])
        start, end = self.find_start_end(self.maze)

        if start is None or end is None:
            raise ValueError("Maze must contain exactly one S and one E")

        start_time = time.perf_counter()

        # BFS queue starts with the start cell.
        q = deque([start])

        # Track discovered cells so they are not added multiple times.
        visited = {start}

        # Parent map for path reconstruction.
        parent = {start: None}

        # Order in which nodes are expanded, used for animation.
        explored_order = []

        # 4-direction movement only.
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while q:
            r, c = q.popleft()
            explored_order.append((r, c))

            if (r, c) == end:
                runtime_ms = (time.perf_counter() - start_time) * 1000
                return self.reconstruct_path(parent, end), len(visited), runtime_ms, explored_order

            for dr, dc in dirs:
                nr, nc = r + dr, c + dc

                if 0 <= nr < rows and 0 <= nc < cols:
                    if self.maze[nr][nc] != '#' and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        parent[(nr, nc)] = (r, c)
                        q.append((nr, nc))

        runtime_ms = (time.perf_counter() - start_time) * 1000
        return [], len(visited), runtime_ms, explored_order

    def run_dfs_with_trace(self):
        """
        Solve the current maze using recursive DFS and record the order
        of exploration.

        DFS does not guarantee the shortest path, but it should return
        a valid path if one exists.

        Returns:
            tuple:
                path (list[tuple[int, int]])
                visited_count (int)
                runtime_ms (float)
                explored_order (list[tuple[int, int]])
        """
        rows, cols = len(self.maze), len(self.maze[0])
        start, end = self.find_start_end(self.maze)

        if start is None or end is None:
            raise ValueError("Maze must contain exactly one S and one E")

        visited = set()
        path = []
        explored_order = []

        start_time = time.perf_counter()

        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        def dfs(r, c):
            """
            Recursive helper function for DFS.

            Args:
                r (int): Current row.
                c (int): Current column.

            Returns:
                bool: True if the end is found from this cell, else False.
            """
            visited.add((r, c))
            explored_order.append((r, c))
            path.append((r, c))

            if (r, c) == end:
                return True

            for dr, dc in dirs:
                nr, nc = r + dr, c + dc

                if 0 <= nr < rows and 0 <= nc < cols:
                    if self.maze[nr][nc] != '#' and (nr, nc) not in visited:
                        if dfs(nr, nc):
                            return True

            # Backtrack: remove current cell from the attempted path.
            path.pop()
            return False

        found = dfs(start[0], start[1])
        runtime_ms = (time.perf_counter() - start_time) * 1000

        return (path if found else []), len(visited), runtime_ms, explored_order

    def solve_maze(self):
        """
        Solve the currently loaded maze using the selected algorithm.

        Flow:
            1. Clear previous animation/path
            2. Run BFS or DFS
            3. Animate search if enabled
            4. Otherwise draw final result immediately
        """
        if not self.maze:
            messagebox.showwarning("No Maze", "Please load or generate a maze first.")
            return

        self.cancel_animation()
        self.path = []
        self.explored = []
        self.draw_maze()

        algorithm = self.algorithm_var.get()

        try:
            if algorithm == "BFS":
                path, visited_count, runtime_ms, explored_order = self.run_bfs_with_trace()
            else:
                path, visited_count, runtime_ms, explored_order = self.run_dfs_with_trace()

            if self.animate_var.get():
                self.animating = True
                self.animate_exploration(
                    explored_order,
                    path,
                    algorithm,
                    visited_count,
                    runtime_ms,
                    0
                )
            else:
                self.explored = explored_order
                self.path = path
                self.draw_maze()
                self.update_stats(algorithm, path, visited_count, runtime_ms)

        except Exception as e:
            messagebox.showerror("Solve Error", str(e))

    def animate_exploration(self, explored_order, final_path, algorithm, visited_count, runtime_ms, index):
        """
        Animate the search process one explored cell at a time.

        Uses Tkinter's after() so the GUI remains responsive.

        Args:
            explored_order (list[tuple[int, int]]): Cells visited in order.
            final_path (list[tuple[int, int]]): Final solution path.
            algorithm (str): "BFS" or "DFS"
            visited_count (int): Number of visited cells.
            runtime_ms (float): Runtime in milliseconds.
            index (int): Current frame index in the animation.
        """
        if index >= len(explored_order):
            self.explored = explored_order
            self.path = final_path
            self.draw_maze()
            self.update_stats(algorithm, final_path, visited_count, runtime_ms)
            self.animating = False
            self.after_id = None
            return

        self.explored.append(explored_order[index])
        self.draw_maze()

        delay = self.speed_var.get()
        self.after_id = self.root.after(
            delay,
            lambda: self.animate_exploration(
                explored_order,
                final_path,
                algorithm,
                visited_count,
                runtime_ms,
                index + 1
            )
        )

    def update_stats(self, algorithm, path, visited_count, runtime_ms):
        """
        Update the stats label after solving.

        Args:
            algorithm (str): Algorithm name used.
            path (list[tuple[int, int]]): Final path found.
            visited_count (int): Number of visited/explored cells.
            runtime_ms (float): Runtime in milliseconds.
        """
        if path:
            path_length = len(path) - 1
            self.stats_label.config(
                text=(
                    f"Algorithm: {algorithm}\n"
                    f"Path Length: {path_length} steps\n"
                    f"Visited/Explored Cells: {visited_count}\n"
                    f"Runtime: {runtime_ms:.3f} ms"
                )
            )
        else:
            self.stats_label.config(
                text=(
                    f"Algorithm: {algorithm}\n"
                    f"No Path Found\n"
                    f"Visited/Explored Cells: {visited_count}\n"
                    f"Runtime: {runtime_ms:.3f} ms"
                )
            )

    def draw_maze(self):
        """
        Draw the current maze, explored cells, and final path on the canvas.

        Color meaning:
            black      = wall
            white      = open path
            lightblue  = explored cell
            yellow     = final solution path
            green      = start
            red        = end
        """
        if not self.maze:
            return

        rows = len(self.maze)
        cols = len(self.maze[0])

        canvas_width = cols * self.current_cell_size
        canvas_height = rows * self.current_cell_size

        self.canvas.delete("all")
        self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))

        explored_set = set(self.explored)
        path_set = set(self.path)

        for r in range(rows):
            for c in range(cols):
                x1 = c * self.current_cell_size
                y1 = r * self.current_cell_size
                x2 = x1 + self.current_cell_size
                y2 = y1 + self.current_cell_size

                cell = self.maze[r][c]

                # Base color for open cells.
                color = "white"

                if cell == '#':
                    color = "black"
                elif (r, c) in explored_set:
                    color = "lightblue"

                # Path overrides explored color.
                if (r, c) in path_set:
                    color = "yellow"

                # Start and end override all other colors.
                if cell == 'S':
                    color = "green"
                elif cell == 'E':
                    color = "red"

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="gray"
                )

                # Draw S and E labels in the center of their cells.
                if cell in ('S', 'E'):
                    font_size = max(8, self.current_cell_size // 3)
                    self.canvas.create_text(
                        x1 + self.current_cell_size / 2,
                        y1 + self.current_cell_size / 2,
                        text=cell,
                        fill="white",
                        font=("Arial", font_size, "bold")
                    )


if __name__ == "__main__":
    """
    Program entry point.

    Creates the Tkinter root window, instantiates the MazeApp,
    and starts the event loop.
    """
    root = tk.Tk()
    root.geometry("1000x700")
    app = MazeApp(root)
    root.mainloop()