# Maze Solver GUI (BFS & DFS)

## Course
CPSC 335 – Project 2

## Overview
This project is a Python GUI application that solves mazes using:

- Breadth-First Search (BFS)
- Depth-First Search (DFS)

The application allows users to:
- Load a maze from a `.txt` file
- Generate a random maze
- Select BFS or DFS
- Visualize the solving process (with optional animation)
- Display performance statistics

---

## Team Members & Roles

- Brendon Cozzens– BFS Engineer  
  Implemented BFS solver (`bfs.py`)  
  Ensures shortest path and correctness  

- Jorge Patino– DFS Engineer  
  Implemented DFS solver (`dfs.py`)  
  Handles recursion, backtracking, and correctness  

- Brendon Cozzens & Adonay Yonnas – GUI Engineer  
  Implemented GUI (`gui.py`)  
  Integrated BFS and DFS, visualization, animation  

---

## Features

### Maze Input
- Load maze from `.txt` file
- Generate random maze (adjustable size)

### Maze Rules
- `S` = Start (exactly one)
- `E` = End (exactly one)
- `#` = Wall
- `.` = Open path
- Movement: Up, Down, Left, Right (no diagonals)

### Algorithms
- **BFS**
  - Uses `collections.deque`
  - Guarantees shortest path in steps

- **DFS**
  - Uses recursion
  - Finds a valid path if one exists (not necessarily shortest)

### Visualization
- Maze grid display
- Start (green) and End (red)
- Explored cells (light blue, when animation enabled)
- Final path (yellow)

### Animation (Bonus Feature)
- Step-by-step exploration visualization
- Adjustable speed using slider

### Additional Features
- Zoom in / zoom out
- Clear path button
- Scrollable canvas for large mazes

---

## Output (Displayed in GUI)

After solving:
- Algorithm used (BFS or DFS)
- Path length (number of steps)
- Number of visited/explored cells
- Runtime (milliseconds)

If no path exists:
- Displays **"No Path Found"**

---

## How to Run

1. Make sure Python 3.10+ is installed
2. Place all files in the same directory:
   - `bfs.py`
   - `dfs.py`
   - `gui.py`
3. Run the program:

```bash
python gui.py