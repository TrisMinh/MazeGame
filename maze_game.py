"""
=============================================================================
  MAZE PATHFINDING GAME — Pygame Edition
=============================================================================
  Tác giả  : AI Assistant
  Ngày     : 2026-03-08
  Phiên bản: 1.0

  MÔ TẢ:
    Một trò chơi mê cung tương tác được xây dựng bằng Python + Pygame.
    AI tự động tìm đường từ Start → Goal sử dụng 3 thuật toán:
      1. DFS  (Depth-First Search)
      2. BFS  (Breadth-First Search)
      3. A*   (A-Star)

  CẤU TRÚC CODE:
    ┌─────────────────────────────────────────────────────────────┐
    │  1. Constants & Color Palette                               │
    │  2. MazeGenerator  – Tạo mê cung bằng Recursive Backtracker│
    │  3. PathFinder      – DFS / BFS / A*                        │
    │  4. AnimationManager– Quản lý animation từng bước           │
    │  5. StatsPanel      – Hiển thị thống kê & giải thích       │
    │  6. Button          – Widget nút bấm                        │
    │  7. MazeGame        – Vòng lặp chính (main game loop)       │
    │  8. main()          – Điểm khởi động                        │
    └─────────────────────────────────────────────────────────────┘

  CÁCH CHẠY:
    pip install pygame
    python maze_game.py
=============================================================================
"""

import pygame
import sys
import random
import time
import heapq
from collections import deque

# ═══════════════════════════════════════════════════════════════════════════
#  1. CONSTANTS & COLOR PALETTE
# ═══════════════════════════════════════════════════════════════════════════

# =============================================================================
#  ĐỔI KÍCH THƯỚC MAZE — Chỉnh ở đây!
#  ─────────────────────────────────────────────────────────────────────────
#  COLS / ROWS : số cột / hàng (phải là SỐ LẺ: 15, 21, 25, 31, 41, 61...)
#  CELL_SIZE   : kích thước pixel mỗi ô
#
#  Preset gợi ý:
#    Nhỏ   (nhanh)   : COLS=15,  ROWS=15,  CELL_SIZE=36
#    Vừa   (mặc định): COLS=25,  ROWS=25,  CELL_SIZE=28   ← đang dùng
#    Lớn             : COLS=41,  ROWS=41,  CELL_SIZE=17
#    Rất lớn         : COLS=61,  ROWS=61,  CELL_SIZE=11
#    Siêu lớn        : COLS=101, ROWS=101, CELL_SIZE=7
# =============================================================================
COLS        = 61   # ← đổi số cột ở đây (số lẻ)
ROWS        = 61   # ← đổi số hàng ở đây (số lẻ, nên bằng COLS)
CELL_SIZE   = 11   # ← đổi kích thước ô pixel ở đây

# --- Tự động làm tròn lên số lẻ (nếu nhập số chẵn vẫn hoạt động!) ---
COLS = COLS if COLS % 2 == 1 else COLS + 1
ROWS = ROWS if ROWS % 2 == 1 else ROWS + 1

# --- Window layout (tự động tính theo COLS/ROWS/CELL_SIZE) ---
MAZE_X_OFFSET   = 20
MAZE_Y_OFFSET   = 80
PANEL_WIDTH     = 340
WINDOW_W        = COLS * CELL_SIZE + MAZE_X_OFFSET * 2 + PANEL_WIDTH
WINDOW_H        = max(ROWS * CELL_SIZE + MAZE_Y_OFFSET + 58, 780)

# --- Animation speed ---
BASE_DELAY      = 5              # ms giữa mỗi bước animation
FAST_DELAY      = 2

# --- Color palette (R, G, B) ---
C_BG            = (15, 17, 26)       # nền tối
C_WALL          = (30, 35, 55)       # tường mê cung
C_PASSAGE       = (240, 242, 255)    # đường đi
C_START         = (39, 200, 107)     # ô bắt đầu (xanh lá)
C_GOAL          = (230, 60, 60)      # ô đích (đỏ)
C_GRID_LINE     = (45, 50, 75)       # lưới mờ

# Màu thuật toán
C_DFS_VISIT     = (160, 80, 230)     # DFS đang duyệt – tím nhạt
C_DFS_PATH      = (200, 100, 255)    # DFS đường cuối – tím sáng
C_BFS_VISIT     = (40, 120, 230)     # BFS đang duyệt – xanh dương nhạt
C_BFS_PATH      = (80, 180, 255)     # BFS đường cuối – xanh dương sáng
C_ASTAR_VISIT   = (200, 140, 30)     # A* đang duyệt – cam nhạt
C_ASTAR_PATH    = (255, 200, 50)     # A* đường cuối – vàng

# UI Colors
C_PANEL_BG      = (22, 25, 40)
C_PANEL_BORDER  = (60, 70, 110)
C_TEXT_PRIMARY  = (230, 235, 255)
C_TEXT_SECONDARY= (140, 150, 190)
C_TEXT_ACCENT   = (100, 200, 255)
C_BTN_DFS       = (140, 60, 220)
C_BTN_BFS       = (40, 120, 230)
C_BTN_ASTAR     = (200, 150, 30)
C_BTN_COMPARE   = (50, 180, 130)
C_BTN_RESET     = (180, 60, 70)
C_BTN_HOVER     = (255, 255, 255, 40)

# Ánh xạ tên thuật toán → màu sắc
ALGO_COLORS = {
    "DFS"  : {"visit": C_DFS_VISIT,   "path": C_DFS_PATH,   "btn": C_BTN_DFS  },
    "BFS"  : {"visit": C_BFS_VISIT,   "path": C_BFS_PATH,   "btn": C_BTN_BFS  },
    "A*"   : {"visit": C_ASTAR_VISIT, "path": C_ASTAR_PATH, "btn": C_BTN_ASTAR},
}

# ═══════════════════════════════════════════════════════════════════════════
#  2. MAZE GENERATOR
#    Sử dụng thuật toán "Recursive Backtracker" (DFS ngẫu nhiên)
#    để sinh mê cung – đảm bảo mọi ô đều có thể đến được.
# ═══════════════════════════════════════════════════════════════════════════

class MazeGenerator:
    """
    Tạo mê cung 2D bằng thuật toán Recursive Backtracker.

    Cách hoạt động:
      1. Bắt đầu từ một ô ngẫu nhiên, đánh dấu đã thăm.
      2. Chọn ngẫu nhiên một hàng xóm chưa thăm (cách 2 bước).
      3. Dỡ tường giữa ô hiện tại và hàng xóm đó.
      4. Đệ quy sang hàng xóm. Quay lui nếu không còn hàng xóm nào.
      5. Kết quả: mê cung hoàn chỉnh, không có vòng lặp kín.

    grid[row][col] = 0 → tường
    grid[row][col] = 1 → đường đi
    """

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        # Tất cả ô bắt đầu là tường (0)
        self.grid = [[0] * cols for _ in range(rows)]

    # ------------------------------------------------------------------
    def generate(self) -> list[list[int]]:
        """Sinh mê cung, trả về grid 2D."""
        # Dùng iterative stack thay vì đệ quy
        # → không bị RecursionError dù maze cực lớn (101x101, 201x201...)
        self._carve_iterative(1, 1)
        # Đảm bảo ô start & goal luôn là đường đi
        self.grid[1][1] = 1
        self.grid[self.rows - 2][self.cols - 2] = 1
        return self.grid

    # ------------------------------------------------------------------
    def _carve_iterative(self, start_r: int, start_c: int):
        """
        Khoét đường bằng vòng lặp (stack-based DFS).
        Thay thế hoàn toàn cho đệ quy — hoạt động với mọi kích thước maze.
        """
        DIRS = [(0, 2), (0, -2), (2, 0), (-2, 0)]

        self.grid[start_r][start_c] = 1
        stack = [(start_r, start_c)]

        while stack:
            r, c = stack[-1]          # nhìn ô trên đỉnh stack

            # Tìm các hàng xóm chưa thăm (cách 2 ô)
            neighbors = []
            for dr, dc in DIRS:
                nr, nc = r + dr, c + dc
                if (1 <= nr < self.rows - 1 and
                        1 <= nc < self.cols - 1 and
                        self.grid[nr][nc] == 0):
                    neighbors.append((dr, dc, nr, nc))

            if neighbors:
                # Chọn ngẫu nhiên một hàng xóm
                dr, dc, nr, nc = random.choice(neighbors)
                # Dỡ tường giữa
                self.grid[r + dr // 2][c + dc // 2] = 1
                self.grid[nr][nc] = 1
                stack.append((nr, nc))   # đi tiếp
            else:
                stack.pop()              # quay lui


# ═══════════════════════════════════════════════════════════════════════════
#  3. PATHFINDER — DFS / BFS / A*
#    Mỗi thuật toán trả về:
#      visited_order: list[tuple] – thứ tự các node đã duyệt
#      path         : list[tuple] – đường đi cuối cùng từ start → goal
#      stats        : dict        – số liệu thống kê
# ═══════════════════════════════════════════════════════════════════════════

class PathFinder:
    """
    Chứa 3 thuật toán tìm đường trên lưới 2D.
    Tất cả đều nhận grid, start, goal và không sửa đổi grid gốc.
    """

    DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]   # phải, trái, xuống, lên

    # ------------------------------------------------------------------
    @staticmethod
    def _neighbors(grid, r, c):
        """Trả về danh sách các ô kề hợp lệ (là đường đi, trong lưới)."""
        rows, cols = len(grid), len(grid[0])
        result = []
        for dr, dc in PathFinder.DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                result.append((nr, nc))
        return result

    # ------------------------------------------------------------------
    @staticmethod
    def _reconstruct_path(came_from: dict, start: tuple, goal: tuple) -> list:
        """
        Từ dict {node: parent}, truy ngược từ goal về start để lấy đường đi.
        """
        path = []
        node = goal
        while node is not None:
            path.append(node)
            node = came_from.get(node)
        path.reverse()
        return path if path[0] == start else []

    # ══════════════════════════════════════════════════════════════════
    @staticmethod
    def dfs(grid, start: tuple, goal: tuple) -> dict:
        """
        DFS – Depth First Search (Tìm kiếm theo chiều sâu)
        ─────────────────────────────────────────────────
        • Dùng ngăn xếp (stack) – LIFO.
        • Luôn đi sâu nhất có thể trước khi quay lui.
        • Không đảm bảo đường ngắn nhất.
        • Nhanh tìm ra một đường đi bất kỳ.
        """
        t_start = time.perf_counter()

        stack        = [start]
        came_from    = {start: None}   # {node: node_cha}
        visited      = set()
        visited_order= []              # thứ tự duyệt để animation

        while stack:
            current = stack.pop()     # lấy từ đỉnh stack (LIFO)

            if current in visited:
                continue
            visited.add(current)
            visited_order.append(current)

            if current == goal:
                break

            # Thêm hàng xóm vào stack
            for nb in PathFinder._neighbors(grid, *current):
                if nb not in visited:
                    stack.append(nb)
                    if nb not in came_from:
                        came_from[nb] = current

        elapsed = time.perf_counter() - t_start
        path    = PathFinder._reconstruct_path(came_from, start, goal) \
                  if goal in came_from else []

        return {
            "visited_order": visited_order,
            "path"         : path,
            "nodes_explored": len(visited_order),
            "path_length"  : len(path),
            "time_ms"      : elapsed * 1000,
        }

    # ══════════════════════════════════════════════════════════════════
    @staticmethod
    def bfs(grid, start: tuple, goal: tuple) -> dict:
        """
        BFS – Breadth First Search (Tìm kiếm theo chiều rộng)
        ──────────────────────────────────────────────────────
        • Dùng hàng đợi (queue) – FIFO.
        • Khám phá tất cả node gần nhất trước (theo số bước).
        • ĐẢM BẢO đường đi ngắn nhất (tính theo số bước).
        • Tốn nhiều bộ nhớ hơn DFS vì phải lưu toàn bộ tầng hiện tại.
        """
        t_start = time.perf_counter()

        queue        = deque([start])
        came_from    = {start: None}
        visited_order= []

        while queue:
            current = queue.popleft()   # lấy từ đầu queue (FIFO)
            visited_order.append(current)

            if current == goal:
                break

            for nb in PathFinder._neighbors(grid, *current):
                if nb not in came_from:
                    came_from[nb] = current
                    queue.append(nb)

        elapsed = time.perf_counter() - t_start
        path    = PathFinder._reconstruct_path(came_from, start, goal) \
                  if goal in came_from else []

        return {
            "visited_order": visited_order,
            "path"         : path,
            "nodes_explored": len(visited_order),
            "path_length"  : len(path),
            "time_ms"      : elapsed * 1000,
        }

    # ══════════════════════════════════════════════════════════════════
    @staticmethod
    def astar(grid, start: tuple, goal: tuple) -> dict:
        """
        A* – A-Star Search
        ──────────────────
        • Kết hợp Dijkstra (g: chi phí thực tế) + Heuristic (h: ước lượng).
        • f(n) = g(n) + h(n)
        • h = khoảng cách Manhattan đến goal.
        • Luôn tìm đường ngắn nhất VÀ thường NHANH hơn BFS vì
          ưu tiên khám phá node gần goal hơn.
        """
        t_start = time.perf_counter()

        def heuristic(a, b):
            """Khoảng cách Manhattan – phù hợp cho lưới 4 chiều."""
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        # Heap: (f_score, tie_breaker, node)
        open_heap    = [(heuristic(start, goal), 0, start)]
        came_from    = {start: None}
        g_score      = {start: 0}      # chi phí thực tế từ start
        counter      = 1               # để phá tie-break
        visited_order= []
        closed       = set()

        while open_heap:
            f, _, current = heapq.heappop(open_heap)

            if current in closed:
                continue
            closed.add(current)
            visited_order.append(current)

            if current == goal:
                break

            for nb in PathFinder._neighbors(grid, *current):
                if nb in closed:
                    continue

                tentative_g = g_score[current] + 1   # mỗi bước = chi phí 1

                if tentative_g < g_score.get(nb, float('inf')):
                    came_from[nb] = current
                    g_score[nb]   = tentative_g
                    f_new         = tentative_g + heuristic(nb, goal)
                    heapq.heappush(open_heap, (f_new, counter, nb))
                    counter += 1

        elapsed = time.perf_counter() - t_start
        path    = PathFinder._reconstruct_path(came_from, start, goal) \
                  if goal in came_from else []

        return {
            "visited_order": visited_order,
            "path"         : path,
            "nodes_explored": len(visited_order),
            "path_length"  : len(path),
            "time_ms"      : elapsed * 1000,
        }


# ═══════════════════════════════════════════════════════════════════════════
#  4. ANIMATION MANAGER
#    Quản lý việc phát lại animation (visited nodes → final path)
#    theo từng frame của Pygame loop.
# ═══════════════════════════════════════════════════════════════════════════

class AnimationManager:
    """
    Lưu trữ trạng thái animation và cập nhật theo thời gian thực.

    States:
      'idle'     → chờ lệnh
      'visiting' → đang hiển thị các node đã duyệt
      'pathing'  → đang hiển thị đường đi cuối cùng
      'done'     → hoàn thành
    """

    def __init__(self):
        self.reset()

    # ------------------------------------------------------------------
    def reset(self):
        """Xoá toàn bộ trạng thái animation."""
        self.state         = 'idle'
        self.algo_name     = None
        self.visited_order = []        # danh sách node đã duyệt
        self.path          = []        # đường đi cuối cùng
        self.vis_index     = 0         # index hiện tại trong visited_order
        self.path_index    = 0         # index hiện tại trong path
        self.shown_visited = set()     # các node đã vẽ (visited)
        self.shown_path    = set()     # các node đã vẽ (path)
        self.delay_ms      = BASE_DELAY
        self.last_tick     = 0
        self.stats         = None

    # ------------------------------------------------------------------
    def start(self, algo_name: str, result: dict, delay: int = BASE_DELAY):
        """Bắt đầu animation cho một thuật toán."""
        self.reset()
        self.state         = 'visiting'
        self.algo_name     = algo_name
        self.visited_order = result["visited_order"]
        self.path          = result["path"]
        self.delay_ms      = delay
        self.stats         = result
        self.last_tick     = pygame.time.get_ticks()

    # ------------------------------------------------------------------
    def update(self):
        """Gọi mỗi frame – cập nhật trạng thái animation."""
        now = pygame.time.get_ticks()
        if now - self.last_tick < self.delay_ms:
            return                        # chưa đến lúc next step

        self.last_tick = now

        if self.state == 'visiting':
            if self.vis_index < len(self.visited_order):
                self.shown_visited.add(self.visited_order[self.vis_index])
                self.vis_index += 1
            else:
                # Chuyển sang vẽ đường đi
                self.state = 'pathing'

        elif self.state == 'pathing':
            if self.path_index < len(self.path):
                self.shown_path.add(self.path[self.path_index])
                self.path_index += 1
            else:
                self.state = 'done'

    # ------------------------------------------------------------------
    def is_done(self) -> bool:
        return self.state == 'done'


# ═══════════════════════════════════════════════════════════════════════════
#  5. STATS PANEL
#    Vẽ panel thống kê + giải thích thuật toán ở bên phải màn hình.
# ═══════════════════════════════════════════════════════════════════════════

class StatsPanel:
    """Hiển thị kết quả và giải thích thuật toán trên panel bên phải."""

    # Giải thích ngắn gọn từng thuật toán (hiển thị sau khi chạy xong)
    EXPLANATIONS = {
        "DFS": [
            "DFS – Depth First Search",
            "─" * 26,
            "• Đi sâu nhất có thể theo",
            "  một hướng trước.",
            "• Dùng STACK (vào sau ra trước).",
            "• Không đảm bảo đường ngắn nhất.",
            "• Tốt khi maze rất sâu hoặc",
            "  khi chỉ cần tìm 1 đường.",
        ],
        "BFS": [
            "BFS – Breadth First Search",
            "─" * 26,
            "• Khám phá tất cả node cùng",
            "  khoảng cách trước.",
            "• Dùng QUEUE (vào trước ra trước).",
            "• ĐẢM BẢO đường ngắn nhất",
            "  (đếm theo số bước).",
            "• Tốn nhiều RAM hơn DFS.",
        ],
        "A*": [
            "A* – A-Star Search",
            "─" * 26,
            "• Kết hợp BFS + Heuristic.",
            "• f(n)=g(n)+h(n)",
            "  g: chi phí đã đi thực tế",
            "  h: ước lượng Manhattan đến goal",
            "• Ưu tiên node 'có vẻ gần goal'.",
            "• Nhanh nhất & tối ưu nhất.",
        ],
    }

    def __init__(self, x: int, y: int, w: int, h: int, font_sm, font_md, font_lg):
        self.rect    = pygame.Rect(x, y, w, h)
        self.font_sm = font_sm
        self.font_md = font_md
        self.font_lg = font_lg
        # Lưu kết quả của các lần chạy: {algo_name: stats_dict}
        self.results : dict = {}
        self.scroll_y: int  = 0

    # ------------------------------------------------------------------
    def add_result(self, algo_name: str, stats: dict):
        self.results[algo_name] = stats

    # ------------------------------------------------------------------
    def clear(self):
        self.results   = {}
        self.scroll_y  = 0

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface):
        """Vẽ toàn bộ panel."""
        # Nền panel
        panel_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        panel_surf.fill((*C_PANEL_BG, 230))
        surface.blit(panel_surf, self.rect.topleft)

        # Viền
        pygame.draw.rect(surface, C_PANEL_BORDER, self.rect, 2, border_radius=8)

        y = self.rect.y + 14
        x = self.rect.x + 14
        w = self.rect.w - 28

        # Tiêu đề panel
        title = self.font_md.render("📊 Kết quả & Phân tích", True, C_TEXT_ACCENT)
        surface.blit(title, (x, y))
        y += title.get_height() + 6

        pygame.draw.line(surface, C_PANEL_BORDER, (x, y), (x + w, y))
        y += 10

        if not self.results:
            hint = self.font_sm.render("Chọn thuật toán và nhấn nút để chạy.", True, C_TEXT_SECONDARY)
            surface.blit(hint, (x, y))
            y += 30

            # Vẽ legend màu sắc
            for algo, info in ALGO_COLORS.items():
                pygame.draw.rect(surface, info["path"], (x, y + 3, 14, 14), border_radius=3)
                txt = self.font_sm.render(algo, True, C_TEXT_PRIMARY)
                surface.blit(txt, (x + 20, y))
                y += 22
            return

        # Bảng kết quả từng thuật toán
        order = ["DFS", "BFS", "A*"]
        for algo in order:
            if algo not in self.results:
                continue
            stats   = self.results[algo]
            color   = ALGO_COLORS[algo]["path"]

            # Header thuật toán
            pygame.draw.rect(surface, (*color, 50), (x - 2, y - 2, w + 4, 22),
                             border_radius=4)
            hdr = self.font_md.render(f"▶ {algo}", True, color)
            surface.blit(hdr, (x + 2, y))
            y += 24

            rows_data = [
                ("Path length",     f"{stats['path_length']} bước" if stats['path_length'] else "Không tìm được"),
                ("Nodes explored",  f"{stats['nodes_explored']}"),
                ("Time",            f"{stats['time_ms']:.3f} ms"),
            ]
            for label, val in rows_data:
                lbl_surf = self.font_sm.render(f"  {label}:", True, C_TEXT_SECONDARY)
                val_surf = self.font_sm.render(val, True, C_TEXT_PRIMARY)
                surface.blit(lbl_surf, (x, y))
                surface.blit(val_surf, (x + w - val_surf.get_width(), y))
                y += 18
            y += 6

        # So sánh winner
        if len(self.results) >= 2:
            pygame.draw.line(surface, C_PANEL_BORDER, (x, y), (x + w, y))
            y += 8
            cmp_txt = self.font_sm.render("🏆 So sánh", True, C_TEXT_ACCENT)
            surface.blit(cmp_txt, (x, y))
            y += 20

            valid = {a: s for a, s in self.results.items() if s["path_length"] > 0}
            if valid:
                fastest   = min(valid, key=lambda a: valid[a]["time_ms"])
                shortest  = min(valid, key=lambda a: valid[a]["path_length"])
                efficient = min(valid, key=lambda a: valid[a]["nodes_explored"])

                lines = [
                    ("⚡ Nhanh nhất",   fastest,   ALGO_COLORS[fastest]["path"]),
                    ("📏 Đường ngắn",   shortest,  ALGO_COLORS[shortest]["path"]),
                    ("🧠 Ít node nhất", efficient, ALGO_COLORS[efficient]["path"]),
                ]
                for label, winner, col in lines:
                    lbl = self.font_sm.render(label + ":", True, C_TEXT_SECONDARY)
                    win = self.font_sm.render(winner, True, col)
                    surface.blit(lbl, (x, y))
                    surface.blit(win, (x + w - win.get_width(), y))
                    y += 18
                y += 8

        # Giải thích từng thuật toán đã chạy
        pygame.draw.line(surface, C_PANEL_BORDER, (x, y), (x + w, y))
        y += 8
        ex_hdr = self.font_sm.render("💡 Giải thích thuật toán", True, C_TEXT_ACCENT)
        surface.blit(ex_hdr, (x, y))
        y += 20

        for algo in order:
            if algo not in self.results:
                continue
            color = ALGO_COLORS[algo]["path"]
            for line in self.EXPLANATIONS[algo]:
                if y > self.rect.bottom - 20:
                    break
                if line.startswith("─"):
                    pygame.draw.line(surface, (*color, 120),
                                     (x, y + 6), (x + w, y + 6))
                    y += 14
                else:
                    style_col = color if not line.startswith("•") else C_TEXT_PRIMARY
                    txt_surf  = self.font_sm.render(line, True, style_col)
                    surface.blit(txt_surf, (x, y))
                    y += 16
            y += 8


# ═══════════════════════════════════════════════════════════════════════════
#  6. COMPARE TABLE — Popup modal với bar chart trực quan
# ═══════════════════════════════════════════════════════════════════════════

class CompareTable:
    """
    Modal popup hiển thị bảng so sánh trực quan 3 thuật toán.
    Có bar chart cho Path Length, Nodes Explored và Time.
    Nhấn bất kỳ đâu bên ngoài hoặc phím ESC để đóng.
    """

    def __init__(self, screen_w: int, screen_h: int, font_sm, font_md, font_lg):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.font_sm  = font_sm
        self.font_md  = font_md
        self.font_lg  = font_lg
        self.visible  = False
        self.results  = {}   # {algo: stats_dict}

        # Kích thước popup
        self.w = 620
        self.h = 480
        self.x = (screen_w - self.w) // 2
        self.y = (screen_h - self.h) // 2
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    # ------------------------------------------------------------------
    def show(self, results: dict):
        """Mở popup với dữ liệu kết quả."""
        self.results = results
        self.visible = len(results) > 0

    def hide(self):
        self.visible = False

    # ------------------------------------------------------------------
    def handle_event(self, event) -> bool:
        """Trả về True nếu popup bắt ký event (để block event cho game)."""
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide(); return True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.rect.collidepoint(event.pos):
                self.hide()   # click bên ngoài → đóng
            return True       # block click bên trong
        return self.visible   # nếu đang hiện thì chặn mọi event

    # ------------------------------------------------------------------
    def _draw_bar_section(self, surface, sx, sy, sw, label: str,
                          values: dict, fmt_fn, bar_color_key: str):
        """
        Vẽ một nhóm bar chart cho một metric.
        values = {algo: numeric_value}
        """
        # Tiêu đề metric
        hdr = self.font_md.render(label, True, C_TEXT_ACCENT)
        surface.blit(hdr, (sx, sy))
        sy += 22

        if not values:
            na = self.font_sm.render("(Chưa có dữ liệu)", True, C_TEXT_SECONDARY)
            surface.blit(na, (sx, sy))
            return sy + 18

        max_val = max(values.values()) or 1
        bar_h   = 20
        gap     = 10
        algos   = ["DFS", "BFS", "A*"]

        for algo in algos:
            if algo not in values:
                continue
            val      = values[algo]
            col      = ALGO_COLORS[algo][bar_color_key]
            bar_w    = int((val / max_val) * (sw - 120))

            # Label algo
            al = self.font_sm.render(f"{algo:<4}", True, col)
            surface.blit(al, (sx, sy + 2))

            # Bar
            bar_rect = pygame.Rect(sx + 38, sy, bar_w, bar_h)
            bar_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
            bar_surf.fill((*col, 180))
            surface.blit(bar_surf, bar_rect.topleft)
            # Viền bar
            pygame.draw.rect(surface, col, bar_rect, 1, border_radius=3)

            # Giá trị text
            val_txt = self.font_sm.render(fmt_fn(val), True, C_TEXT_PRIMARY)
            surface.blit(val_txt, (sx + 38 + bar_w + 6, sy + 2))

            sy += bar_h + gap

        return sy + 4

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface):
        """Vẽ toàn bộ popup modal."""
        if not self.visible:
            return

        # --- Overlay tối phía sau ---
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # --- Nền popup ---
        pop_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pop_surf.fill((*C_PANEL_BG, 250))
        surface.blit(pop_surf, (self.x, self.y))
        pygame.draw.rect(surface, C_TEXT_ACCENT, self.rect, 2, border_radius=12)

        # --- Tiêu đề ---
        px, py = self.x + 24, self.y + 18
        pw = self.w - 48

        title = self.font_lg.render("📊 Bảng So Sánh Thuật Toán", True, C_TEXT_ACCENT)
        surface.blit(title, (px, py))
        py += title.get_height() + 4

        hint = self.font_xs.render("Nhấn ESC hoặc click bên ngoài để đóng",
                                   True, C_TEXT_SECONDARY)
        surface.blit(hint, (px, py))
        py += hint.get_height() + 10

        pygame.draw.line(surface, C_PANEL_BORDER, (px, py), (px + pw, py))
        py += 12

        if not self.results:
            msg = self.font_md.render("Chưa có kết quả. Hãy chạy ít nhất 1 thuật toán!",
                                      True, C_TEXT_SECONDARY)
            surface.blit(msg, (px, py))
            return

        # --- Bảng số liệu ---
        col_widths = [70, 110, 130, 120]   # Algo | Path | Explored | Time
        headers    = ["Thuật toán", "Path length", "Nodes explored", "Time (ms)"]
        row_h      = 24
        algos      = ["DFS", "BFS", "A*"]

        # Header hàng
        cx = px
        for i, h in enumerate(headers):
            hs = self.font_sm.render(h, True, C_TEXT_SECONDARY)
            surface.blit(hs, (cx, py))
            cx += col_widths[i]
        py += row_h
        pygame.draw.line(surface, C_PANEL_BORDER, (px, py - 4), (px + pw, py - 4))

        # Data rows
        valid = {}
        for algo in algos:
            if algo not in self.results:
                continue
            s   = self.results[algo]
            col = ALGO_COLORS[algo]["path"]

            pygame.draw.rect(surface, (*col, 20),
                             (px - 4, py - 2, pw + 8, row_h - 2), border_radius=3)

            cx = px
            cells = [
                algo,
                f"{s['path_length']} bước" if s['path_length'] else "N/A",
                str(s['nodes_explored']),
                f"{s['time_ms']:.4f}",
            ]
            for i, cell in enumerate(cells):
                cs = self.font_sm.render(cell, True, col if i == 0 else C_TEXT_PRIMARY)
                surface.blit(cs, (cx, py))
                cx += col_widths[i]
            py += row_h

            if s['path_length'] > 0:
                valid[algo] = s

        # Winner row
        if valid:
            pygame.draw.line(surface, C_PANEL_BORDER, (px, py), (px + pw, py))
            py += 8
            winners = [
                ("⚡ Nhanh nhất",    min(valid, key=lambda a: valid[a]["time_ms"])),
                ("📏 Đường ngắn",    min(valid, key=lambda a: valid[a]["path_length"])),
                ("🧠 Ít node nhất",  min(valid, key=lambda a: valid[a]["nodes_explored"])),
            ]
            wx = px
            for label, winner in winners:
                wcol = ALGO_COLORS[winner]["path"]
                ls   = self.font_sm.render(f"{label}: ", True, C_TEXT_SECONDARY)
                ws   = self.font_sm.render(winner, True, wcol)
                surface.blit(ls, (wx, py))
                surface.blit(ws, (wx + ls.get_width(), py))
                wx += 200
            py += 24

        pygame.draw.line(surface, C_PANEL_BORDER, (px, py), (px + pw, py))
        py += 12

        # --- Bar charts ---
        half_w = pw // 2 - 10

        # Cột trái: Path Length
        path_vals = {a: s['path_length'] for a, s in self.results.items() if s['path_length'] > 0}
        py_left = self._draw_bar_section(
            surface, px, py, half_w,
            "📏 Path Length (bước)",
            path_vals, lambda v: str(v), "path"
        )

        # Cột phải: Nodes Explored
        node_vals = {a: s['nodes_explored'] for a, s in self.results.items()}
        self._draw_bar_section(
            surface, px + half_w + 20, py, half_w,
            "🔍 Nodes Explored",
            node_vals, lambda v: str(v), "visit"
        )

        py = max(py_left, py + 100) + 6

        # Time bar — full width
        if py < self.y + self.h - 60:
            time_vals = {a: s['time_ms'] for a, s in self.results.items()}
            self._draw_bar_section(
                surface, px, py, pw,
                "⏱ Time (ms)",
                time_vals, lambda v: f"{v:.4f}ms", "path"
            )


# ═══════════════════════════════════════════════════════════════════════════
#  7. BUTTON WIDGET
# ═══════════════════════════════════════════════════════════════════════════

class Button:
    """Nút bấm đơn giản với hiệu ứng hover."""

    def __init__(self, rect: pygame.Rect, label: str, color: tuple,
                 font: pygame.font.Font, icon: str = ""):
        self.rect   = rect
        self.label  = label
        self.color  = color
        self.font   = font
        self.icon   = icon
        self.hovered= False
        self.enabled= True

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface):
        alpha = 255 if self.enabled else 100
        base  = tuple(min(255, c + 30) for c in self.color) if self.hovered else self.color
        col   = (*base, alpha)

        # Nền nút
        btn_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, col, (0, 0, self.rect.w, self.rect.h),
                         border_radius=8)
        # Viền nội sáng hơn
        light = tuple(min(255, c + 60) for c in self.color)
        pygame.draw.rect(btn_surf, (*light, 180), (0, 0, self.rect.w, self.rect.h),
                         2, border_radius=8)
        surface.blit(btn_surf, self.rect.topleft)

        # Nhãn nút
        text = f"{self.icon} {self.label}".strip()
        lbl  = self.font.render(text, True, C_TEXT_PRIMARY)
        lx   = self.rect.centerx - lbl.get_width() // 2
        ly   = self.rect.centery - lbl.get_height() // 2
        surface.blit(lbl, (lx, ly))

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Trả về True nếu nút được click."""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos) and self.enabled
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.enabled:
                return True
        return False


# ═══════════════════════════════════════════════════════════════════════════
#  7. MAZE GAME — Main Application Class
# ═══════════════════════════════════════════════════════════════════════════

class MazeGame:
    """
    Lớp chính điều phối toàn bộ game:
      - Khởi tạo Pygame
      - Sinh mê cung
      - Xử lý sự kiện
      - Cập nhật animation
      - Vẽ màn hình
    """

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("🌀 Maze Pathfinding — DFS · BFS · A*")

        self.screen  = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock   = pygame.time.Clock()

        # Font chữ
        self.font_lg  = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_md  = pygame.font.SysFont("Segoe UI", 15, bold=True)
        self.font_sm  = pygame.font.SysFont("Segoe UI", 13)
        self.font_xs  = pygame.font.SysFont("Segoe UI", 11)

        # Maze state
        self.grid  = []
        self.start = (1, 1)
        self.goal  = (ROWS - 2, COLS - 2)

        # Animation & stats
        self.anim  = AnimationManager()
        # Lưu layer kết quả của từng thuật toán để vẽ chồng lên nhau
        self.layers: dict[str, dict] = {}   # {algo: result}
        # Guard để tránh in stats console nhiều lần
        self._stats_printed = False

        # Panel thống kê
        panel_x = MAZE_X_OFFSET + COLS * CELL_SIZE + 20
        panel_y = MAZE_Y_OFFSET
        panel_h = WINDOW_H - MAZE_Y_OFFSET - 20
        self.stats_panel = StatsPanel(
            panel_x, panel_y, PANEL_WIDTH - 10, panel_h,
            self.font_sm, self.font_md, self.font_lg
        )

        # Popup bảng so sánh
        self.compare_table = CompareTable(
            WINDOW_W, WINDOW_H,
            self.font_sm, self.font_md, self.font_lg
        )
        self.compare_table.font_xs = self.font_xs   # thêm font nhỏ

        # Tạo maze lần đầu
        self._new_maze()

        # Tạo các nút điều khiển
        self._create_buttons()

        # Status bar message
        self.status_msg = "Chọn thuật toán và nhấn nút để bắt đầu!"

    # ------------------------------------------------------------------
    def _new_maze(self):
        """Sinh maze mới và reset mọi trạng thái."""
        gen         = MazeGenerator(ROWS, COLS)
        self.grid   = gen.generate()
        self.anim.reset()
        self.layers = {}
        self._stats_printed = False
        self.stats_panel.clear()
        if hasattr(self, 'compare_table'):
            self.compare_table.hide()
        self.status_msg = "Maze mới! Chọn thuật toán để bắt đầu."

    # ------------------------------------------------------------------
    def _create_buttons(self):
        """Khởi tạo các nút bấm UI."""
        bx = MAZE_X_OFFSET                  # x bắt đầu hàng nút
        by = 20                             # y (thanh nút trên cùng)
        bw = 110                            # chiều rộng nút
        bh = 38                             # chiều cao nút
        gap = 8                             # khoảng cách giữa nút

        self.btn_dfs = Button(
            pygame.Rect(bx, by, bw, bh),
            "Run DFS", C_BTN_DFS, self.font_md, "🔵"
        )
        self.btn_bfs = Button(
            pygame.Rect(bx + (bw + gap), by, bw, bh),
            "Run BFS", C_BTN_BFS, self.font_md, "🔷"
        )
        self.btn_astar = Button(
            pygame.Rect(bx + (bw + gap) * 2, by, bw, bh),
            "Run A*", C_BTN_ASTAR, self.font_md, "⭐"
        )
        self.btn_compare = Button(
            pygame.Rect(bx + (bw + gap) * 3, by, bw + 20, bh),
            "Compare All", C_BTN_COMPARE, self.font_md, "📊"
        )
        self.btn_reset = Button(
            pygame.Rect(bx + (bw + gap) * 4 + 20, by, bw + 10, bh),
            "New Maze", C_BTN_RESET, self.font_md, "🔄"
        )
        # Nút mở popup bảng so sánh — đặt ở hàng nút, cuối cùng
        self.btn_table = Button(
            pygame.Rect(bx + (bw + gap) * 5 + 30, by, bw + 20, bh),
            "Show Table", (60, 160, 180), self.font_md, "📋"
        )

        self.buttons = [
            self.btn_dfs, self.btn_bfs, self.btn_astar,
            self.btn_compare, self.btn_reset, self.btn_table
        ]

    # ------------------------------------------------------------------
    def _run_algorithm(self, algo_name: str):
        """Chạy một thuật toán và bắt đầu animation."""
        if self.anim.state not in ('idle', 'done'):
            return   # đang chạy, bỏ qua

        finder_map = {
            "DFS": PathFinder.dfs,
            "BFS": PathFinder.bfs,
            "A*" : PathFinder.astar,
        }
        fn     = finder_map[algo_name]
        result = fn(self.grid, self.start, self.goal)

        # Lưu kết quả để vẽ (layer) và hiển thị stats
        self.layers[algo_name] = result
        self.stats_panel.add_result(algo_name, result)

        # Bắt đầu animation
        self.anim.start(algo_name, result)
        self._stats_printed = False   # reset để in stats lúc xong
        self.status_msg = f"🔍 {algo_name} đang tìm đường..."

    # ------------------------------------------------------------------
    def _run_compare(self):
        """Chạy cả 3 thuật toán, hiển thị ngay kết quả (không animation compare)."""
        if self.anim.state not in ('idle', 'done'):
            return

        self.layers = {}
        self.stats_panel.clear()

        for algo, fn in [("DFS", PathFinder.dfs),
                         ("BFS", PathFinder.bfs),
                         ("A*",  PathFinder.astar)]:
            result = fn(self.grid, self.start, self.goal)
            self.layers[algo] = result
            self.stats_panel.add_result(algo, result)

        # Hiển thị tất cả kết quả ngay lập tức (không cần animation step-by-step)
        self.anim.state = 'done'
        self.status_msg = "✅ So sánh hoàn tất! Nhấn [Show Table] để xem bảng."

        # In thống kê ra console (chỉ 1 lần)
        if not self._stats_printed:
            self._print_console_stats()
            self._stats_printed = True

    # ------------------------------------------------------------------
    def _print_console_stats(self):
        """In bảng thống kê và giải thích ra console."""
        print("\n" + "═" * 65)
        print("  MAZE PATHFINDING — KẾT QUẢ SO SÁNH")
        print("═" * 65)
        header = f"{'Thuật toán':<12} {'Path Length':>12} {'Nodes Explored':>16} {'Time (ms)':>12}"
        print(header)
        print("─" * 65)

        valid = {}
        for algo, stats in self.stats_panel.results.items():
            pl  = stats['path_length']
            ne  = stats['nodes_explored']
            tm  = stats['time_ms']
            tag = "" if pl > 0 else "(Không tìm được)"
            print(f"  {algo:<10} {str(pl) + tag:>14} {ne:>16} {tm:>12.4f}")
            if pl > 0:
                valid[algo] = stats

        if valid:
            print("─" * 65)
            fastest  = min(valid, key=lambda a: valid[a]["time_ms"])
            shortest = min(valid, key=lambda a: valid[a]["path_length"])
            print(f"  ⚡ Nhanh nhất   : {fastest}")
            print(f"  📏 Đường ngắn  : {shortest}")

        print("\n" + "─" * 65)
        print("  GIẢI THÍCH THUẬT TOÁN (dành cho người chưa biết)")
        print("─" * 65)
        explanations_full = {
            "DFS": """
  DFS (Depth First Search) – Tìm kiếm theo chiều sâu:
    Hình dung như một người đi trong mê cung tối với ngọn nến.
    Họ luôn chọn đi thẳng, chỉ quay lại khi đâm vào tường.
    Kết quả: tìm đường rất nhanh nhưng đường đi thường KHÔNG ngắn nhất.
    Dùng cấu trúc STACK (chồng đĩa – vào sau ra trước).
""",
            "BFS": """
  BFS (Breadth First Search) – Tìm kiếm theo chiều rộng:
    Hình dung như sóng lan ra từ điểm xuất phát.
    Mỗi 'vòng sóng' = tất cả ô cách start đúng N bước.
    Kết quả: LUÔN tìm đường ngắn nhất (ít bước nhất).
    Tốn RAM vì phải lưu cả 'vòng sóng' hiện tại.
    Dùng cấu trúc QUEUE (hàng đợi – vào trước ra trước).
""",
            "A*": """
  A* (A-Star) – Tìm kiếm thông minh:
    Kết hợp ưu điểm của BFS (đảm bảo tối ưu) và thêm 'trực giác'.
    Công thức: f(n) = g(n) + h(n)
      • g(n): số bước đã đi từ start đến node n
      • h(n): ước lượng số bước từ n đến goal (Manhattan distance)
    A* ưu tiên các node 'có vẻ gần goal hơn', nhờ đó:
      → Khám phá ít node hơn BFS
      → Vẫn đảm bảo tìm đường ngắn nhất
    Đây là thuật toán được dùng trong Google Maps, game, robotics...
""",
        }
        for algo, exp in explanations_full.items():
            if algo in self.stats_panel.results:
                print(exp)
        print("═" * 65 + "\n")

    # ══════════════════════════════════════════════════════════════════
    #  VẼ MAZE
    # ══════════════════════════════════════════════════════════════════

    def _draw_maze(self):
        """Vẽ lưới maze (tường + đường đi) lên màn hình."""
        for r in range(ROWS):
            for c in range(COLS):
                rx = MAZE_X_OFFSET + c * CELL_SIZE
                ry = MAZE_Y_OFFSET + r * CELL_SIZE
                rect = pygame.Rect(rx, ry, CELL_SIZE, CELL_SIZE)

                if self.grid[r][c] == 0:
                    # Tường: màu tối + gradient nhẹ
                    pygame.draw.rect(self.screen, C_WALL, rect)
                else:
                    # Đường đi
                    pygame.draw.rect(self.screen, C_PASSAGE, rect)

                # Lưới mờ
                pygame.draw.rect(self.screen, C_GRID_LINE, rect, 1)

    # ------------------------------------------------------------------
    def _draw_layers(self):
        """
        Vẽ các lớp animation:
        1. Tất cả các kết quả đã lưu (layers) – vẽ visited + path
        2. Animation hiện tại (anim) – vẽ theo tiến độ
        """
        # Vẽ các layer đã hoàn thành (không phải layer đang chạy)
        for algo, result in self.layers.items():
            if algo == self.anim.algo_name and self.anim.state != 'done':
                continue   # skip layer đang animation (sẽ vẽ bên dưới)
            visit_col = ALGO_COLORS[algo]["visit"]
            path_col  = ALGO_COLORS[algo]["path"]

            for node in result["visited_order"]:
                self._draw_cell(*node, (*visit_col, 120), border=False)
            for node in result["path"]:
                self._draw_cell(*node, (*path_col, 200), border=False)

        # Vẽ animation đang chạy
        if self.anim.algo_name and self.anim.state != 'idle':
            algo      = self.anim.algo_name
            visit_col = ALGO_COLORS[algo]["visit"]
            path_col  = ALGO_COLORS[algo]["path"]

            for node in self.anim.shown_visited:
                self._draw_cell(*node, (*visit_col, 140), border=False)

            # Highlight node đang duyệt (nhấp nháy)
            if self.anim.state == 'visiting' and \
                    self.anim.vis_index < len(self.anim.visited_order):
                cur = self.anim.visited_order[self.anim.vis_index - 1] \
                      if self.anim.vis_index > 0 else None
                if cur:
                    self._draw_cell(*cur, (255, 255, 255, 200), border=False)

            for node in self.anim.shown_path:
                self._draw_cell(*node, (*path_col, 230), border=False)

    # ------------------------------------------------------------------
    def _draw_cell(self, r: int, c: int, color: tuple, border: bool = True):
        """Vẽ một ô với màu tùy chỉnh (hỗ trợ alpha)."""
        rx = MAZE_X_OFFSET + c * CELL_SIZE + 2
        ry = MAZE_Y_OFFSET + r * CELL_SIZE + 2
        w  = CELL_SIZE - 4
        h  = CELL_SIZE - 4

        cell_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cell_surf.fill(color)
        self.screen.blit(cell_surf, (rx, ry))

    # ------------------------------------------------------------------
    def _draw_start_goal(self):
        """Vẽ ô Start và Goal với biểu tượng rõ ràng."""
        sr, sc = self.start
        gr, gc = self.goal

        # Start – xanh lá
        self._draw_cell(sr, sc, (*C_START, 255))
        s_lbl = self.font_xs.render("S", True, (0, 0, 0))
        self.screen.blit(s_lbl,
            (MAZE_X_OFFSET + sc * CELL_SIZE + 8,
             MAZE_Y_OFFSET + sr * CELL_SIZE + 7))

        # Goal – đỏ
        self._draw_cell(gr, gc, (*C_GOAL, 255))
        g_lbl = self.font_xs.render("G", True, (255, 255, 255))
        self.screen.blit(g_lbl,
            (MAZE_X_OFFSET + gc * CELL_SIZE + 8,
             MAZE_Y_OFFSET + gr * CELL_SIZE + 7))

    # ------------------------------------------------------------------
    def _draw_status_bar(self):
        """Vẽ thanh trạng thái dưới cùng."""
        bar_y = ROWS * CELL_SIZE + MAZE_Y_OFFSET + 4
        bar_r = pygame.Rect(MAZE_X_OFFSET, bar_y,
                            COLS * CELL_SIZE, 22)
        bar_s = pygame.Surface((bar_r.w, bar_r.h), pygame.SRCALPHA)
        bar_s.fill((*C_PANEL_BG, 200))
        self.screen.blit(bar_s, bar_r.topleft)

        msg  = self.font_sm.render(self.status_msg, True, C_TEXT_ACCENT)
        self.screen.blit(msg, (bar_r.x + 8, bar_r.y + 3))

    # ------------------------------------------------------------------
    def _draw_legend(self):
        """Vẽ chú thích màu sắc phía trên maze."""
        items = [
            ("Start",      C_START),
            ("Goal",       C_GOAL),
            ("DFS path",   C_DFS_PATH),
            ("BFS path",   C_BFS_PATH),
            ("A* path",    C_ASTAR_PATH),
        ]
        lx = MAZE_X_OFFSET
        ly = MAZE_Y_OFFSET - 22
        for label, col in items:
            pygame.draw.rect(self.screen, col, (lx, ly + 2, 12, 12), border_radius=2)
            txt = self.font_xs.render(label, True, C_TEXT_SECONDARY)
            self.screen.blit(txt, (lx + 16, ly))
            lx += txt.get_width() + 30

    # ══════════════════════════════════════════════════════════════════
    #  MAIN LOOP
    # ══════════════════════════════════════════════════════════════════

    def run(self):
        """Vòng lặp chính của game."""
        while True:
            # --- Xử lý sự kiện ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self._new_maze()
                    elif event.key == pygame.K_1:
                        self._run_algorithm("DFS")
                    elif event.key == pygame.K_2:
                        self._run_algorithm("BFS")
                    elif event.key == pygame.K_3:
                        self._run_algorithm("A*")
                    elif event.key == pygame.K_c:
                        self._run_compare()

                # Popup bắt event trước — nếu popup đang mở thì block
                if self.compare_table.handle_event(event):
                    continue

                # Xử lý sự kiện nút bấm
                if self.btn_dfs.handle_event(event):
                    self._run_algorithm("DFS")
                if self.btn_bfs.handle_event(event):
                    self._run_algorithm("BFS")
                if self.btn_astar.handle_event(event):
                    self._run_algorithm("A*")
                if self.btn_compare.handle_event(event):
                    self._run_compare()
                if self.btn_reset.handle_event(event):
                    self._new_maze()
                if self.btn_table.handle_event(event):
                    self.compare_table.show(self.stats_panel.results)

                # Kéo thả KHÔNG hỗ trợ (maze có thể click cell tùy chỉnh tương lai)

            # --- Cập nhật animation ---
            self.anim.update()
            if self.anim.is_done() and self.status_msg.startswith("🔍"):
                algo = self.anim.algo_name
                pl   = self.anim.stats["path_length"]
                ne   = self.anim.stats["nodes_explored"]
                tm   = self.anim.stats["time_ms"]
                if pl > 0:
                    self.status_msg = (
                        f"✅ {algo} xong! Path={pl} | "
                        f"Nodes={ne} | {tm:.3f}ms  |  [Show Table] để so sánh"
                    )
                else:
                    self.status_msg = f"❌ {algo}: Không tìm được đường đi!"
                # In stats console chỉ 1 lần
                if not self._stats_printed:
                    self._print_console_stats()
                    self._stats_printed = True

            # --- Vẽ ---
            self.screen.fill(C_BG)

            self._draw_maze()
            self._draw_layers()
            self._draw_start_goal()

            self._draw_legend()
            self._draw_status_bar()
            self.stats_panel.draw(self.screen)

            # Vẽ nút bấm
            for btn in self.buttons:
                btn.draw(self.screen)

            # Ghi chú phím tắt — vẽ ngay dưới status bar, không bị chồng
            hint_y = ROWS * CELL_SIZE + MAZE_Y_OFFSET + 4 + 26
            hint = self.font_xs.render(
                "[1] DFS  [2] BFS  [3] A*  [C] Compare All  [R] New Maze  [ESC] Đóng bảng",
                True, C_TEXT_SECONDARY
            )
            self.screen.blit(hint, (MAZE_X_OFFSET, hint_y))

            # Vẽ popup bảng so sánh (luôn ở trên cùng)
            self.compare_table.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)          # giới hạn 60 FPS


# ═══════════════════════════════════════════════════════════════════════════
#  8. ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """
    Điểm khởi đầu chương trình.
    Yêu cầu: pip install pygame
    """
    try:
        import pygame as _pg
    except ImportError:
        print("❌ Pygame chưa được cài đặt!")
        print("   Chạy lệnh: pip install pygame")
        sys.exit(1)

    game = MazeGame()
    game.run()


if __name__ == "__main__":
    main()
