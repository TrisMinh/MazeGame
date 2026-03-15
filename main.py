import sys
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
from ui.theme import C_BG, C_BTN_ASTAR, C_BTN_BFS, C_BTN_COMPARE, C_BTN_DFS, C_BTN_RESET, C_TEXT_SECONDARY
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

    def _new_maze(self):
        gen = MazeGenerator(ROWS, COLS)
        self.grid = gen.generate()
        self.anim.reset()
        self.layers = {}
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
        self.btn_compare = Button(
            pygame.Rect(bx + (bw + gap) * 3, by, bw + 20, bh),
            BUTTON_LABELS["COMPARE"],
            C_BTN_COMPARE,
            self.font_md,
            BUTTON_ICONS["COMPARE"],
        )
        self.btn_reset = Button(
            pygame.Rect(bx + (bw + gap) * 4 + 20, by, bw + 10, bh),
            BUTTON_LABELS["RESET"],
            C_BTN_RESET,
            self.font_md,
            BUTTON_ICONS["RESET"],
        )
        self.btn_table = Button(
            pygame.Rect(bx + (bw + gap) * 5 + 30, by, bw + 20, bh),
            BUTTON_LABELS["TABLE"],
            (60, 160, 180),
            self.font_md,
            BUTTON_ICONS["TABLE"],
        )

        self.buttons = [
            self.btn_dfs,
            self.btn_bfs,
            self.btn_astar,
            self.btn_compare,
            self.btn_reset,
            self.btn_table,
        ]

    def _run_algorithm(self, algo_name: str):
        if self.anim.state not in ("idle", "done"):
            return

        result = SolverService.run(algo_name, self.grid, self.start, self.goal)
        self.layers[algo_name] = result
        self.stats_panel.add_result(algo_name, result)
        self.anim.start(algo_name, result)
        self._stats_printed = False
        self.status_msg = STATUS_MESSAGES["running"].format(algo=algo_name)

    def _run_compare(self):
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
                if self.btn_compare.handle_event(event):
                    self._run_compare()
                if self.btn_reset.handle_event(event):
                    self._new_maze()
                if self.btn_table.handle_event(event):
                    self.compare_table.show(self.stats_panel.results)

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