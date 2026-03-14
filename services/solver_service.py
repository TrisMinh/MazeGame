from logic.pathfinder import PathFinder


class SolverService:
    FINDERS = {
        "DFS": PathFinder.dfs,
        "BFS": PathFinder.bfs,
        "A*": PathFinder.astar,
    }

    @classmethod
    def run(cls, algo_name: str, grid, start, goal):
        finder = cls.FINDERS[algo_name]
        return finder(grid, start, goal)