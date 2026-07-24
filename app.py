import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import deque
import time

st.set_page_config(page_title="The Maze of Paths", page_icon="🕯️", layout="centered")

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
BG_TOP = "#12101a"
BG_BOTTOM = "#1b1830"
CARD_BG = "#1c1a2b"
FRAME_GLOW = "#caa057"
WALL_FILL = "#2a2740"
WALL_GROUT = "#161425"
FLOOR_FILL = "#ede3cf"
START_COLOR = "#34d399"
END_COLOR = "#f6c85f"
TRAIL_COLOR = "#7dc8ff"
PATH_COLOR = "#ff9d4d"
TEXT_CREAM = "#f3e9d2"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap');

.stApp {{
    background: radial-gradient(ellipse at top, {BG_BOTTOM} 0%, {BG_TOP} 70%);
}}

html, body, [class*="css"]  {{
    font-family: 'Inter', sans-serif;
}}

h1#maze-title {{
    font-family: 'Cinzel', serif;
    font-weight: 700;
    text-align: center;
    color: {TEXT_CREAM};
    letter-spacing: 0.06em;
    font-size: 2.1rem;
    margin-bottom: 0;
    text-shadow: 0 0 18px rgba(246, 200, 95, 0.35);
}}

p#maze-subtitle {{
    font-family: 'Inter', sans-serif;
    text-align: center;
    color: #9b93b8;
    font-size: 0.95rem;
    margin-top: 4px;
    letter-spacing: 0.02em;
}}

[data-testid="stImage"] {{
    display: flex;
    justify-content: center;
}}

[data-testid="stImage"] img {{
    border-radius: 14px;
    border: 2px solid {FRAME_GLOW};
    box-shadow: 0 0 0 6px {CARD_BG}, 0 0 30px rgba(202, 160, 87, 0.25), 0 12px 40px rgba(0,0,0,0.55);
}}

div[data-testid="stVerticalBlock"] div.stButton > button {{
    font-family: 'Cinzel', serif;
    background: linear-gradient(180deg, #e8b85a 0%, #c8912f 100%);
    color: #211a0a;
    border: none;
    border-radius: 8px;
    font-weight: 700;
    letter-spacing: 0.04em;
    padding: 0.55rem 1.2rem;
    box-shadow: 0 4px 14px rgba(200, 145, 47, 0.4);
    transition: transform 0.15s ease;
}}
div[data-testid="stVerticalBlock"] div.stButton > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(200, 145, 47, 0.55);
}}

.scoreboard {{
    font-family: 'JetBrains Mono', monospace;
    background: {CARD_BG};
    border: 1px solid rgba(202, 160, 87, 0.35);
    border-radius: 10px;
    padding: 14px 18px;
    color: {TEXT_CREAM};
    text-align: center;
    font-size: 0.95rem;
    margin-top: 14px;
}}

section[data-testid="stSidebar"] {{
    background: {BG_TOP};
    border-right: 1px solid rgba(202, 160, 87, 0.2);
}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Maze presets
# ---------------------------------------------------------------------------
PRESETS = {
    "The Old Corridor": [
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
    "The Spiral Vault": [
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
    "The Open Hall": [
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
    return [list(r.ljust(width)) for r in rows]


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
    start = find_char(grid, "O")
    end = find_char(grid, "X")

    q = deque()
    q.append((start, [start]))
    visited = {start}
    order_visited = [start]

    while q:
        current, path = q.popleft()
        yield list(order_visited), None

        if current == end:
            yield list(order_visited), path
            return

        for n in neighbors(grid, *current):
            r, c = n
            if n in visited or grid[r][c] == "#":
                continue
            visited.add(n)
            order_visited.append(n)
            q.append((n, path + [n]))

    yield list(order_visited), None


# ---------------------------------------------------------------------------
# Rendering — stylized "dungeon" maze
# ---------------------------------------------------------------------------
def draw_grid(grid, visited=None, path=None):
    rows, cols = len(grid), len(grid[0])
    visited = visited or []
    n_visited = len(visited)

    fig, ax = plt.subplots(figsize=(cols / 1.9, rows / 1.9))
    fig.patch.set_facecolor(CARD_BG)
    ax.set_facecolor(CARD_BG)

    for i in range(rows):
        for j in range(cols):
            ch = grid[i][j]
            y = rows - 1 - i  # flip so row 0 renders at the top

            if ch == "#":
                ax.add_patch(patches.Rectangle((j, y), 1, 1, facecolor=WALL_FILL,
                                                edgecolor=WALL_GROUT, linewidth=1.4))
                offset = 0.5 if i % 2 == 0 else 0.0
                ax.plot([j, j + 1], [y + 0.5, y + 0.5], color=WALL_GROUT, linewidth=0.8, alpha=0.6)
                if 0 < offset < 1:
                    ax.plot([j + offset, j + offset], [y, y + 1], color=WALL_GROUT, linewidth=0.8, alpha=0.5)
            else:
                ax.add_patch(patches.Rectangle((j, y), 1, 1, facecolor=FLOOR_FILL,
                                                edgecolor="#d8cba8", linewidth=0.4))

    # explored trail — fading footsteps
    for idx, (r, c) in enumerate(visited):
        if grid[r][c] in ("O", "X"):
            continue
        y = rows - 1 - r
        recency = (idx + 1) / max(n_visited, 1)
        alpha = 0.15 + 0.55 * recency
        circ = patches.Circle((c + 0.5, y + 0.5), 0.16, facecolor=TRAIL_COLOR,
                               edgecolor="none", alpha=alpha, zorder=3)
        ax.add_patch(circ)

    # solved path — glowing trail line
    if path:
        xs = [c + 0.5 for (r, c) in path]
        ys = [rows - 1 - r + 0.5 for (r, c) in path]
        ax.plot(xs, ys, color=PATH_COLOR, linewidth=6, alpha=0.25, zorder=4, solid_capstyle="round")
        ax.plot(xs, ys, color=PATH_COLOR, linewidth=2.5, alpha=0.95, zorder=5, solid_capstyle="round")

    # start marker
    start = find_char(grid, "O")
    if start:
        r, c = start
        y = rows - 1 - r
        for radius, alpha in [(0.42, 0.15), (0.3, 0.3), (0.2, 1.0)]:
            ax.add_patch(patches.Circle((c + 0.5, y + 0.5), radius, facecolor=START_COLOR,
                                         edgecolor="none", alpha=alpha, zorder=6))

    # end marker
    end = find_char(grid, "X")
    if end:
        r, c = end
        y = rows - 1 - r
        for radius, alpha in [(0.42, 0.18), (0.3, 0.35), (0.2, 1.0)]:
            ax.add_patch(patches.Circle((c + 0.5, y + 0.5), radius, facecolor=END_COLOR,
                                         edgecolor="none", alpha=alpha, zorder=6))
        ax.scatter([c + 0.5], [y + 0.5], marker="*", s=90, color="#3a2b00", zorder=7)

    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout(pad=0.4)
    return fig


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.markdown('<h1 id="maze-title">🕯️ The Maze of Paths</h1>', unsafe_allow_html=True)
st.markdown('<p id="maze-subtitle">Watch Breadth-First Search light a trail to the shortest way out</p>',
            unsafe_allow_html=True)
st.write("")

with st.sidebar:
    st.markdown("### ⚙️ Controls")
    preset_name = st.selectbox("Choose a chamber", list(PRESETS.keys()))
    speed = st.slider("Torch speed", min_value=1, max_value=10, value=6)
    st.markdown("---")
    st.markdown(
        "**Legend**\n\n"
        "🟢 Start &nbsp;·&nbsp; 🟡 Exit\n\n"
        "🔵 Explored cell\n\n"
        "🟠 Shortest path"
    )

grid = parse_maze(PRESETS[preset_name])
delay = (11 - speed) * 0.025

placeholder = st.empty()
scoreboard = st.empty()

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    solve_clicked = st.button("🔥 Light the Torch", type="primary", use_container_width=True)

if solve_clicked:
    final_path = None
    last_visited = []
    for visited, path in bfs_steps(grid):
        last_visited = visited
        placeholder.pyplot(draw_grid(grid, visited=visited, path=path))
        if path:
            final_path = path
        time.sleep(delay)

    if final_path:
        scoreboard.markdown(
            f'<div class="scoreboard">✅ PATH FOUND &nbsp;|&nbsp; '
            f'{len(final_path) - 1} STEPS &nbsp;|&nbsp; '
            f'{len(last_visited)} CELLS EXPLORED</div>',
            unsafe_allow_html=True,
        )
    else:
        scoreboard.markdown(
            '<div class="scoreboard">❌ NO PATH EXISTS IN THIS CHAMBER</div>',
            unsafe_allow_html=True,
        )
else:
    placeholder.pyplot(draw_grid(grid))
    scoreboard.markdown(
        '<div class="scoreboard">Press <b>Light the Torch</b> to begin the search</div>',
        unsafe_allow_html=True,
    )

with st.expander("How the search works"):
    st.markdown(
        """
        This uses **Breadth-First Search (BFS)** on a grid graph — exploring the
        maze one ring of distance at a time. Because it expands layer by layer,
        the very first time it reaches the exit is guaranteed to be along the
        **shortest possible route**.

        - 🔵 Blue glow — cells visited during the search, fading with age
        - 🟠 Orange trail — the final shortest path once the exit is found
        """
    )