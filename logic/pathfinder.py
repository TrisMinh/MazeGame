import heapq
import time
from collections import deque


class PathFinder:
    DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    @staticmethod
    def _neighbors(grid, r, c):
        rows, cols = len(grid), len(grid[0])
        result = []

        for dr, dc in PathFinder.DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                result.append((nr, nc))

        return result

    @staticmethod
    def _reconstruct_path(came_from: dict, start: tuple, goal: tuple) -> list:
        path = []
        node = goal

        while node is not None:
            path.append(node)
            node = came_from.get(node)

        path.reverse()
        return path if path and path[0] == start else []

    @staticmethod
    def dfs(grid, start: tuple, goal: tuple) -> dict:
        t_start = time.perf_counter()

        frontier = [start]
        came_from = {start: None}
        explored = set()
        visited_order = []

        while frontier:
            current = frontier.pop()

            if current in explored:
                continue

            explored.add(current)
            visited_order.append(current)

            if current == goal:
                break

            for nb in PathFinder._neighbors(grid, *current):
                if nb not in explored:
                    frontier.append(nb)
                    if nb not in came_from:
                        came_from[nb] = current

        elapsed = time.perf_counter() - t_start
        path = PathFinder._reconstruct_path(came_from, start, goal) if goal in came_from else []

        return {
            "visited_order": visited_order,
            "path": path,
            "nodes_explored": len(visited_order),
            "path_length": len(path),
            "time_ms": elapsed * 1000,
        }

    @staticmethod
    def bfs(grid, start: tuple, goal: tuple) -> dict:
        t_start = time.perf_counter()

        frontier = deque([start])
        came_from = {start: None}
        visited_order = []

        while frontier:
            current = frontier.popleft()
            visited_order.append(current)

            if current == goal:
                break

            for nb in PathFinder._neighbors(grid, *current):
                if nb not in came_from:
                    came_from[nb] = current
                    frontier.append(nb)

        elapsed = time.perf_counter() - t_start
        path = PathFinder._reconstruct_path(came_from, start, goal) if goal in came_from else []

        return {
            "visited_order": visited_order,
            "path": path,
            "nodes_explored": len(visited_order),
            "path_length": len(path),
            "time_ms": elapsed * 1000,
        }

    @staticmethod
    def astar(grid, start: tuple, goal: tuple) -> dict:
        t_start = time.perf_counter()

        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        frontier = [(heuristic(start, goal), 0, start)]
        came_from = {start: None}
        g_score = {start: 0}
        counter = 1
        visited_order = []
        explored = set()

        while frontier:
            _, _, current = heapq.heappop(frontier)

            if current in explored:
                continue

            explored.add(current)
            visited_order.append(current)

            if current == goal:
                break

            for nb in PathFinder._neighbors(grid, *current):
                if nb in explored:
                    continue

                tentative_g = g_score[current] + 1

                if tentative_g < g_score.get(nb, float("inf")):
                    came_from[nb] = current
                    g_score[nb] = tentative_g
                    f_new = tentative_g + heuristic(nb, goal)
                    heapq.heappush(frontier, (f_new, counter, nb))
                    counter += 1

        elapsed = time.perf_counter() - t_start
        path = PathFinder._reconstruct_path(came_from, start, goal) if goal in came_from else []

        return {
            "visited_order": visited_order,
            "path": path,
            "nodes_explored": len(visited_order),
            "path_length": len(path),
            "time_ms": elapsed * 1000,
        }