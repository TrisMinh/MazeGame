import pygame

from ui.theme import ALGO_COLORS, C_PANEL_BG, C_PANEL_BORDER, C_TEXT_ACCENT, C_TEXT_PRIMARY, C_TEXT_SECONDARY


class StatsPanel:
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
        self.rect = pygame.Rect(x, y, w, h)
        self.font_sm = font_sm
        self.font_md = font_md
        self.font_lg = font_lg
        self.results: dict = {}
        self.scroll_y: int = 0

    def add_result(self, algo_name: str, stats: dict):
        self.results[algo_name] = stats

    def clear(self):
        self.results = {}
        self.scroll_y = 0

    def draw(self, surface: pygame.Surface):
        panel_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        panel_surf.fill((*C_PANEL_BG, 230))
        surface.blit(panel_surf, self.rect.topleft)

        pygame.draw.rect(surface, C_PANEL_BORDER, self.rect, 2, border_radius=8)

        y = self.rect.y + 14
        x = self.rect.x + 14
        w = self.rect.w - 28

        title = self.font_md.render("📊 Kết quả & Phân tích", True, C_TEXT_ACCENT)
        surface.blit(title, (x, y))
        y += title.get_height() + 6

        pygame.draw.line(surface, C_PANEL_BORDER, (x, y), (x + w, y))
        y += 10

        if not self.results:
            hint = self.font_sm.render("Chọn thuật toán và nhấn nút để chạy.", True, C_TEXT_SECONDARY)
            surface.blit(hint, (x, y))
            y += 30

            for algo, info in ALGO_COLORS.items():
                pygame.draw.rect(surface, info["path"], (x, y + 3, 14, 14), border_radius=3)
                txt = self.font_sm.render(algo, True, C_TEXT_PRIMARY)
                surface.blit(txt, (x + 20, y))
                y += 22

            return

        order = ["DFS", "BFS", "A*"]
        for algo in order:
            if algo not in self.results:
                continue

            stats = self.results[algo]
            color = ALGO_COLORS[algo]["path"]

            pygame.draw.rect(surface, (*color, 50), (x - 2, y - 2, w + 4, 22), border_radius=4)
            hdr = self.font_md.render(f"▶ {algo}", True, color)
            surface.blit(hdr, (x + 2, y))
            y += 24

            rows_data = [
                ("Path length", f"{stats['path_length']} bước" if stats["path_length"] else "Không tìm được"),
                ("Nodes explored", f"{stats['nodes_explored']}"),
                ("Time", f"{stats['time_ms']:.3f} ms"),
            ]

            for label, val in rows_data:
                lbl_surf = self.font_sm.render(f"  {label}:", True, C_TEXT_SECONDARY)
                val_surf = self.font_sm.render(val, True, C_TEXT_PRIMARY)
                surface.blit(lbl_surf, (x, y))
                surface.blit(val_surf, (x + w - val_surf.get_width(), y))
                y += 18

            y += 6

        if len(self.results) >= 2:
            pygame.draw.line(surface, C_PANEL_BORDER, (x, y), (x + w, y))
            y += 8

            cmp_txt = self.font_sm.render("🏆 So sánh", True, C_TEXT_ACCENT)
            surface.blit(cmp_txt, (x, y))
            y += 20

            valid = {a: s for a, s in self.results.items() if s["path_length"] > 0}
            if valid:
                fastest = min(valid, key=lambda a: valid[a]["time_ms"])
                shortest = min(valid, key=lambda a: valid[a]["path_length"])
                efficient = min(valid, key=lambda a: valid[a]["nodes_explored"])

                lines = [
                    ("⚡ Nhanh nhất", fastest, ALGO_COLORS[fastest]["path"]),
                    ("📏 Đường ngắn", shortest, ALGO_COLORS[shortest]["path"]),
                    ("🧠 Ít node nhất", efficient, ALGO_COLORS[efficient]["path"]),
                ]

                for label, winner, col in lines:
                    lbl = self.font_sm.render(label + ":", True, C_TEXT_SECONDARY)
                    win = self.font_sm.render(winner, True, col)
                    surface.blit(lbl, (x, y))
                    surface.blit(win, (x + w - win.get_width(), y))
                    y += 18

                y += 8

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
                    pygame.draw.line(surface, (*color, 120), (x, y + 6), (x + w, y + 6))
                    y += 14
                else:
                    style_col = color if not line.startswith("•") else C_TEXT_PRIMARY
                    txt_surf = self.font_sm.render(line, True, style_col)
                    surface.blit(txt_surf, (x, y))
                    y += 16

            y += 8


class CompareTable:
    def __init__(self, screen_w: int, screen_h: int, font_xs, font_sm, font_md, font_lg):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.font_xs = font_xs
        self.font_sm = font_sm
        self.font_md = font_md
        self.font_lg = font_lg
        self.visible = False
        self.results = {}

        self.w = 620
        self.h = 480
        self.x = (screen_w - self.w) // 2
        self.y = (screen_h - self.h) // 2
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def show(self, results: dict):
        self.results = results
        self.visible = len(results) > 0

    def hide(self):
        self.visible = False

    def handle_event(self, event) -> bool:
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide()
            return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.rect.collidepoint(event.pos):
                self.hide()
            return True

        return self.visible

    def _draw_bar_section(self, surface, sx, sy, sw, label: str, values: dict, fmt_fn, bar_color_key: str):
        hdr = self.font_md.render(label, True, C_TEXT_ACCENT)
        surface.blit(hdr, (sx, sy))
        sy += 22

        if not values:
            na = self.font_sm.render("(Chưa có dữ liệu)", True, C_TEXT_SECONDARY)
            surface.blit(na, (sx, sy))
            return sy + 18

        max_val = max(values.values()) or 1
        bar_h = 20
        gap = 10
        algos = ["DFS", "BFS", "A*"]

        for algo in algos:
            if algo not in values:
                continue

            val = values[algo]
            col = ALGO_COLORS[algo][bar_color_key]
            bar_w = int((val / max_val) * (sw - 120))

            al = self.font_sm.render(f"{algo:<4}", True, col)
            surface.blit(al, (sx, sy + 2))

            bar_rect = pygame.Rect(sx + 38, sy, bar_w, bar_h)
            bar_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
            bar_surf.fill((*col, 180))
            surface.blit(bar_surf, bar_rect.topleft)
            pygame.draw.rect(surface, col, bar_rect, 1, border_radius=3)

            val_txt = self.font_sm.render(fmt_fn(val), True, C_TEXT_PRIMARY)
            surface.blit(val_txt, (sx + 38 + bar_w + 6, sy + 2))

            sy += bar_h + gap

        return sy + 4

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        pop_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pop_surf.fill((*C_PANEL_BG, 250))
        surface.blit(pop_surf, (self.x, self.y))
        pygame.draw.rect(surface, C_TEXT_ACCENT, self.rect, 2, border_radius=12)

        px, py = self.x + 24, self.y + 18
        pw = self.w - 48

        title = self.font_lg.render("📊 Bảng So Sánh Thuật Toán", True, C_TEXT_ACCENT)
        surface.blit(title, (px, py))
        py += title.get_height() + 4

        hint = self.font_xs.render("Nhấn ESC hoặc click bên ngoài để đóng", True, C_TEXT_SECONDARY)
        surface.blit(hint, (px, py))
        py += hint.get_height() + 10

        pygame.draw.line(surface, C_PANEL_BORDER, (px, py), (px + pw, py))
        py += 12

        if not self.results:
            msg = self.font_md.render("Chưa có kết quả. Hãy chạy ít nhất 1 thuật toán!", True, C_TEXT_SECONDARY)
            surface.blit(msg, (px, py))
            return

        col_widths = [70, 110, 130, 120]
        headers = ["Thuật toán", "Path length", "Nodes explored", "Time (ms)"]
        row_h = 24
        algos = ["DFS", "BFS", "A*"]

        cx = px
        for i, h in enumerate(headers):
            hs = self.font_sm.render(h, True, C_TEXT_SECONDARY)
            surface.blit(hs, (cx, py))
            cx += col_widths[i]

        py += row_h
        pygame.draw.line(surface, C_PANEL_BORDER, (px, py - 4), (px + pw, py - 4))

        valid = {}
        for algo in algos:
            if algo not in self.results:
                continue

            s = self.results[algo]
            col = ALGO_COLORS[algo]["path"]

            pygame.draw.rect(surface, (*col, 20), (px - 4, py - 2, pw + 8, row_h - 2), border_radius=3)

            cx = px
            cells = [
                algo,
                f"{s['path_length']} bước" if s["path_length"] else "N/A",
                str(s["nodes_explored"]),
                f"{s['time_ms']:.4f}",
            ]

            for i, cell in enumerate(cells):
                cs = self.font_sm.render(cell, True, col if i == 0 else C_TEXT_PRIMARY)
                surface.blit(cs, (cx, py))
                cx += col_widths[i]

            py += row_h

            if s["path_length"] > 0:
                valid[algo] = s

        if valid:
            pygame.draw.line(surface, C_PANEL_BORDER, (px, py), (px + pw, py))
            py += 8

            winners = [
                ("⚡ Nhanh nhất", min(valid, key=lambda a: valid[a]["time_ms"])),
                ("📏 Đường ngắn", min(valid, key=lambda a: valid[a]["path_length"])),
                ("🧠 Ít node nhất", min(valid, key=lambda a: valid[a]["nodes_explored"])),
            ]

            wx = px
            for label, winner in winners:
                wcol = ALGO_COLORS[winner]["path"]
                ls = self.font_sm.render(f"{label}: ", True, C_TEXT_SECONDARY)
                ws = self.font_sm.render(winner, True, wcol)
                surface.blit(ls, (wx, py))
                surface.blit(ws, (wx + ls.get_width(), py))
                wx += 200

            py += 24

        pygame.draw.line(surface, C_PANEL_BORDER, (px, py), (px + pw, py))
        py += 12

        half_w = pw // 2 - 10

        path_vals = {a: s["path_length"] for a, s in self.results.items() if s["path_length"] > 0}
        py_left = self._draw_bar_section(
            surface,
            px,
            py,
            half_w,
            "📏 Path Length (bước)",
            path_vals,
            lambda v: str(v),
            "path",
        )

        node_vals = {a: s["nodes_explored"] for a, s in self.results.items()}
        self._draw_bar_section(
            surface,
            px + half_w + 20,
            py,
            half_w,
            "🔍 Nodes Explored",
            node_vals,
            lambda v: str(v),
            "visit",
        )

        py = max(py_left, py + 100) + 6

        if py < self.y + self.h - 60:
            time_vals = {a: s["time_ms"] for a, s in self.results.items()}
            self._draw_bar_section(
                surface,
                px,
                py,
                pw,
                "⏱ Time (ms)",
                time_vals,
                lambda v: f"{v:.4f}ms",
                "path",
            )