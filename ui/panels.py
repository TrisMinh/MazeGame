import pygame

from config import (
    SHOW_COMPARE_TABLE_HINT,
    SHOW_PANEL_COMPARISON,
    SHOW_PANEL_EMPTY_HINT,
    SHOW_PANEL_EXPLANATIONS,
    SHOW_PANEL_TITLE,
    SHOW_EXECUTION_TIME,
)
from ui.texts import ALGORITHM_ORDER, ALGO_EXPLANATIONS, COMPARE_TABLE_TEXT, STATS_PANEL_TEXT
from ui.theme import ALGO_COLORS, C_PANEL_BG, C_PANEL_BORDER, C_TEXT_ACCENT, C_TEXT_PRIMARY, C_TEXT_SECONDARY


class StatsPanel:
    def __init__(self, x: int, y: int, w: int, h: int, font_sm, font_md, font_lg):
        self.rect = pygame.Rect(x, y, w, h)
        self.font_sm = font_sm
        self.font_md = font_md
        self.font_lg = font_lg
        self.results: dict = {}

    def add_result(self, algo_name: str, stats: dict):
        self.results[algo_name] = stats

    def clear(self):
        self.results = {}

    def draw(self, surface: pygame.Surface):
        panel_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        panel_surf.fill((*C_PANEL_BG, 230))
        surface.blit(panel_surf, self.rect.topleft)

        pygame.draw.rect(surface, C_PANEL_BORDER, self.rect, 2, border_radius=8)

        y = self.rect.y + 14
        x = self.rect.x + 14
        w = self.rect.w - 28

        if SHOW_PANEL_TITLE:
            title = self.font_md.render(STATS_PANEL_TEXT["title"], True, C_TEXT_ACCENT)
            surface.blit(title, (x, y))
            y += title.get_height() + 6

            pygame.draw.line(surface, C_PANEL_BORDER, (x, y), (x + w, y))
            y += 10

        if not self.results:
            if SHOW_PANEL_EMPTY_HINT:
                hint = self.font_sm.render(STATS_PANEL_TEXT["empty_hint"], True, C_TEXT_SECONDARY)
                surface.blit(hint, (x, y))
                y += 30

            for algo, info in ALGO_COLORS.items():
                pygame.draw.rect(surface, info["path"], (x, y + 3, 14, 14), border_radius=3)
                txt = self.font_sm.render(algo, True, C_TEXT_PRIMARY)
                surface.blit(txt, (x + 20, y))
                y += 22

            return

        for algo in ALGORITHM_ORDER:
            if algo not in self.results:
                continue

            stats = self.results[algo]
            color = ALGO_COLORS[algo]["path"]

            pygame.draw.rect(surface, (*color, 50), (x - 2, y - 2, w + 4, 22), border_radius=4)
            hdr = self.font_md.render(f"▶ {algo}", True, color)
            surface.blit(hdr, (x + 2, y))
            y += 24

            rows_data = [
                (
                    STATS_PANEL_TEXT["path_length"],
                    f"{stats['path_length']} {STATS_PANEL_TEXT['steps_suffix']}"
                    if stats["path_length"]
                    else STATS_PANEL_TEXT["not_found"],
                ),
                (STATS_PANEL_TEXT["nodes_explored"], f"{stats['nodes_explored']}"),
            ]
            if SHOW_EXECUTION_TIME:
                rows_data.append((STATS_PANEL_TEXT["time"], f"{stats['time_ms']:.3f} ms"))

            for label, val in rows_data:
                lbl_surf = self.font_sm.render(f"  {label}:", True, C_TEXT_SECONDARY)
                val_surf = self.font_sm.render(val, True, C_TEXT_PRIMARY)
                surface.blit(lbl_surf, (x, y))
                surface.blit(val_surf, (x + w - val_surf.get_width(), y))
                y += 18

            y += 6

        if SHOW_PANEL_COMPARISON and len(self.results) >= 2:
            pygame.draw.line(surface, C_PANEL_BORDER, (x, y), (x + w, y))
            y += 8

            cmp_txt = self.font_sm.render(STATS_PANEL_TEXT["comparison_title"], True, C_TEXT_ACCENT)
            surface.blit(cmp_txt, (x, y))
            y += 20

            valid = {a: s for a, s in self.results.items() if s["path_length"] > 0}
            if valid:
                shortest = min(valid, key=lambda a: valid[a]["path_length"])
                efficient = min(valid, key=lambda a: valid[a]["nodes_explored"])

                lines = [
                    (STATS_PANEL_TEXT["shortest"], shortest, ALGO_COLORS[shortest]["path"]),
                    (STATS_PANEL_TEXT["efficient"], efficient, ALGO_COLORS[efficient]["path"]),
                ]
                if SHOW_EXECUTION_TIME:
                    fastest = min(valid, key=lambda a: valid[a]["time_ms"])
                    lines.insert(0, (STATS_PANEL_TEXT["fastest"], fastest, ALGO_COLORS[fastest]["path"]))

                for label, winner, col in lines:
                    lbl = self.font_sm.render(label + ":", True, C_TEXT_SECONDARY)
                    win = self.font_sm.render(winner, True, col)
                    surface.blit(lbl, (x, y))
                    surface.blit(win, (x + w - win.get_width(), y))
                    y += 18

                y += 8

        if SHOW_PANEL_EXPLANATIONS:
            pygame.draw.line(surface, C_PANEL_BORDER, (x, y), (x + w, y))
            y += 8

            ex_hdr = self.font_sm.render(STATS_PANEL_TEXT["explanations_title"], True, C_TEXT_ACCENT)
            surface.blit(ex_hdr, (x, y))
            y += 20

            for algo in ALGORITHM_ORDER:
                if algo not in self.results:
                    continue

                color = ALGO_COLORS[algo]["path"]

                for line in ALGO_EXPLANATIONS[algo]:
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
            na = self.font_sm.render(COMPARE_TABLE_TEXT["no_data"], True, C_TEXT_SECONDARY)
            surface.blit(na, (sx, sy))
            return sy + 18

        max_val = max(values.values()) or 1
        bar_h = 20
        gap = 10

        for algo in ALGORITHM_ORDER:
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

        title = self.font_lg.render(COMPARE_TABLE_TEXT["title"], True, C_TEXT_ACCENT)
        surface.blit(title, (px, py))
        py += title.get_height() + 4

        if SHOW_COMPARE_TABLE_HINT:
            hint = self.font_xs.render(COMPARE_TABLE_TEXT["close_hint"], True, C_TEXT_SECONDARY)
            surface.blit(hint, (px, py))
            py += hint.get_height() + 10
        else:
            py += 10

        pygame.draw.line(surface, C_PANEL_BORDER, (px, py), (px + pw, py))
        py += 12

        if not self.results:
            msg = self.font_md.render(COMPARE_TABLE_TEXT["empty"], True, C_TEXT_SECONDARY)
            surface.blit(msg, (px, py))
            return

        if SHOW_EXECUTION_TIME:
            col_widths = [70, 110, 130, 120]
            headers = COMPARE_TABLE_TEXT["headers"]
        else:
            col_widths = [100, 140, 160]
            headers = COMPARE_TABLE_TEXT["headers"][:3]
        row_h = 24

        cx = px
        for i, header in enumerate(headers):
            hs = self.font_sm.render(header, True, C_TEXT_SECONDARY)
            surface.blit(hs, (cx, py))
            cx += col_widths[i]

        py += row_h
        pygame.draw.line(surface, C_PANEL_BORDER, (px, py - 4), (px + pw, py - 4))

        valid = {}
        for algo in ALGORITHM_ORDER:
            if algo not in self.results:
                continue

            s = self.results[algo]
            col = ALGO_COLORS[algo]["path"]

            pygame.draw.rect(surface, (*col, 20), (px - 4, py - 2, pw + 8, row_h - 2), border_radius=3)

            cx = px
            cells = [
                algo,
                f"{s['path_length']} {COMPARE_TABLE_TEXT['steps_suffix']}"
                if s["path_length"]
                else COMPARE_TABLE_TEXT["not_available"],
                str(s["nodes_explored"]),
            ]
            if SHOW_EXECUTION_TIME:
                cells.append(f"{s['time_ms']:.4f}")

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
                (COMPARE_TABLE_TEXT["shortest"], min(valid, key=lambda a: valid[a]["path_length"])),
                (COMPARE_TABLE_TEXT["efficient"], min(valid, key=lambda a: valid[a]["nodes_explored"])),
            ]
            if SHOW_EXECUTION_TIME:
                winners.insert(0, (COMPARE_TABLE_TEXT["fastest"], min(valid, key=lambda a: valid[a]["time_ms"])))

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
            COMPARE_TABLE_TEXT["path_section"],
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
            COMPARE_TABLE_TEXT["node_section"],
            node_vals,
            lambda v: str(v),
            "visit",
        )

        py = max(py_left, py + 100) + 6

        if py < self.y + self.h - 60 and SHOW_EXECUTION_TIME:
            time_vals = {a: s["time_ms"] for a, s in self.results.items()}
            self._draw_bar_section(
                surface,
                px,
                py,
                pw,
                COMPARE_TABLE_TEXT["time_section"],
                time_vals,
                lambda v: f"{v:.4f}ms",
                "path",
            )