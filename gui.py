"""
gui.py

Tkinter GUI for visualizing and solving mazes with BFS and DFS.

Features:
    - Choose BFS or DFS
    - Load a built-in sample maze
    - Load a maze from a .txt file
    - Generate a random maze
    - Animate search exploration step-by-step
    - Zoom in/out
    - Scroll and pan across large mazes
    - Show solving statistics:
        * algorithm used
        * path length
        * visited/explored cells
        * runtime

Maze symbols:
    S = start
    E = end
    # = wall
    . = open path
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import random
from collections import deque
import time

# Default drawing sizes for maze cells.
CELL_SIZE = 30
MIN_CELL_SIZE = 10
MAX_CELL_SIZE = 60


class MazeApp:
    """
    Main GUI application class for the maze solver.

    This class handles:
        - window setup
        - control widgets
        - maze loading/generation
        - solving with BFS/DFS
        - animation
        - drawing the maze on a canvas
    """

    def __init__(self, root):
        """
        Initialize the GUI application state and build the interface.

        Args:
            root (tk.Tk): The main Tkinter window.
        """
        self.root = root
        self.root.title("Maze Solver - BFS / DFS")

        # Maze data structures.
        self.maze = []          # Current maze grid
        self.path = []          # Final solved path
        self.explored = []      # Order of explored cells for animation

        # View and animation state.
        self.current_cell_size = CELL_SIZE
        self.pan_start = None
        self.animating = False
        self.after_id = None

        # Built-in sample mazes.
        self.samples = {
            "Sample 1": [
                "##########",
                "#S...#...#",
                "#.##.#.#.#",
                "#....#.#E#",
                "##########"
            ],
            "Sample 2": [
                "############",
                "#S....#....#",
                "###.#.#.##.#",
                "#...#...#..#",
                "#.#####.#.##",
                "#.......#E.#",
                "############"
            ],
            "Sample 3": [
                "###############",
                "#S..#.........#",
                "#.#.#.#######.#",
                "#.#...#.....#.#",
                "#.#####.###.#.#",
                "#.....#...#...#",
                "###.#.###.###.#",
                "#...#.....#..E#",
                "###############"
            ]
        }

        # Tkinter state variables connected to UI controls.
        self.algorithm_var = tk.StringVar(value="BFS")
        self.sample_var = tk.StringVar(value="Sample 1")
        self.size_var = tk.IntVar(value=12)
        self.animate_var = tk.BooleanVar(value=True)
        self.speed_var = tk.IntVar(value=30)  # milliseconds per animation step

        # Build the user interface and load the default sample maze.
        self.build_ui()
        self.load_sample_maze()

    def build_ui(self):
        """
        Create all GUI widgets:
            - algorithm selection controls
            - maze loading/generation controls
            - animation controls
            - zoom controls
            - stats label
            - scrollable drawing canvas
        """
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        # Algorithm selection.
        tk.Label(control_frame, text="Algorithm:").grid(row=0, column=0, sticky="w")
        tk.Radiobutton(control_frame, text="BFS", variable=self.algorithm_var, value="BFS").grid(row=0, column=1, sticky="w")
        tk.Radiobutton(control_frame, text="DFS", variable=self.algorithm_var, value="DFS").grid(row=0, column=2, sticky="w")

        # Sample maze selection.
        tk.Label(control_frame, text="Samples:").grid(row=0, column=3, padx=(20, 5), sticky="w")
        sample_menu = tk.OptionMenu(control_frame, self.sample_var, *self.samples.keys())
        sample_menu.grid(row=0, column=4, sticky="w")

        tk.Button(control_frame, text="Load Sample", command=self.load_sample_maze).grid(row=0, column=5, padx=5)
        tk.Button(control_frame, text="Load .txt File", command=self.load_maze_from_file).grid(row=0, column=6, padx=5)

        # Random maze generation.
        tk.Label(control_frame, text="Grid Size:").grid(row=1, column=0, pady=(10, 0), sticky="w")
        tk.Spinbox(control_frame, from_=8, to=50, textvariable=self.size_var, width=5).grid(row=1, column=1, pady=(10, 0), sticky="w")
        tk.Button(control_frame, text="Generate Random Maze", command=self.generate_random_maze).grid(row=1, column=2, columnspan=2, pady=(10, 0), padx=5)

        # Solve and clear controls.
        tk.Button(control_frame, text="Solve", command=self.solve_maze, bg="lightgreen").grid(row=1, column=5, pady=(10, 0), padx=5)
        tk.Button(control_frame, text="Clear Path", command=self.clear_path).grid(row=1, column=6, pady=(10, 0), padx=5)

        # Animation settings.
        tk.Checkbutton(control_frame, text="Animate Search", variable=self.animate_var).grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="w")
        tk.Label(control_frame, text="Speed:").grid(row=2, column=2, pady=(10, 0), sticky="e")
        tk.Scale(
            control_frame,
            from_=1,
            to=200,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            length=160,
            label="ms/step"
        ).grid(row=2, column=3, columnspan=2, pady=(10, 0), sticky="w")

        # Zoom controls.
        tk.Button(control_frame, text="Zoom +", command=self.zoom_in).grid(row=2, column=5, pady=(10, 0), padx=5)
        tk.Button(control_frame, text="Zoom -", command=self.zoom_out).grid(row=2, column=6, pady=(10, 0), padx=5)

        # Stats label shown below controls.
        self.stats_label = tk.Label(
            self.root,
            text="Load a maze and click Solve.",
            anchor="w",
            justify="left",
            padx=10
        )
        self.stats_label.pack(fill=tk.X)

        # Canvas frame with scrollbars.
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

        # Connect scrollbars to the canvas.
        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)

        # Mouse wheel scrolling.
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)

        # Mouse drag panning.
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.do_pan)

    def cancel_animation(self):
        """
        Cancel any currently scheduled animation step.

        This prevents overlapping animations if the user loads a new maze,
        generates a new one, or solves again before the previous animation
        is finished.
        """
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.animating = False

    def _on_mousewheel(self, event):
        """
        Scroll vertically using the mouse wheel.

        Args:
            event: Tkinter mouse wheel event.
        """
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel(self, event):
        """
        Scroll horizontally using Shift + mouse wheel.

        Args:
            event: Tkinter mouse wheel event.
        """
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def start_pan(self, event):
        """
        Mark the starting point for click-and-drag panning.

        Args:
            event: Tkinter mouse event.
        """
        self.canvas.scan_mark(event.x, event.y)

    def do_pan(self, event):
        """
        Drag the canvas view while the left mouse button is held.

        Args:
            event: Tkinter mouse event.
        """
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def zoom_in(self):
        """
        Increase the size of each maze cell, up to MAX_CELL_SIZE.
        """
        self.current_cell_size = min(MAX_CELL_SIZE, self.current_cell_size + 5)
        self.draw_maze()

    def zoom_out(self):
        """
        Decrease the size of each maze cell, down to MIN_CELL_SIZE.
        """
        self.current_cell_size = max(MIN_CELL_SIZE, self.current_cell_size - 5)
        self.draw_maze()

    def validate_maze(self, maze):
        """
        Validate that a maze is well-formed.

        Rules checked:
            - maze is not empty
            - all rows are the same length
            - only valid symbols are used
            - exactly one S and one E exist

        Args:
            maze (list[str] or list[list[str]]): Maze data to validate.

        Returns:
            tuple[bool, str]:
                (True, "") if valid
                (False, error_message) if invalid
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

    def load_sample_maze(self):
        """
        Load the currently selected built-in sample maze into the GUI.
        """
        self.cancel_animation()

        maze_lines = self.samples[self.sample_var.get()]
        valid, msg = self.validate_maze(maze_lines)
        if not valid:
            messagebox.showerror("Invalid Maze", msg)
            return

        self.maze = [list(row) for row in maze_lines]
        self.path = []
        self.explored = []
        self.draw_maze()
        self.stats_label.config(text=f"Loaded {self.sample_var.get()}")

    def load_maze_from_file(self):
        """
        Load a maze from a text file selected by the user.
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

        Notes:
            - Borders are turned into walls.
            - Internal cells are randomly assigned walls with probability 0.28.
            - S is placed near the top-left.
            - E is placed near the bottom-right.
            - Cells around S and E are opened to reduce immediate trapping.
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

        # Randomly place internal walls.
        for r in range(1, size - 1):
            for c in range(1, size - 1):
                if random.random() < 0.28:
                    maze[r][c] = '#'

        # Place start and end.
        maze[1][1] = 'S'
        maze[size - 2][size - 2] = 'E'

        # Open a few nearby cells around start and end.
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
        then redraw the maze in its unsolved state.
        """
        self.cancel_animation()
        self.path = []
        self.explored = []
        self.draw_maze()
        self.stats_label.config(text="Path cleared.")

    def find_start_end(self, grid):
        """
        Find the start and end cells inside a maze grid.

        Args:
            grid (list[list[str]]): Maze grid.

        Returns:
            tuple:
                start (row, col) or None
                end (row, col) or None
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

        The parent dictionary maps each discovered node to the node
        from which it was first reached.

        Args:
            parent (dict): child -> parent map
            end (tuple[int, int]): End cell

        Returns:
            list[tuple[int, int]]: Path from start to end.
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
        Run BFS directly inside the GUI and also record exploration order
        for animation.

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

        q = deque([start])
        visited = {start}
        parent = {start: None}
        explored_order = []

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
        Run recursive DFS directly inside the GUI and record exploration
        order for animation.

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
            Recursive DFS helper.

            Args:
                r (int): Current row.
                c (int): Current column.

            Returns:
                bool: True if a path to E is found from this cell.
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

            # Remove dead-end cell when backtracking.
            path.pop()
            return False

        found = dfs(start[0], start[1])
        runtime_ms = (time.perf_counter() - start_time) * 1000

        return (path if found else []), len(visited), runtime_ms, explored_order

    def solve_maze(self):
        """
        Solve the currently loaded maze using the selected algorithm.

        Behavior:
            - clears previous solution/animation
            - runs BFS or DFS
            - either animates exploration or draws final result immediately
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
        Animate the search process one explored cell at a time using Tkinter's
        after() scheduler.

        Args:
            explored_order (list[tuple[int, int]]): Order cells were explored.
            final_path (list[tuple[int, int]]): Final solved path.
            algorithm (str): "BFS" or "DFS"
            visited_count (int): Number of visited cells.
            runtime_ms (float): Runtime in milliseconds.
            index (int): Current animation frame index.
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
            algorithm (str): "BFS" or "DFS"
            path (list[tuple[int, int]]): Final path
            visited_count (int): Number of explored cells
            runtime_ms (float): Runtime in milliseconds
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
        Draw the maze onto the canvas.

        Color scheme:
            black      = wall
            white      = open cell
            lightblue  = explored cell
            yellow     = final path
            green      = start
            red        = end

        The canvas uses the current zoom level stored in self.current_cell_size.
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

                # Base coloring.
                color = "white"
                if cell == '#':
                    color = "black"
                elif (r, c) in explored_set:
                    color = "lightblue"

                # Path overrides explored color.
                if (r, c) in path_set:
                    color = "yellow"

                # Start and end override everything else for clarity.
                if cell == 'S':
                    color = "green"
                elif cell == 'E':
                    color = "red"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

                # Draw labels for start and end.
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
    # Create the main application window and start the Tkinter event loop.
    root = tk.Tk()
    root.geometry("1000x700")
    app = MazeApp(root)
    root.mainloop()