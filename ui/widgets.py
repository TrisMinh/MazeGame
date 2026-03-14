import pygame

from ui.theme import C_TEXT_PRIMARY


class Button:
    def __init__(self, rect: pygame.Rect, label: str, color: tuple, font: pygame.font.Font, icon: str = ""):
        self.rect = rect
        self.label = label
        self.color = color
        self.font = font
        self.icon = icon
        self.hovered = False
        self.enabled = True

    def draw(self, surface: pygame.Surface):
        alpha = 255 if self.enabled else 100
        base = tuple(min(255, c + 30) for c in self.color) if self.hovered else self.color
        col = (*base, alpha)

        btn_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, col, (0, 0, self.rect.w, self.rect.h), border_radius=8)

        light = tuple(min(255, c + 60) for c in self.color)
        pygame.draw.rect(btn_surf, (*light, 180), (0, 0, self.rect.w, self.rect.h), 2, border_radius=8)

        surface.blit(btn_surf, self.rect.topleft)

        text = f"{self.icon} {self.label}".strip()
        lbl = self.font.render(text, True, C_TEXT_PRIMARY)
        lx = self.rect.centerx - lbl.get_width() // 2
        ly = self.rect.centery - lbl.get_height() // 2
        surface.blit(lbl, (lx, ly))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos) and self.enabled

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.enabled:
                return True

        return False