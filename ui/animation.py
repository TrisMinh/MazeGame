import pygame

BASE_DELAY = 5
FAST_DELAY = 2


class AnimationManager:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state = "idle"
        self.algo_name = None
        self.visited_order = []
        self.path = []
        self.vis_index = 0
        self.path_index = 0
        self.shown_visited = set()
        self.shown_path = set()
        self.delay_ms = BASE_DELAY
        self.last_tick = 0
        self.stats = None

    def start(self, algo_name: str, result: dict, delay: int = BASE_DELAY):
        self.reset()
        self.state = "visiting"
        self.algo_name = algo_name
        self.visited_order = result["visited_order"]
        self.path = result["path"]
        self.delay_ms = delay
        self.stats = result
        self.last_tick = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()

        if now - self.last_tick < self.delay_ms:
            return

        self.last_tick = now

        if self.state == "visiting":
            if self.vis_index < len(self.visited_order):
                self.shown_visited.add(self.visited_order[self.vis_index])
                self.vis_index += 1
            else:
                self.state = "pathing"

        elif self.state == "pathing":
            if self.path_index < len(self.path):
                self.shown_path.add(self.path[self.path_index])
                self.path_index += 1
            else:
                self.state = "done"

    def is_done(self) -> bool:
        return self.state == "done"