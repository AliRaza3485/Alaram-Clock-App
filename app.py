import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from collections import deque
import time

st.set_page_config(page_title="BFS Maze Solver", page_icon="🧩", layout="centered")

# ---------- Maze presets ----------
PRESETS = {
    "Classic": [
        "#O#######",
        "#       #",
        "# ## ## #",
        "# #    ##",
        "# # ##  #",
        "# # ##  #",
        "# # ## ##",
        "#       #",
        "#######X#",
    ],
    "Spiral": [
        "#O########",
        "# ####### #",
        "# #     # #",
        "# # ### # #",
        "# # #X# # #",
        "# # ### # #",
        "# #     # #",
        "# ####### #",
        "#          ",
    ],
    "Open Field": [
        "#O#########",
        "#          #",
        "#  ##  ##  #",
        "#  ##  ##  #",
        "#          #",
        "#  ##  ##  #",
        "#  ##  ##  #",
        "#         X#",
        "############",
    ],
}


def parse_maze(rows):
    width = max(len(r) for r in rows)
    grid = [list(r.ljust(width)) for r in rows]
    return grid


def find_char(grid, ch):
    for i, row in enumerate(grid):
        for j, val in enumerate(row):
            if val == ch:
                return (i, j)
    return None


def neighbors(grid, row, col):
    result = []
    if row > 0:
        result.append((row - 1, col))
    if row + 1 < len(grid):
        result.append((row + 1, col))
    if col > 0:
        result.append((row, col - 1))
    if col + 1 < len(grid[0]):
        result.append((row, col + 1))
    return result


def bfs_steps(grid):
    """Yield (visited_so_far, path_if_found) at each step for animation."""
    start = find_char(grid, "O")
    end = find_char(grid, "X")

    q = deque()
    q.append((start, [start]))
    visited = {start}
    order_visited = [start]

    while q:
        current, path = q.popleft()
        yield set(order_visited), None

        if current == end:
            yield set(order_visited), path
            return

        for n in neighbors(grid, *current):
            r, c = n
            if n in visited or grid[r][c] == "#":
                continue
            visited.add(n)
            order_visited.append(n)
            q.append((n, path + [n]))

    yield set(order_visited), None


def draw_grid(grid, visited=None, path=None):
    rows, cols = len(grid), len(grid[0])
    # 0 = open, 1 = wall, 2 = visited, 3 = path, 4 = start, 5 = end
    arr = np.zeros((rows, cols))
    for i in range(rows):
        for j in range(cols):
            ch = grid[i][j]
            if ch == "#":
                arr[i][j] = 1
            elif ch == "O":
                arr[i][j] = 4
            elif ch == "X":
                arr[i][j] = 5

    if visited:
        for (i, j) in visited:
            if grid[i][j] not in ("O", "X"):
                arr[i][j] = 2
    if path:
        for (i, j) in path:
            if grid[i][j] not in ("O", "X"):
                arr[i][j] = 3

    colors = ["#f4f4f4", "#2b2b2b", "#a7d8ff", "#ffb703", "#2ecc71", "#e63946"]
    cmap = ListedColormap(colors)

    fig, ax = plt.subplots(figsize=(cols / 2.2, rows / 2.2))
    ax.imshow(arr, cmap=cmap, vmin=0, vmax=5)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return fig


# ---------- UI ----------
st.title("🧩 BFS Maze Pathfinding Visualizer")
st.caption("Breadth-First Search finding the shortest path, step by step.")

preset_name = st.selectbox("Choose a maze", list(PRESETS.keys()))
grid = parse_maze(PRESETS[preset_name])

speed = st.slider("Animation speed", min_value=1, max_value=10, value=6)
delay = (11 - speed) * 0.03

placeholder = st.empty()
status = st.empty()

if st.button("▶ Solve Maze", type="primary"):
    final_path = None
    for visited, path in bfs_steps(grid):
        placeholder.pyplot(draw_grid(grid, visited=visited, path=path))
        if path:
            final_path = path
        time.sleep(delay)

    if final_path:
        status.success(f"Path found in {len(final_path) - 1} steps, exploring {len(visited)} cells.")
    else:
        status.error("No path exists in this maze.")
else:
    placeholder.pyplot(draw_grid(grid))
    status.info("Press **Solve Maze** to watch BFS explore the grid and find the shortest route.")

with st.expander("How it works"):
    st.markdown(
        """
        This uses **Breadth-First Search (BFS)** on a grid graph:
        - 🟩 Start, 🟥 End, ⬛ Wall
        - 🟦 Cells visited during the search
        - 🟧 The final shortest path once the end is reached

        BFS explores the maze layer by layer, guaranteeing the first time it reaches
        the end, it has found the *shortest possible path* (in terms of number of steps).
        """
    )
