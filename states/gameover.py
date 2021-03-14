from typing import List

import pygame

from core import State
from locals import Color, Config, settings
from powerups import Powerup


class GameOverState(State):
    LINE_SIZE = 7
    def __init__(self, level, score, powerups):
        super().__init__()

        if score > settings.highscore:
            settings.highscore = score
        self.timer = 0
        self.level = level
        self.score = score
        self.powerups: List[Powerup] = powerups

    def on_key_down(self, event):
        if event.key == pygame.K_SPACE:
            from states.game import GameState
            from states.pickpowerup import PickPowerUpState
            self.next_state = PickPowerUpState(GameState())

    def logic(self):
        super(GameOverState, self).logic()
        self.timer += 1

    def draw(self, display):
        super().draw(display)

        for i, p in enumerate(self.powerups):
            pos = self.pos_of(i)
            p.draw(display, pos)

        self.draw_text(display, f"Score: {self.score}", topright=(self.w - 5, 3))
        self.draw_text(display, f"Level: {self.level}", topleft=(5, 3))

        if self.timer % 120 > 15:
            r = self.draw_text(display, "GAME OVER", Color.ORANGE, 64, center=self.size / 2)
            self.draw_text(display, "Press SPACE to restart", Color.BRIGHT, midtop=r.midbottom)

    def pos_of(self, idx):
        x = idx % self.LINE_SIZE
        y = idx // self.LINE_SIZE

        line = min(self.LINE_SIZE, len(self.powerups) - y * self.LINE_SIZE)

        w, h = Config().size
        x = (w / 9) * (5 - line / 2 + x)
        y = 0.2 * h + (w/9) * y

        return x, y

