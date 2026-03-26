import pygame

from services.solver_service import SolverService
from ui.texts import STATUS_MESSAGES


class GameplayController:
    def __init__(self):
        self.game_mode = False
        self.player_pos: tuple[int, int] | None = None
        self.player_history: list[tuple[int, int]] = []
        self.player_correct_path: list[tuple[int, int]] = []
        self.hold_initial_delay_ms = 160
        self.hold_repeat_delay_ms = 70
        self.last_hold_move_tick = 0
        self.last_hold_dir: tuple[int, int] | None = None
        self.hold_repeat_started = False

    @staticmethod
    def _collapse_history_to_path(history: list[tuple[int, int]]) -> list[tuple[int, int]]:
        path: list[tuple[int, int]] = []
        index_of: dict[tuple[int, int], int] = {}

        for node in history:
            if node in index_of:
                cut_at = index_of[node]
                for old in path[cut_at + 1 :]:
                    index_of.pop(old, None)
                path = path[: cut_at + 1]
            else:
                index_of[node] = len(path)
                path.append(node)

        return path

    def reset(self):
        self.game_mode = False
        self.player_pos = None
        self.player_history = []
        self.player_correct_path = []
        self.last_hold_move_tick = 0
        self.last_hold_dir = None
        self.hold_repeat_started = False

    def start(self, start: tuple[int, int]) -> str:
        self.game_mode = True
        self.player_pos = start
        self.player_history = [start]
        self.player_correct_path = []
        self.last_hold_move_tick = pygame.time.get_ticks()
        self.last_hold_dir = None
        self.hold_repeat_started = False
        return STATUS_MESSAGES["game_started"]

    def move(self, dr: int, dc: int, grid, goal: tuple[int, int]) -> str | None:
        if not self.game_mode or self.player_pos is None:
            return None

        r, c = self.player_pos
        nr, nc = r + dr, c + dc
        rows, cols = len(grid), len(grid[0])

        if not (0 <= nr < rows and 0 <= nc < cols):
            return None
        if grid[nr][nc] != 1:
            return None

        self.player_pos = (nr, nc)
        self.player_history.append((nr, nc))

        if self.player_pos == goal:
            return self.finish(grid, self.player_history[0], goal)

        return None

    def finish(self, grid, start: tuple[int, int], goal: tuple[int, int]) -> str:
        self.game_mode = False
        self.last_hold_dir = None
        self.hold_repeat_started = False
        self.player_correct_path = self._collapse_history_to_path(self.player_history)

        shortest = SolverService.run("BFS", grid, start, goal)["path"]
        shortest_steps = max(0, len(shortest) - 1)
        total_steps = max(0, len(self.player_history) - 1)
        correct_steps = max(0, len(self.player_correct_path) - 1)
        efficiency = 100.0
        if correct_steps > 0 and shortest_steps > 0:
            efficiency = min(100.0, (shortest_steps / correct_steps) * 100.0)

        return STATUS_MESSAGES["game_win"].format(
            steps=total_steps,
            correct_steps=correct_steps,
            shortest_steps=shortest_steps,
            efficiency=efficiency,
        )

    @staticmethod
    def current_move_direction() -> tuple[int, int] | None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            return (-1, 0)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            return (1, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            return (0, -1)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            return (0, 1)
        return None

    def handle_held_movement(self, grid, goal: tuple[int, int]) -> str | None:
        if not self.game_mode:
            return None

        direction = self.current_move_direction()
        if direction is None:
            self.last_hold_dir = None
            self.hold_repeat_started = False
            return None

        now = pygame.time.get_ticks()
        if direction != self.last_hold_dir:
            self.last_hold_dir = direction
            self.last_hold_move_tick = now
            self.hold_repeat_started = False
            return None

        elapsed = now - self.last_hold_move_tick
        delay = self.hold_repeat_delay_ms if self.hold_repeat_started else self.hold_initial_delay_ms
        if elapsed < delay:
            return None

        self.last_hold_move_tick = now
        self.hold_repeat_started = True
        return self.move(*direction, grid, goal)

    def on_keydown_move(self, direction: tuple[int, int], grid, goal: tuple[int, int]) -> str | None:
        status_msg = self.move(*direction, grid, goal)
        self.last_hold_dir = direction
        self.last_hold_move_tick = pygame.time.get_ticks()
        self.hold_repeat_started = False
        return status_msg
