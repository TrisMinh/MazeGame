# 🌀 Hướng Dẫn Xây Dựng Maze Pathfinding Game Từ Đầu

> **Dành cho người mới hoàn toàn** — không cần biết thuật toán, không cần biết Pygame  
> Sau khi đọc xong, bạn sẽ tự viết được game này từ tờ giấy trắng

---

## 📚 Mục Lục

1. [Hiểu bức tranh tổng thể](#1-hiểu-bức-tranh-tổng-thể)
2. [Cài đặt môi trường](#2-cài-đặt-môi-trường)
3. [Python cơ bản cần biết](#3-python-cơ-bản-cần-biết)
4. [Grid 2D — Nền tảng của Maze](#4-grid-2d--nền-tảng-của-maze)
5. [Thuật toán tạo Maze](#5-thuật-toán-tạo-maze)
6. [Pygame cơ bản — Vẽ lên màn hình](#6-pygame-cơ-bản--vẽ-lên-màn-hình)
7. [Thuật toán tìm đường — DFS](#7-thuật-toán-tìm-đường--dfs)
8. [Thuật toán tìm đường — BFS](#8-thuật-toán-tìm-đường--bfs)
9. [Thuật toán tìm đường — A*](#9-thuật-toán-tìm-đường--a)
10. [Animation — Hiển thị từng bước](#10-animation--hiển-thị-từng-bước)
11. [UI — Nút bấm, Panel, Popup](#11-ui--nút-bấm-panel-popup)
12. [Ghép tất cả lại](#12-ghép-tất-cả-lại)
13. [So sánh 3 thuật toán](#13-so-sánh-3-thuật-toán)
14. [Câu hỏi thường gặp](#14-câu-hỏi-thường-gặp)

---

## 1. Hiểu Bức Tranh Tổng Thể

Trước khi code, hãy hiểu game sẽ làm **GÌ**:

```
┌─────────────────────────────────────────────────┐
│  🟢 S ─────── 🔲 🔲 🔲                          │
│  🔲       🔲       🔲                            │
│  🔲 🔲 🔲 🔲   🔲 🔲 🔲                          │
│          🔲           🔲                         │
│  🔲 🔲 🔲 🔲 🔲 🔲 🔲 🔲                          │
│                              🔴 G               │
└─────────────────────────────────────────────────┘
  S = Start (bắt đầu)    G = Goal (đích)
  🔲 = Tường             (trắng) = Đường đi
```

**Game làm 3 việc:**
1. **Tạo mê cung** ngẫu nhiên (Maze Generation)
2. **AI tìm đường** từ S → G (Pathfinding)  
3. **Hiển thị** quá trình tìm đường với animation (Visualization)

**Cấu trúc code chia thành 6 lớp (class):**

```
MazeGenerator  →  tạo maze
PathFinder     →  DFS / BFS / A*
AnimationManager → điều khiển animation frame-by-frame
StatsPanel     →  hiển thị kết quả bên phải
Button         →  nút bấm UI
MazeGame       →  vòng lặp chính, kết hợp tất cả
```

---

## 2. Cài Đặt Môi Trường

### Bước 1 — Cài Python
Tải Python tại [python.org](https://python.org), chọn phiên bản 3.10+

### Bước 2 — Tạo thư mục project
```
C:\Users\bạn\Desktop\MazeGame\
```

### Bước 3 — Tạo virtual environment (môi trường ảo)
```bash
# Mở terminal trong thư mục MazeGame
python -m venv .venv

# Kích hoạt (Windows)
.venv\Scripts\activate

# Cài Pygame
pip install pygame-ce
```

> **Virtual environment là gì?**  
> Giống như một "phòng sạch" riêng cho project của bạn.  
> Các thư viện cài vào đây không ảnh hưởng project khác.

### Bước 4 — Tạo file
Tạo file `maze_game.py` trong thư mục MazeGame

### Bước 5 — Chạy thử
```bash
python maze_game.py
```

---

## 3. Python Cơ Bản Cần Biết

Trước khi làm game, bạn cần nắm vững 5 khái niệm Python:

### 3.1 List và List 2D

```python
# List bình thường (1 chiều)
row = [0, 1, 0, 1, 0]
print(row[2])   # → 0

# List 2D (giống bảng)
grid = [
    [0, 1, 0],   # hàng 0
    [1, 1, 1],   # hàng 1
    [0, 1, 0],   # hàng 2
]
print(grid[1][2])   # → 1 (hàng 1, cột 2)
```

> **Đây là nền tảng của maze!** Mỗi ô trong maze = 1 phần tử trong list 2D

### 3.2 Vòng lặp

```python
# Duyệt qua grid 2D
for r in range(3):        # r = hàng
    for c in range(3):    # c = cột
        print(f"grid[{r}][{c}] = {grid[r][c]}")
```

### 3.3 Dictionary (từ điển)

```python
# Lưu thông tin theo key
stats = {
    "DFS": {"path": 50, "nodes": 120},
    "BFS": {"path": 45, "nodes": 200},
}
print(stats["DFS"]["path"])   # → 50
```

### 3.4 Class (lớp đối tượng)

```python
class Dog:
    def __init__(self, name):    # hàm khởi tạo
        self.name = name         # thuộc tính

    def bark(self):              # phương thức
        print(f"{self.name}: Gâu!")

rex = Dog("Rex")
rex.bark()   # → Rex: Gâu!
```

### 3.5 Set (tập hợp)

```python
visited = set()           # tập rỗng
visited.add((1, 1))       # thêm tọa độ
visited.add((1, 3))
print((1, 1) in visited)  # → True — kiểm tra O(1), rất nhanh!
```

> **Set rất quan trọng trong thuật toán** vì kiểm tra "đã thăm chưa" chỉ tốn O(1) thời gian.

---

## 4. Grid 2D — Nền Tảng Của Maze

### Biểu diễn maze bằng số

```python
# 0 = tường (wall)
# 1 = đường đi (passage)

maze = [
    [0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 1, 0, 1, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0],
]
```

Nhìn trực quan:
```
# # # # #
# . . . #
# . # . #
# . . . #
# # # # #
```

### Tọa độ (row, col)

```python
# Quy ước: (row, col) = (hàng, cột)
# (0,0) là góc trên trái
# Chú ý: KHÔNG phải (x, y) như toán học - hàng là chiều dọc!

start = (1, 1)   # hàng 1, cột 1
goal  = (3, 3)   # hàng 3, cột 3
```

### Tìm hàng xóm hợp lệ

```python
def get_neighbors(grid, r, c):
    """Trả về các ô kề (lên/xuống/trái/phải) là đường đi."""
    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    # ↑ lên      ↓ xuống   ← trái   → phải

    rows = len(grid)
    cols = len(grid[0])
    result = []

    for dr, dc in DIRECTIONS:
        nr = r + dr   # hàng mới
        nc = c + dc   # cột mới

        # Kiểm tra:
        # 1. Có nằm trong lưới không?
        # 2. Có phải đường đi không?
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
            result.append((nr, nc))

    return result
```

---

## 5. Thuật Toán Tạo Maze

### Tại sao cần thuật toán?

Nếu tạo maze ngẫu nhiên hoàn toàn, sẽ có ô bị cô lập — không thể đến được. Ta cần thuật toán đảm bảo **mọi ô đều kết nối với nhau**.

### Recursive Backtracker (Đệ quy quay lui)

**Ý tưởng** — Giống người đi trong mê cung tối với sợi chỉ Ariadne:

```
1. Đứng ở ô (1,1), đánh dấu đã thăm
2. Nhìn 4 hướng, chọn ngẫu nhiên 1 hàng xóm CHƯA thăm (cách 2 ô)
3. Dỡ tường giữa ta và hàng xóm → tạo đường đi
4. Bước sang hàng xóm, lặp lại từ bước 2
5. Nếu không còn hàng xóm nào chưa thăm → quay lui
6. Lặp đến khi quay về ô đầu tiên
```

**Tại sao nhảy 2 ô?**

```
Cấu trúc grid với khoảng cách 2:

index:  0  1  2  3  4  5  6
        #  .  #  .  #  .  #   ← chỉ số lẻ (1,3,5) = ô đường đi
        #  #  #  #  #  #  #   ← chỉ số chẵn (0,2,4,6) = tường/viền

Ô đường đi A=(1,1), B=(1,3):
Tường giữa A và B là (1,2)
Nhảy 2 ô, khoét tường ở giữa → tạo lối đi A—B
```

**Code thực tế (iterative — dùng stack, không đệ quy):**

```python
import random

class MazeGenerator:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        # Ban đầu toàn bộ là tường
        self.grid = [[0] * cols for _ in range(rows)]

    def generate(self):
        self._carve_iterative(1, 1)
        return self.grid

    def _carve_iterative(self, start_r, start_c):
        DIRS = [(0, 2), (0, -2), (2, 0), (-2, 0)]  # 4 hướng, nhảy 2

        self.grid[start_r][start_c] = 1  # mở ô đầu tiên
        stack = [(start_r, start_c)]

        while stack:
            r, c = stack[-1]  # nhìn đỉnh stack (KHÔNG lấy ra)

            # Tìm hàng xóm chưa thăm (cách 2 ô)
            neighbors = []
            for dr, dc in DIRS:
                nr, nc = r + dr, c + dc
                if (1 <= nr < self.rows - 1 and
                        1 <= nc < self.cols - 1 and
                        self.grid[nr][nc] == 0):  # chưa thăm
                    neighbors.append((dr, dc, nr, nc))

            if neighbors:
                # Chọn ngẫu nhiên 1 hàng xóm
                dr, dc, nr, nc = random.choice(neighbors)
                # Khoét tường giữa
                self.grid[r + dr//2][c + dc//2] = 1
                # Mở ô hàng xóm
                self.grid[nr][nc] = 1
                # Thêm vào stack để tiếp tục từ đây
                stack.append((nr, nc))
            else:
                # Không còn hàng xóm nào → quay lui
                stack.pop()
```

> **Tại sao dùng iterative thay vì đệ quy?**  
> Python có giới hạn đệ quy ~1000 lần. Maze 101×101 cần ~2500 bước → **lỗi RecursionError**.  
> Iterative dùng stack của ta → không giới hạn.

---

## 6. Pygame Cơ Bản — Vẽ Lên Màn Hình

### Pygame là gì?

Pygame là thư viện giúp Python vẽ đồ họa, xử lý bàn phím/chuột, tạo game 2D.

### Vòng lặp game (Game Loop)

Đây là khái niệm quan trọng nhất:

```python
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock  = pygame.time.Clock()

# === VÒNG LẶP GAME ===
while True:
    # 1. XỬ LÝ SỰ KIỆN (bàn phím, chuột, đóng cửa sổ)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 2. CẬP NHẬT TRẠNG THÁI (di chuyển, animation...)
    # ... logic game ...

    # 3. VẼ LÊN MÀN HÌNH
    screen.fill((15, 17, 26))    # xóa màn hình (nền tối)
    # ... vẽ các thứ ...
    pygame.display.flip()         # hiển thị frame mới

    clock.tick(60)               # giới hạn 60 FPS
```

> **Game loop chạy 60 lần/giây** — mỗi lần = 1 frame  
> Mỗi frame: xử lý input → cập nhật → vẽ → lặp lại

### Vẽ hình chữ nhật

```python
# pygame.draw.rect(surface, color, rect)
pygame.draw.rect(screen, (200, 100, 255), (x, y, width, height))

# Vẽ có bo góc
pygame.draw.rect(screen, color, rect, border_radius=8)

# Vẽ chỉ viền (không tô)
pygame.draw.rect(screen, color, rect, 2)   # 2 = độ dày viền
```

### Vẽ với alpha (độ trong suốt)

```python
# Surface có alpha
surf = pygame.Surface((width, height), pygame.SRCALPHA)
surf.fill((200, 100, 255, 150))   # màu RGBA, 150/255 = ~60% opaque
screen.blit(surf, (x, y))
```

### Vẽ chữ

```python
font = pygame.font.SysFont("Segoe UI", 16)
text_surf = font.render("Hello World", True, (255, 255, 255))
screen.blit(text_surf, (100, 50))
```

### Vẽ maze lên màn hình

```python
CELL_SIZE   = 28      # pixel mỗi ô
MAZE_X      = 20      # khoảng trống bên trái
MAZE_Y      = 80      # khoảng trống phía trên

def draw_maze(screen, grid):
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            # Tính tọa độ pixel từ tọa độ grid
            px = MAZE_X + c * CELL_SIZE
            py = MAZE_Y + r * CELL_SIZE
            rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)

            if grid[r][c] == 0:
                color = (30, 35, 55)      # tường — tối
            else:
                color = (240, 242, 255)   # đường đi — sáng

            pygame.draw.rect(screen, color, rect)
```

---

## 7. Thuật Toán Tìm Đường — DFS

### DFS là gì? (Depth First Search — Tìm kiếm theo chiều sâu)

**Hình dung:** Bạn đi trong mê cung tối với 1 ngọn nến.  
Bạn luôn **đi thẳng nhất có thể**, chỉ quay lui khi **đâm vào tường hoặc ngõ cụt**.

```
Maze:
S → → → #
        ↓
# # # # .
↓
. ← ← ← .   ← DFS đi vào đây trước (sâu)
↓
. → → → G

DFS có thể đi một đường rất dài, vòng vèo
trước khi tìm được G
```

### Cấu trúc dữ liệu: Stack (ngăn xếp)

```
Stack = chồng đĩa
Thêm vào trên cùng (push)
Lấy ra từ trên cùng (pop) — LIFO: Last In, First Out

[A] push B → [A, B] pop → lấy B, còn [A]
```

### Code DFS

```python
def dfs(grid, start, goal):
    """
    DFS tìm đường từ start đến goal.
    Trả về dict chứa thông tin.
    """
    stack     = [start]          # Stack ban đầu chứa ô start
    came_from = {start: None}    # {ô: ô_cha} để truy vết đường đi
    visited   = set()            # Tập ô đã thăm
    visited_order = []           # Thứ tự thăm (cho animation)

    while stack:
        current = stack.pop()    # Lấy ô trên cùng stack

        if current in visited:   # Nếu đã thăm → bỏ qua
            continue

        visited.add(current)
        visited_order.append(current)   # Ghi nhớ thứ tự

        if current == goal:      # Tìm thấy đích!
            break

        # Thêm tất cả hàng xóm chưa thăm vào stack
        for neighbor in get_neighbors(grid, *current):
            if neighbor not in visited:
                stack.append(neighbor)
                if neighbor not in came_from:
                    came_from[neighbor] = current

    # Truy ngược từ goal → start để lấy đường đi
    path = reconstruct_path(came_from, start, goal)
    return {
        "visited_order": visited_order,
        "path": path,
        "nodes_explored": len(visited_order),
        "path_length": len(path),
    }
```

### Hàm `reconstruct_path` — Truy vết đường đi

```python
def reconstruct_path(came_from, start, goal):
    """
    came_from = {(3,3): (2,3), (2,3): (1,3), (1,3): (1,1), (1,1): None}
    Truy ngược từ goal về start:
    goal → (3,3) → (2,3) → (1,3) → start
    Đảo ngược → start → (1,3) → (2,3) → goal
    """
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from.get(node)
    path.reverse()

    # Kiểm tra có tìm được không
    if path and path[0] == start:
        return path
    return []   # Không tìm được đường
```

### Đặc điểm DFS:

| | |
|---|---|
| Cấu trúc | Stack (LIFO) |
| Đường đi | KHÔNG đảm bảo ngắn nhất |
| Tốc độ | Nhanh hơn BFS trên maze có 1 đường |
| RAM | Ít hơn BFS |

---

## 8. Thuật Toán Tìm Đường — BFS

### BFS là gì? (Breadth First Search — Tìm kiếm theo chiều rộng)

**Hình dung:** Thả đá xuống hồ nước — sóng lan **đồng đều ra mọi hướng**.  
BFS khám phá **tất cả ô cùng khoảng cách** trước khi đi xa hơn.

```
Bước 1 — Từ S, khám phá tất cả ô cách 1 bước:
S [A B C D]

Bước 2 — Từ A,B,C,D, khám phá tất cả ô cách 2 bước:
S A [E F G] B [H I] C D [J K]

→ Ô nào tìm được TRƯỚC là ĐỢT SỚM NHẤT → đường NGẮN NHẤT
```

### Cấu trúc dữ liệu: Queue (hàng đợi)

```
Queue = hàng người chờ
Thêm vào cuối (enqueue)
Lấy ra từ đầu (dequeue) — FIFO: First In, First Out

[A, B] enqueue C → [A, B, C] dequeue → lấy A, còn [B, C]
```

### Code BFS

```python
from collections import deque   # Queue hiệu quả

def bfs(grid, start, goal):
    queue     = deque([start])   # Queue ban đầu chứa ô start
    came_from = {start: None}    # {ô: ô_cha}
    visited_order = []

    while queue:
        current = queue.popleft()    # Lấy ô đầu tiên trong queue (FIFO)
        visited_order.append(current)

        if current == goal:
            break

        for neighbor in get_neighbors(grid, *current):
            if neighbor not in came_from:   # Chưa thăm
                came_from[neighbor] = current
                queue.append(neighbor)      # Thêm vào cuối queue

    path = reconstruct_path(came_from, start, goal)
    return {
        "visited_order": visited_order,
        "path": path,
        "nodes_explored": len(visited_order),
        "path_length": len(path),
    }
```

> **Tại sao BFS tìm đường ngắn nhất?**  
> Vì BFS khám phá theo từng "lớp" (layer) khoảng cách.  
> Khi tìm thấy goal, đó là lần đầu tiên goal được chạm đến  
> → đây chắc chắn là con đường ngắn nhất (ít bước nhất).

### So sánh DFS vs BFS trực quan:

```
Maze đơn giản:
S . . . . . . . G

DFS (có thể đi lòng vòng):
S→↓←←←←←←←
  ↓→→→→→→→↓
            ↓→G  (đường dài!)

BFS (lan đều):
S → . → . → . → G  (đường ngắn nhất!)
```

---

## 9. Thuật Toán Tìm Đường — A*

### A* là gì? (A-Star)

**Hình dung:** BFS thông minh hơn — biết "nhìn về phía goal" để ưu tiên.

A* dùng công thức:
```
f(n) = g(n) + h(n)
```

| | |
|---|---|
| `g(n)` | Số bước đã đi thực tế từ Start đến ô n |
| `h(n)` | Ước lượng số bước từ n đến Goal (Heuristic) |
| `f(n)` | "Điểm ưu tiên" — **f nhỏ = được khám phá trước** |

### Heuristic — "Trực giác của AI"

```python
def heuristic(a, b):
    """
    Khoảng cách Manhattan — phù hợp mê cung lưới 4 hướng.
    Không dùng đường chéo.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# ví dụ:
heuristic((1, 1), (5, 4))
# = |1-5| + |1-4| = 4 + 3 = 7
```

> **Tại sao Manhattan?**  
> Trong maze chỉ đi 4 hướng (không đường chéo),  
> khoảng cách thực tế ít nhất = |Δrow| + |Δcol|  
> Đây là ước lượng **lạc quan nhất** (không bao giờ ước lượng quá cao)

### Code A*

```python
import heapq   # Min-heap (priority queue)

def astar(grid, start, goal):
    # Heap: (f_score, tie_breaker, node)
    # heapq.heappop() luôn lấy phần tử f_score NHỎ NHẤT
    open_heap = [(heuristic(start, goal), 0, start)]
    came_from = {start: None}
    g_score   = {start: 0}   # chi phí thực tế từ start
    counter   = 1             # tie-breaker nếu f bằng nhau
    closed    = set()
    visited_order = []

    while open_heap:
        f, _, current = heapq.heappop(open_heap)   # Lấy ô f nhỏ nhất

        if current in closed:
            continue
        closed.add(current)
        visited_order.append(current)

        if current == goal:
            break

        for neighbor in get_neighbors(grid, *current):
            if neighbor in closed:
                continue

            # Chi phí đi qua current đến neighbor
            tentative_g = g_score[current] + 1   # mỗi bước = 1

            # Nếu tìm được đường tốt hơn đến neighbor
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor]   = tentative_g
                f_new = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_heap, (f_new, counter, neighbor))
                counter += 1

    path = reconstruct_path(came_from, start, goal)
    return {"visited_order": visited_order, "path": path, ...}
```

### Ví dụ A* hoạt động:

```
Start=(0,0)  Goal=(0,4)

Bước 1: Open = [(4, start)]   ← f=4 (g=0 + h=4)
        Khám phá start

Bước 2: Hàng xóm của start: (0,1) và (1,0)
        (0,1): g=1, h=3, f=4 → thêm vào heap
        (1,0): g=1, h=5, f=6 → thêm vào heap

Bước 3: Open = [(4,(0,1)), (6,(1,0))]
        Khám phá (0,1) vì f nhỏ hơn

        → A* đi thẳng về phía goal, không lang thang!
```

---

## 10. Animation — Hiển Thị Từng Bước

### Ý tưởng cơ bản

Thuật toán chạy xong **trong tích tắc** — nhưng ta muốn xem **từng bước**.  
Giải pháp: lưu **thứ tự duyệt** (`visited_order`), rồi **phát lại** từng bước theo thời gian.

### State Machine (Máy trạng thái)

```
idle → (nhấn nút) → visiting → (hết visited) → pathing → (hết path) → done
  ↑_______________________________________________|
                    (nhấn nút mới)
```

### Code AnimationManager

```python
class AnimationManager:
    def __init__(self):
        self.state = 'idle'
        self.visited_order = []
        self.path = []
        self.vis_index  = 0
        self.path_index = 0
        self.shown_visited = set()
        self.shown_path    = set()
        self.delay_ms = 18       # ms giữa mỗi bước
        self.last_tick = 0

    def start(self, algo_name, result):
        """Bắt đầu animation."""
        self.state = 'visiting'
        self.visited_order = result["visited_order"]
        self.path = result["path"]
        self.vis_index = self.path_index = 0
        self.shown_visited = set()
        self.shown_path = set()
        self.last_tick = pygame.time.get_ticks()

    def update(self):
        """Gọi mỗi frame — cập nhật 1 bước animation."""
        now = pygame.time.get_ticks()
        if now - self.last_tick < self.delay_ms:
            return    # Chưa đến lúc next step

        self.last_tick = now

        if self.state == 'visiting':
            if self.vis_index < len(self.visited_order):
                # Hiện thêm 1 ô đã duyệt
                self.shown_visited.add(self.visited_order[self.vis_index])
                self.vis_index += 1
            else:
                self.state = 'pathing'  # Chuyển sang vẽ đường đi

        elif self.state == 'pathing':
            if self.path_index < len(self.path):
                # Hiện thêm 1 ô đường đi
                self.shown_path.add(self.path[self.path_index])
                self.path_index += 1
            else:
                self.state = 'done'
```

### Cách vẽ animation

```python
def draw_animation(screen, anim, algo_name):
    VISIT_COLOR = (160, 80, 230, 120)  # màu mờ = đã duyệt
    PATH_COLOR  = (200, 100, 255, 230) # màu đậm = đường đi

    # Vẽ tất cả ô đã duyệt (màu mờ)
    for node in anim.shown_visited:
        draw_cell_alpha(screen, *node, VISIT_COLOR)

    # Vẽ đường đi cuối cùng (màu đậm)
    for node in anim.shown_path:
        draw_cell_alpha(screen, *node, PATH_COLOR)
```

---

## 11. UI — Nút Bấm, Panel, Popup

### Button Widget cơ bản

```python
class Button:
    def __init__(self, rect, label, color, font):
        self.rect    = rect     # pygame.Rect(x, y, w, h)
        self.label   = label    # "Run DFS"
        self.color   = color    # (R, G, B)
        self.font    = font
        self.hovered = False    # chuột đang ở trên không?

    def draw(self, screen):
        # Đổi màu khi hover
        col = tuple(min(255, c+30) for c in self.color) if self.hovered else self.color

        pygame.draw.rect(screen, col, self.rect, border_radius=8)

        # Vẽ chữ
        lbl = self.font.render(self.label, True, (255, 255, 255))
        x = self.rect.centerx - lbl.get_width() // 2
        y = self.rect.centery - lbl.get_height() // 2
        screen.blit(lbl, (x, y))

    def handle_event(self, event):
        """Trả về True nếu được click."""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
```

### Popup Modal

```python
def draw_popup(screen, results):
    """Vẽ cửa sổ popup phủ lên màn hình."""
    # 1. Overlay mờ phía sau
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))    # đen 60% trong suốt
    screen.blit(overlay, (0, 0))

    # 2. Nền popup
    popup_rect = pygame.Rect(100, 100, 600, 400)
    pygame.draw.rect(screen, (22, 25, 40), popup_rect, border_radius=12)
    pygame.draw.rect(screen, (100, 200, 255), popup_rect, 2, border_radius=12)

    # 3. Nội dung
    # ... vẽ bảng, bar chart ...
```

---

## 12. Ghép Tất Cả Lại

### Cấu trúc MazeGame chính

```python
class MazeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock  = pygame.time.Clock()

        # 1. Tạo maze
        gen = MazeGenerator(ROWS, COLS)
        self.grid = gen.generate()

        # 2. Khởi tạo các thành phần
        self.anim         = AnimationManager()
        self.stats_panel  = StatsPanel(...)
        self.compare_table= CompareTable(...)

        # 3. Tạo nút bấm
        self.btn_dfs    = Button(...)
        self.btn_bfs    = Button(...)
        self.btn_astar  = Button(...)

    def run(self):
        while True:
            # === XỬ LÝ SỰ KIỆN ===
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if self.btn_dfs.handle_event(event):
                    result = PathFinder.dfs(self.grid, self.start, self.goal)
                    self.anim.start("DFS", result)

                # ... các nút khác ...

            # === CẬP NHẬT ===
            self.anim.update()   # animation tiến thêm 1 bước

            # === VẼ ===
            self.screen.fill(C_BG)  # xóa màn hình
            draw_maze(self.screen, self.grid)
            draw_animation(self.screen, self.anim)
            self.stats_panel.draw(self.screen)
            for btn in self.buttons:
                btn.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)
```

---

## 13. So Sánh 3 Thuật Toán

Đây là bảng so sánh đầy đủ, dễ nhớ:

| | DFS | BFS | A* |
|---|---|---|---|
| **Cấu trúc** | Stack (LIFO) | Queue (FIFO) | Priority Queue (Min-Heap) |
| **Ưu tiên** | Đi sâu nhất | Đi gần nhất (bước) | Đi "có vẻ gần goal" nhất |
| **Đường ngắn nhất?** | ❌ Không | ✅ Có | ✅ Có |
| **Nodes duyệt** | Nhiều (lang thang) | Nhiều (lan đều) | **Ít nhất** |
| **Tốc độ thực tế** | Nhanh hoặc chậm | Chậm hơn A* | **Thường nhanh nhất** |
| **RAM** | Ít nhất | Nhiều nhất | Trung bình |
| **Dùng khi** | Cần 1 đường bất kỳ | Cần đường ngắn nhất | Biết vị trí goal |

### Khi nào A* thua BFS?

Trên **Perfect Maze** (1 đường duy nhất), BFS đôi khi nhanh hơn A* vì:
- Maze 1 đường → heuristic không giúp được nhiều
- Overhead tính toán f(n) của A* trở thành gánh nặng

Trên **maze nhiều đường** (imperfect), A* luôn thắng.

---

## 14. Câu Hỏi Thường Gặp

### ❓ Tại sao DFS đôi khi cho đường ngắn hơn BFS?

Trên perfect maze (1 đường), DFS và BFS **phải tìm đúng con đường duy nhất đó** — path length bằng nhau.  
Nếu DFS cho path ngắn hơn, đó là trùng hợp trong maze cụ thể đó.  
Trên maze nhiều đường, BFS LUÔN tối ưu hơn.

### ❓ `deque` khác `list` ở điểm nào?

```python
# list.pop(0) = O(n) vì phải dịch tất cả phần tử
# deque.popleft() = O(1) vì không dịch gì cả

# Dùng deque cho queue → BFS nhanh hơn rất nhiều
from collections import deque
q = deque([1, 2, 3])
q.popleft()   # O(1) ✅
```

### ❓ `heapq` hoạt động như thế nào?

```python
import heapq

heap = []
heapq.heappush(heap, (5, "C"))  # (priority, item)
heapq.heappush(heap, (1, "A"))
heapq.heappush(heap, (3, "B"))

heapq.heappop(heap)   # → (1, "A") — luôn lấy nhỏ nhất
heapq.heappop(heap)   # → (3, "B")
heapq.heappop(heap)   # → (5, "C")
```

### ❓ Tại sao COLS/ROWS phải là số lẻ?

Thuật toán maze generation nhảy 2 ô một lúc:
- Ô **chỉ số lẻ** (1,3,5...) = ô đường đi
- Ô **chỉ số chẵn** (0,2,4...) = tường

Grid kích thước lẻ (ví dụ 7) có index 0→6:  
Viền: 0 và 6 (chẵn → tường ✅)

Grid kích thước chẵn (ví dụ 6):  
Viền: 0 và 5 (5 là lẻ → đường đi ❌ → lỗi!)

### ❓ Đường mờ và đường đậm là gì?

- **Mờ**: tất cả ô thuật toán đã **duyệt qua** (kể cả ngõ cụt)
- **Đậm**: con đường thực sự từ Start → Goal

### ❓ Tại sao dùng `set` thay vì `list` cho `visited`?

```python
# Kiểm tra trong list → O(n) — phải duyệt từng phần tử
if node in [a, b, c, d, ...]   # chậm!

# Kiểm tra trong set → O(1) — hash lookup
if node in {a, b, c, d, ...}   # nhanh!
```

---

## 🎯 Tóm Tắt Lộ Trình Học

```
Tuần 1: Python cơ bản (list, dict, class, set)
         → Tạo grid 2D đơn giản, vẽ bằng print()

Tuần 2: Maze Generation
         → Hiểu cách nhảy 2 ô, viết _carve_iterative()
         → Vẽ maze bằng * và space trong terminal

Tuần 3: Pygame cơ bản
         → Vẽ hình chữ nhật màu sắc
         → Game loop, xử lý sự kiện

Tuần 4: DFS + BFS
         → Hiểu Stack/Queue
         → Code tìm đường, in ra path

Tuần 5: A* + Heuristic
         → Hiểu f=g+h
         → Code heapq

Tuần 6: Ghép tất cả
         → Animation, UI, thống kê
         → Game hoàn chỉnh!
```

---

*Document này được tạo cùng với file `maze_game.py` — mã nguồn hoàn chỉnh đã có sẵn để bạn đọc và học.*

*Chúc bạn học vui! 🚀*
