import tkinter as tk
from tkinter import filedialog, messagebox
import random

from bfs import solve_bfs
from dfs import solve_dfs


CELL_SIZE = 30


class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver - BFS / DFS")

        self.maze = []
        self.path = []

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

        self.algorithm_var = tk.StringVar(value="BFS")
        self.sample_var = tk.StringVar(value="Sample 1")
        self.size_var = tk.IntVar(value=12)

        self.build_ui()
        self.load_sample_maze()

    def build_ui(self):
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(control_frame, text="Algorithm:").grid(row=0, column=0, sticky="w")
        tk.Radiobutton(control_frame, text="BFS", variable=self.algorithm_var, value="BFS").grid(row=0, column=1, sticky="w")
        tk.Radiobutton(control_frame, text="DFS", variable=self.algorithm_var, value="DFS").grid(row=0, column=2, sticky="w")

        tk.Label(control_frame, text="Samples:").grid(row=0, column=3, padx=(20, 5), sticky="w")
        sample_menu = tk.OptionMenu(control_frame, self.sample_var, *self.samples.keys())
        sample_menu.grid(row=0, column=4, sticky="w")

        tk.Button(control_frame, text="Load Sample", command=self.load_sample_maze).grid(row=0, column=5, padx=5)
        tk.Button(control_frame, text="Load .txt File", command=self.load_maze_from_file).grid(row=0, column=6, padx=5)

        tk.Label(control_frame, text="Random Size:").grid(row=1, column=0, pady=(10, 0), sticky="w")
        tk.Spinbox(control_frame, from_=8, to=30, textvariable=self.size_var, width=5).grid(row=1, column=1, pady=(10, 0), sticky="w")
        tk.Button(control_frame, text="Generate Random Maze", command=self.generate_random_maze).grid(row=1, column=2, columnspan=2, pady=(10, 0), padx=5)

        tk.Button(control_frame, text="Solve", command=self.solve_maze, bg="lightgreen").grid(row=1, column=5, pady=(10, 0), padx=5)
        tk.Button(control_frame, text="Clear Path", command=self.clear_path).grid(row=1, column=6, pady=(10, 0), padx=5)

        self.stats_label = tk.Label(self.root, text="Load a maze and click Solve.", anchor="w", justify="left", padx=10)
        self.stats_label.pack(fill=tk.X)

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(padx=10, pady=10)

    def validate_maze(self, maze):
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
        maze_lines = self.samples[self.sample_var.get()]
        valid, msg = self.validate_maze(maze_lines)
        if not valid:
            messagebox.showerror("Invalid Maze", msg)
            return

        self.maze = [list(row) for row in maze_lines]
        self.path = []
        self.draw_maze()
        self.stats_label.config(text=f"Loaded {self.sample_var.get()}")

    def load_maze_from_file(self):
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
            self.draw_maze()
            self.stats_label.config(text=f"Loaded maze from file: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_random_maze(self):
        size = self.size_var.get()
        maze = [['.' for _ in range(size)] for _ in range(size)]

        # border walls
        for r in range(size):
            maze[r][0] = '#'
            maze[r][size - 1] = '#'
        for c in range(size):
            maze[0][c] = '#'
            maze[size - 1][c] = '#'

        # random internal walls
        for r in range(1, size - 1):
            for c in range(1, size - 1):
                if random.random() < 0.28:
                    maze[r][c] = '#'

        # place S and E
        maze[1][1] = 'S'
        maze[size - 2][size - 2] = 'E'

        # ensure a little space around S and E
        for rr, cc in [(1, 2), (2, 1), (size - 2, size - 3), (size - 3, size - 2)]:
            if 0 <= rr < size and 0 <= cc < size:
                maze[rr][cc] = '.'

        self.maze = maze
        self.path = []
        self.draw_maze()
        self.stats_label.config(text=f"Generated random {size}x{size} maze")

    def clear_path(self):
        self.path = []
        self.draw_maze()
        self.stats_label.config(text="Path cleared.")

    def solve_maze(self):
        if not self.maze:
            messagebox.showwarning("No Maze", "Please load or generate a maze first.")
            return

        algorithm = self.algorithm_var.get()

        try:
            if algorithm == "BFS":
                path, visited_count, runtime_ms = solve_bfs(self.maze)
            else:
                path, visited_count, runtime_ms = solve_dfs(self.maze)

            self.path = path
            self.draw_maze()

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
        except Exception as e:
            messagebox.showerror("Solve Error", str(e))

    def draw_maze(self):
        if not self.maze:
            return

        rows = len(self.maze)
        cols = len(self.maze[0])

        self.canvas.config(width=cols * CELL_SIZE, height=rows * CELL_SIZE)
        self.canvas.delete("all")

        path_set = set(self.path)

        for r in range(rows):
            for c in range(cols):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                cell = self.maze[r][c]

                color = "white"
                if cell == '#':
                    color = "black"
                elif cell == 'S':
                    color = "green"
                elif cell == 'E':
                    color = "red"
                elif (r, c) in path_set:
                    color = "yellow"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

                if cell in ('S', 'E'):
                    self.canvas.create_text(
                        x1 + CELL_SIZE / 2,
                        y1 + CELL_SIZE / 2,
                        text=cell,
                        fill="white",
                        font=("Arial", 12, "bold")
                    )


if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()