import random


class MazeGenerator:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid = [[0] * cols for _ in range(rows)]

    def generate(self) -> list[list[int]]:
        self._carve_iterative(1, 1)
        self.grid[1][1] = 1
        self.grid[self.rows - 2][self.cols - 2] = 1
        self._break_extra_walls_for_loops()
        return self.grid

    def _carve_iterative(self, start_r: int, start_c: int):
        dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]

        self.grid[start_r][start_c] = 1
        frontier = [(start_r, start_c)]

        while frontier:
            r, c = frontier[-1]
            neighbors = []

            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 1 <= nr < self.rows - 1 and 1 <= nc < self.cols - 1 and self.grid[nr][nc] == 0:
                    neighbors.append((dr, dc, nr, nc))

            if neighbors:
                dr, dc, nr, nc = random.choice(neighbors)
                self.grid[r + dr // 2][c + dc // 2] = 1
                self.grid[nr][nc] = 1
                frontier.append((nr, nc))
            else:
                frontier.pop()

    def _break_extra_walls_for_loops(self):
        candidates = []

        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                if self.grid[r][c] != 0:
                    continue

                if self.grid[r][c - 1] == 1 and self.grid[r][c + 1] == 1:
                    candidates.append((r, c))
                elif self.grid[r - 1][c] == 1 and self.grid[r + 1][c] == 1:
                    candidates.append((r, c))

        if not candidates:
            return

        room_count = ((self.rows - 1) // 2) * ((self.cols - 1) // 2)
        target_breaks = max(2, room_count // 50)
        target_breaks = min(target_breaks, len(candidates))

        for r, c in random.sample(candidates, target_breaks):
            self.grid[r][c] = 1