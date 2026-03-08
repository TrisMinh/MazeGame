# 🌀 Maze Pathfinding Game — Walkthrough

## What Was Built

A complete Python Maze Game ([maze_game.py](file:///c:/Users/minht/OneDrive/Desktop/MazeGame/maze_game.py)) featuring:
- **Beautiful Pygame GUI** with dark theme, color-coded overlays, animation
- **3 AI pathfinding algorithms**: DFS, BFS, A*
- **Step-by-step animation** showing exploration + final path
- **Stats panel** (path length, nodes explored, time, winners)
- **Algorithm explanations** in Vietnamese for non-technical users

---

## Architecture

| Class | Responsibility |
|---|---|
| [MazeGenerator](file:///c:/Users/minht/OneDrive/Desktop/MazeGame/maze_game.py#103-151) | Recursive Backtracker — guaranteed solvable maze |
| [PathFinder](file:///c:/Users/minht/OneDrive/Desktop/MazeGame/_test_logic.py#26-81) | Static methods: `.dfs()`, `.bfs()`, `.astar()` |
| [AnimationManager](file:///c:/Users/minht/OneDrive/Desktop/MazeGame/maze_game.py#353-421) | State machine: `idle → visiting → pathing → done` |
| [StatsPanel](file:///c:/Users/minht/OneDrive/Desktop/MazeGame/maze_game.py#428-598) | Right-side panel with results + explanations |
| [Button](file:///c:/Users/minht/OneDrive/Desktop/MazeGame/maze_game.py#604-649) | UI widget with hover effects |
| [MazeGame](file:///c:/Users/minht/OneDrive/Desktop/MazeGame/maze_game.py#655-1062) | Main game loop, event handling, rendering |

---

## Verification Results

### Syntax Check
- ✅ `ast.parse()` — no errors
- 6 classes, 35 functions detected

### Algorithm Logic (headless test, seed=42, 25×25 maze)
| Algorithm | Path Length | Nodes Explored | Time |
|---|---|---|---|
| BFS | 169 | (varies) | <1ms |
| A* | 169 | **fewer than BFS** | <1ms |
| DFS | longer | varies | <1ms |

- ✅ **BFS path == A* path** (both optimal) — assertion passed
- ✅ pygame-ce 2.5.7 confirmed installed

---

## How to Run

```bash
cd "C:\Users\minht\OneDrive\Desktop\MazeGame"
python maze_game.py
```

---

## Controls

| Action | Button / Key |
|---|---|
| Run DFS | `🔵 Run DFS` or `[1]` |
| Run BFS | `🔷 Run BFS` or `[2]` |
| Run A* | `⭐ Run A*` or `[3]` |
| Compare all 3 | `📊 Compare All` or `[C]` |
| New maze | `🔄 New Maze` or `[R]` |

---

## Color Legend

| Color | Meaning |
|---|---|
| 🟢 Green | Start |
| 🔴 Red | Goal |
| 🟣 Purple | DFS visit / path |
| 🔵 Blue | BFS visit / path |
| 🟡 Yellow | A* visit / path |

---

## Algorithm Summary (for users)

- **DFS** — Goes deep first (stack). Fast but NOT shortest path.
- **BFS** — Expands level by level (queue). ALWAYS shortest path, more RAM.
- **A\*** — BFS + Manhattan heuristic. Shortest path AND explores FEWER nodes.
