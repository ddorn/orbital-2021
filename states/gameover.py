import pygame

from core import State
from locals import Color


class GameOverState(State):
    def __init__(self, level, score):
        super().__init__()

        self.timer = 0
        self.level = level
        self.score = score

    def on_key_down(self, event):
        if event.key == pygame.K_SPACE:
            from states.game import GameState
            self.next_state = GameState()

    def logic(self):
        super(GameOverState, self).logic()
        self.timer += 1

    def draw(self, display):
        super().draw(display)

        if self.timer % 60 > 6:
            r = self.draw_text(display, "GAME OVER", Color.ORANGE, 64, center=self.size / 2)
            self.draw_text(display, "Press SPACE to restart", Color.BRIGHT, midtop=r.midbottom)

            self.draw_text(display, f"Score: {self.score}", topright=(self.w - 5, 3))
            self.draw_text(display, f"Level: {self.level}", topleft=(5, 3))
