import pygame

from ui.theme import ALGO_COLORS, C_ASTAR_PATH, C_BFS_PATH, C_DFS_PATH, C_GOAL, C_PANEL_BG, C_PASSAGE, C_START, C_TEXT_ACCENT, C_TEXT_SECONDARY, C_WALL


class MazeRenderer:
    def __init__(self, screen, font_xs, font_sm, cols, rows, cell_size, maze_x_offset, maze_y_offset):
        self.screen = screen
        self.font_xs = font_xs
        self.font_sm = font_sm
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.maze_x_offset = maze_x_offset
        self.maze_y_offset = maze_y_offset

    def draw_cell(self, r: int, c: int, color: tuple, shrink: int = 0):
        rx = self.maze_x_offset + c * self.cell_size + shrink
        ry = self.maze_y_offset + r * self.cell_size + shrink
        size = self.cell_size - shrink * 2
        rect = pygame.Rect(rx, ry, size, size)
        pygame.draw.rect(self.screen, color, rect)
        if shrink == 0:
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def draw_maze(self, grid):
        for r in range(self.rows):
            for c in range(self.cols):
                rx = self.maze_x_offset + c * self.cell_size
                ry = self.maze_y_offset + r * self.cell_size
                rect = pygame.Rect(rx, ry, self.cell_size, self.cell_size)

                if grid[r][c] == 0:
                    pygame.draw.rect(self.screen, C_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, C_PASSAGE, rect)
                    pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def draw_layers(self, layers, anim):
        for algo, result in layers.items():
            if algo == anim.algo_name and anim.state != "done":
                continue

            visit_col = ALGO_COLORS[algo]["visit"]
            path_col = ALGO_COLORS[algo]["path"]

            for node in result["visited_order"]:
                self.draw_cell(*node, visit_col)

            for node in result["path"]:
                self.draw_cell(*node, path_col)

        if anim.algo_name and anim.state != "idle":
            algo = anim.algo_name
            visit_col = ALGO_COLORS[algo]["visit"]
            path_col = ALGO_COLORS[algo]["path"]

            for node in anim.shown_visited:
                self.draw_cell(*node, visit_col)

            if anim.state == "visiting" and anim.vis_index < len(anim.visited_order):
                cur = anim.visited_order[anim.vis_index - 1] if anim.vis_index > 0 else None
                if cur:
                    self.draw_cell(*cur, (255, 255, 255))

            for node in anim.shown_path:
                self.draw_cell(*node, path_col, shrink=2)

    def draw_start_goal(self, start, goal):
        sr, sc = start
        gr, gc = goal

        t = pygame.time.get_ticks()
        is_blink = (t // 400) % 2 == 0

        color_start = (50, 205, 50) if is_blink else C_START
        color_goal = (255, 100, 100) if is_blink else C_GOAL

        self.draw_cell(sr, sc, color_start)
        if is_blink:
            rx = self.maze_x_offset + sc * self.cell_size
            ry = self.maze_y_offset + sr * self.cell_size
            pygame.draw.rect(self.screen, (255, 255, 0), (rx, ry, self.cell_size, self.cell_size), 1)

        s_lbl = self.font_xs.render("S", True, (255, 255, 255))
        self.screen.blit(
            s_lbl,
            (self.maze_x_offset + sc * self.cell_size + 4, self.maze_y_offset + sr * self.cell_size + 3),
        )

        self.draw_cell(gr, gc, color_goal)
        if is_blink:
            rx = self.maze_x_offset + gc * self.cell_size
            ry = self.maze_y_offset + gr * self.cell_size
            pygame.draw.rect(self.screen, (255, 255, 0), (rx, ry, self.cell_size, self.cell_size), 1)

        g_lbl = self.font_xs.render("G", True, (255, 255, 255))
        self.screen.blit(
            g_lbl,
            (self.maze_x_offset + gc * self.cell_size + 4, self.maze_y_offset + gr * self.cell_size + 3),
        )

    def draw_status_bar(self, status_msg: str):
        bar_y = self.rows * self.cell_size + self.maze_y_offset + 4
        bar_r = pygame.Rect(self.maze_x_offset, bar_y, self.cols * self.cell_size, 22)
        bar_s = pygame.Surface((bar_r.w, bar_r.h), pygame.SRCALPHA)
        bar_s.fill((*C_PANEL_BG, 200))
        self.screen.blit(bar_s, bar_r.topleft)

        msg = self.font_sm.render(status_msg, True, C_TEXT_ACCENT)
        self.screen.blit(msg, (bar_r.x + 8, bar_r.y + 3))

    def draw_legend(self):
        items = [
            ("Start", C_START),
            ("Goal", C_GOAL),
            ("DFS path", C_DFS_PATH),
            ("BFS path", C_BFS_PATH),
            ("A* path", C_ASTAR_PATH),
        ]

        lx = self.maze_x_offset
        ly = self.maze_y_offset - 22

        for label, col in items:
            pygame.draw.rect(self.screen, col, (lx, ly + 2, 12, 12), border_radius=2)
            txt = self.font_xs.render(label, True, C_TEXT_SECONDARY)
            self.screen.blit(txt, (lx + 16, ly))
            lx += txt.get_width() + 30