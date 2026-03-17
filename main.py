import sys
import random
from collections import deque
import pygame

from config import (
    CELL_SIZE,
    COLS,
    MAZE_X_OFFSET,
    MAZE_Y_OFFSET,
    PANEL_WIDTH,
    ROWS,
    SHOW_BOTTOM_HINT,
    SHOW_CONSOLE_EXPLANATIONS,
    SHOW_CONSOLE_STATS,
    WINDOW_H,
    WINDOW_W,
)
from logic.maze_generator import MazeGenerator
from services.solver_service import SolverService
from ui.animation import AnimationManager
from ui.panels import CompareTable, StatsPanel
from ui.renderer import MazeRenderer
from ui.texts import (
    ALGORITHM_ORDER,
    APP_TITLE,
    BOTTOM_HINT,
    BUTTON_ICONS,
    BUTTON_LABELS,
    CONSOLE_EXPLANATIONS,
    CONSOLE_TEXT,
    STATUS_MESSAGES,
)
from ui.theme import C_BG, C_BTN_ASTAR, C_BTN_BFS, C_BTN_COMPARE, C_BTN_DFS, C_BTN_PLAY, C_BTN_RESET, C_TEXT_SECONDARY
from ui.widgets import Button


class MazeGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(APP_TITLE)

        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock = pygame.time.Clock()

        self.font_lg = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_md = pygame.font.SysFont("Segoe UI", 15, bold=True)
        self.font_sm = pygame.font.SysFont("Segoe UI", 13)
        self.font_xs = pygame.font.SysFont("Segoe UI", 11)

        self.grid = []
        self.start = (1, 1)
        self.goal = (ROWS - 2, COLS - 2)

        self.anim = AnimationManager()
        self.layers: dict[str, dict] = {}
        self._stats_printed = False
        self.game_mode = False
        self.player_pos: tuple[int, int] | None = None
        self.player_history: list[tuple[int, int]] = []
        self.player_correct_path: list[tuple[int, int]] = []
        self.hold_initial_delay_ms = 160
        self.hold_repeat_delay_ms = 70
        self.last_hold_move_tick = 0
        self.last_hold_dir: tuple[int, int] | None = None
        self.hold_repeat_started = False

        panel_x = MAZE_X_OFFSET + COLS * CELL_SIZE + 20
        panel_y = MAZE_Y_OFFSET
        panel_h = WINDOW_H - MAZE_Y_OFFSET - 20

        self.stats_panel = StatsPanel(
            panel_x,
            panel_y,
            PANEL_WIDTH - 10,
            panel_h,
            self.font_sm,
            self.font_md,
            self.font_lg,
        )

        self.compare_table = CompareTable(
            WINDOW_W,
            WINDOW_H,
            self.font_xs,
            self.font_sm,
            self.font_md,
            self.font_lg,
        )

        self.renderer = MazeRenderer(
            self.screen,
            self.font_xs,
            self.font_sm,
            COLS,
            ROWS,
            CELL_SIZE,
            MAZE_X_OFFSET,
            MAZE_Y_OFFSET,
        )

        self._new_maze()
        self._create_buttons()
        self.status_msg = STATUS_MESSAGES["initial"]

    def _passage_candidates(self) -> list[tuple[int, int]]:
        # Prefer odd cells because maze carving treats them as room anchors.
        odd_cells = [
            (r, c)
            for r in range(1, ROWS - 1)
            for c in range(1, COLS - 1)
            if self.grid[r][c] == 1 and r % 2 == 1 and c % 2 == 1
        ]
        if odd_cells:
            return odd_cells

        return [
            (r, c)
            for r in range(1, ROWS - 1)
            for c in range(1, COLS - 1)
            if self.grid[r][c] == 1
        ]

    def _shortest_path_length(self, start: tuple[int, int], goal: tuple[int, int]) -> int:
        if start == goal:
            return 0

        q = deque([(start, 0)])
        visited = {start}

        while q:
            (r, c), dist = q.popleft()

            for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nr, nc = r + dr, c + dc
                nb = (nr, nc)

                if not (0 <= nr < ROWS and 0 <= nc < COLS):
                    continue
                if self.grid[nr][nc] != 1 or nb in visited:
                    continue
                if nb == goal:
                    return dist + 1

                visited.add(nb)
                q.append((nb, dist + 1))

        return -1

    def _randomize_start_goal(self):
        candidates = self._passage_candidates()
        if len(candidates) < 2:
            self.start = (1, 1)
            self.goal = (ROWS - 2, COLS - 2)
            return

        min_required = max(10, (ROWS + COLS) // 3)
        attempts = min(300, len(candidates) * 10)

        best_pair = None
        best_len = -1

        for _ in range(attempts):
            s = random.choice(candidates)
            g = random.choice(candidates)
            if s == g:
                continue

            path_len = self._shortest_path_length(s, g)
            if path_len > best_len:
                best_len = path_len
                best_pair = (s, g)

            if path_len >= min_required:
                self.start, self.goal = s, g
                return

        if best_pair is not None:
            self.start, self.goal = best_pair
            return

        self.start = candidates[0]
        self.goal = candidates[-1]

    def _new_maze(self):
        gen = MazeGenerator(ROWS, COLS)
        self.grid = gen.generate()
        self._randomize_start_goal()
        self.anim.reset()
        self.layers = {}
        self.game_mode = False
        self.player_pos = None
        self.player_history = []
        self.player_correct_path = []
        self.last_hold_move_tick = 0
        self.last_hold_dir = None
        self.hold_repeat_started = False
        self._stats_printed = False
        self.stats_panel.clear()
        if hasattr(self, "compare_table"):
            self.compare_table.hide()
        self.status_msg = STATUS_MESSAGES["new_maze"]

    def _create_buttons(self):
        bx = MAZE_X_OFFSET
        by = 20
        bw = 110
        bh = 38
        gap = 8

        self.btn_dfs = Button(
            pygame.Rect(bx, by, bw, bh),
            BUTTON_LABELS["DFS"],
            C_BTN_DFS,
            self.font_md,
            BUTTON_ICONS["DFS"],
        )
        self.btn_bfs = Button(
            pygame.Rect(bx + (bw + gap), by, bw, bh),
            BUTTON_LABELS["BFS"],
            C_BTN_BFS,
            self.font_md,
            BUTTON_ICONS["BFS"],
        )
        self.btn_astar = Button(
            pygame.Rect(bx + (bw + gap) * 2, by, bw, bh),
            BUTTON_LABELS["A*"],
            C_BTN_ASTAR,
            self.font_md,
            BUTTON_ICONS["A*"],
        )
        self.btn_play = Button(
            pygame.Rect(bx + (bw + gap) * 3, by, bw + 6, bh),
            BUTTON_LABELS["PLAY"],
            C_BTN_PLAY,
            self.font_md,
            BUTTON_ICONS["PLAY"],
        )
        self.btn_compare = Button(
            pygame.Rect(bx + (bw + gap) * 4 + 6, by, bw + 14, bh),
            BUTTON_LABELS["COMPARE"],
            C_BTN_COMPARE,
            self.font_md,
            BUTTON_ICONS["COMPARE"],
        )
        self.btn_reset = Button(
            pygame.Rect(bx + (bw + gap) * 5 + 20, by, bw + 8, bh),
            BUTTON_LABELS["RESET"],
            C_BTN_RESET,
            self.font_md,
            BUTTON_ICONS["RESET"],
        )
        self.btn_table = Button(
            pygame.Rect(bx + (bw + gap) * 6 + 28, by, bw + 14, bh),
            BUTTON_LABELS["TABLE"],
            (60, 160, 180),
            self.font_md,
            BUTTON_ICONS["TABLE"],
        )

        self.buttons = [
            self.btn_dfs,
            self.btn_bfs,
            self.btn_astar,
            self.btn_play,
            self.btn_compare,
            self.btn_reset,
            self.btn_table,
        ]

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

    def _start_player_game(self):
        if self.anim.state not in ("idle", "done"):
            return

        self.game_mode = True
        self.layers = {}
        self.anim.reset()
        self.stats_panel.clear()
        self.player_pos = self.start
        self.player_history = [self.start]
        self.player_correct_path = []
        self.last_hold_move_tick = pygame.time.get_ticks()
        self.last_hold_dir = None
        self.hold_repeat_started = False
        if hasattr(self, "compare_table"):
            self.compare_table.hide()
        self.status_msg = STATUS_MESSAGES["game_started"]

    def _handle_player_move(self, dr: int, dc: int):
        if not self.game_mode or self.player_pos is None:
            return

        r, c = self.player_pos
        nr, nc = r + dr, c + dc

        if not (0 <= nr < ROWS and 0 <= nc < COLS):
            return
        if self.grid[nr][nc] != 1:
            return

        self.player_pos = (nr, nc)
        self.player_history.append((nr, nc))

        if self.player_pos == self.goal:
            self._finish_player_game()

    def _finish_player_game(self):
        self.game_mode = False
        self.last_hold_dir = None
        self.hold_repeat_started = False
        self.player_correct_path = self._collapse_history_to_path(self.player_history)

        shortest = SolverService.run("BFS", self.grid, self.start, self.goal)["path"]
        shortest_steps = max(0, len(shortest) - 1)
        total_steps = max(0, len(self.player_history) - 1)
        correct_steps = max(0, len(self.player_correct_path) - 1)
        efficiency = 100.0
        if correct_steps > 0 and shortest_steps > 0:
            efficiency = min(100.0, (shortest_steps / correct_steps) * 100.0)

        self.status_msg = STATUS_MESSAGES["game_win"].format(
            steps=total_steps,
            correct_steps=correct_steps,
            shortest_steps=shortest_steps,
            efficiency=efficiency,
        )

    def _current_move_direction(self) -> tuple[int, int] | None:
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

    def _handle_held_player_movement(self):
        if not self.game_mode:
            return

        direction = self._current_move_direction()
        if direction is None:
            self.last_hold_dir = None
            self.hold_repeat_started = False
            return

        now = pygame.time.get_ticks()
        if direction != self.last_hold_dir:
            self.last_hold_dir = direction
            self.last_hold_move_tick = now
            self.hold_repeat_started = False
            return

        elapsed = now - self.last_hold_move_tick
        delay = self.hold_repeat_delay_ms if self.hold_repeat_started else self.hold_initial_delay_ms
        if elapsed < delay:
            return

        self.last_hold_move_tick = now
        self.hold_repeat_started = True
        self._handle_player_move(*direction)

    def _run_algorithm(self, algo_name: str):
        if self.game_mode:
            self.status_msg = STATUS_MESSAGES["game_blocked"]
            return

        if self.anim.state not in ("idle", "done"):
            return

        result = SolverService.run(algo_name, self.grid, self.start, self.goal)
        self.layers[algo_name] = result
        self.stats_panel.add_result(algo_name, result)
        self.anim.start(algo_name, result)
        self._stats_printed = False
        self.status_msg = STATUS_MESSAGES["running"].format(algo=algo_name)

    def _run_compare(self):
        if self.game_mode:
            self.status_msg = STATUS_MESSAGES["game_blocked"]
            return

        if self.anim.state not in ("idle", "done"):
            return

        self.layers = {}
        self.stats_panel.clear()

        for algo in ALGORITHM_ORDER:
            result = SolverService.run(algo, self.grid, self.start, self.goal)
            self.layers[algo] = result
            self.stats_panel.add_result(algo, result)

        self.anim.state = "done"
        self.status_msg = STATUS_MESSAGES["compare_done"]

        if SHOW_CONSOLE_STATS and not self._stats_printed:
            self._print_console_stats()
            self._stats_printed = True

    def _print_console_stats(self):
        print("\n" + CONSOLE_TEXT["line"])
        print(CONSOLE_TEXT["title"])
        print(CONSOLE_TEXT["line"])
        print(CONSOLE_TEXT["header"])
        print(CONSOLE_TEXT["subline"])

        valid = {}
        for algo, stats in self.stats_panel.results.items():
            pl = stats["path_length"]
            ne = stats["nodes_explored"]
            tm = stats["time_ms"]
            tag = "" if pl > 0 else CONSOLE_TEXT["not_found_tag"]
            print(f"  {algo:<10} {str(pl) + tag:>14} {ne:>16} {tm:>12.4f}")
            if pl > 0:
                valid[algo] = stats

        if valid:
            print(CONSOLE_TEXT["subline"])
            fastest = min(valid, key=lambda a: valid[a]["time_ms"])
            shortest = min(valid, key=lambda a: valid[a]["path_length"])
            print(CONSOLE_TEXT["fastest"].format(algo=fastest))
            print(CONSOLE_TEXT["shortest"].format(algo=shortest))

        if SHOW_CONSOLE_EXPLANATIONS:
            print("\n" + CONSOLE_TEXT["subline"])
            print(CONSOLE_TEXT["explanation_title"])
            print(CONSOLE_TEXT["subline"])

            for algo in ALGORITHM_ORDER:
                if algo in self.stats_panel.results:
                    print(CONSOLE_EXPLANATIONS[algo])

        print(CONSOLE_TEXT["line"] + "\n")

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.game_mode:
                        if event.key in (pygame.K_UP, pygame.K_w):
                            self._handle_player_move(-1, 0)
                            self.last_hold_dir = (-1, 0)
                            self.last_hold_move_tick = pygame.time.get_ticks()
                            self.hold_repeat_started = False
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self._handle_player_move(1, 0)
                            self.last_hold_dir = (1, 0)
                            self.last_hold_move_tick = pygame.time.get_ticks()
                            self.hold_repeat_started = False
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            self._handle_player_move(0, -1)
                            self.last_hold_dir = (0, -1)
                            self.last_hold_move_tick = pygame.time.get_ticks()
                            self.hold_repeat_started = False
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            self._handle_player_move(0, 1)
                            self.last_hold_dir = (0, 1)
                            self.last_hold_move_tick = pygame.time.get_ticks()
                            self.hold_repeat_started = False

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

                if self.compare_table.handle_event(event):
                    continue

                if self.btn_dfs.handle_event(event):
                    self._run_algorithm("DFS")
                if self.btn_bfs.handle_event(event):
                    self._run_algorithm("BFS")
                if self.btn_astar.handle_event(event):
                    self._run_algorithm("A*")
                if self.btn_play.handle_event(event):
                    self._start_player_game()
                if self.btn_compare.handle_event(event):
                    self._run_compare()
                if self.btn_reset.handle_event(event):
                    self._new_maze()
                if self.btn_table.handle_event(event):
                    self.compare_table.show(self.stats_panel.results)

            self._handle_held_player_movement()
            self.anim.update()

            if self.anim.is_done() and self.status_msg.startswith("🔍"):
                algo = self.anim.algo_name
                pl = self.anim.stats["path_length"]
                ne = self.anim.stats["nodes_explored"]
                tm = self.anim.stats["time_ms"]

                if pl > 0:
                    self.status_msg = STATUS_MESSAGES["algo_done"].format(
                        algo=algo,
                        path_length=pl,
                        nodes_explored=ne,
                        time_ms=tm,
                    )
                else:
                    self.status_msg = STATUS_MESSAGES["algo_failed"].format(algo=algo)

                if SHOW_CONSOLE_STATS and not self._stats_printed:
                    self._print_console_stats()
                    self._stats_printed = True

            self.screen.fill(C_BG)

            self.renderer.draw_maze(self.grid)
            self.renderer.draw_layers(self.layers, self.anim)
            self.renderer.draw_player_run(self.player_pos, self.player_history, self.player_correct_path)
            self.renderer.draw_start_goal(self.start, self.goal)
            self.renderer.draw_legend()
            self.renderer.draw_status_bar(self.status_msg)

            self.stats_panel.draw(self.screen)

            for btn in self.buttons:
                btn.draw(self.screen)

            if SHOW_BOTTOM_HINT:
                hint_y = ROWS * CELL_SIZE + MAZE_Y_OFFSET + 30
                hint = self.font_xs.render(BOTTOM_HINT, True, C_TEXT_SECONDARY)
                self.screen.blit(hint, (MAZE_X_OFFSET, hint_y))

            self.compare_table.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)


def main():
    game = MazeGame()
    game.run()


if __name__ == "__main__":
    main()