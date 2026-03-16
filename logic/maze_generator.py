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
        self._break_one_wall_for_second_path()
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

    def _break_one_wall_for_second_path(self):
        candidates = []

        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                if self.grid[r][c] != 0:
                    continue

                if self.grid[r][c - 1] == 1 and self.grid[r][c + 1] == 1:
                    candidates.append((r, c))
                elif self.grid[r - 1][c] == 1 and self.grid[r + 1][c] == 1:
                    candidates.append((r, c))

        if candidates:
            r, c = random.choice(candidates)
            self.grid[r][c] = 1