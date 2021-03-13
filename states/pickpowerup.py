from typing import List

import pygame

from core import State
from locals import Color
from powerups import Powerup


class PickPowerUpState(State):
    bg_color = None

    def __init__(self, game_state, powerups: List[Powerup]):
        super(PickPowerUpState, self).__init__(game_state.size)
        self.game_state = game_state
        self.powerups = powerups
        self.selected = 0

    def on_key_down(self, event):
        if event.key == pygame.K_SPACE:
            # Avoid using multiple times a powerup
            if self.next_state == self:
                powerup = self.powerups[self.selected]
                powerup.apply(self.game_state)
                self.next_state = self.game_state
                self.game_state.next_state = self.game_state
        elif event.key == pygame.K_LEFT:
            self.selected -= 1
        elif event.key == pygame.K_RIGHT:
            self.selected += 1
        self.selected %= len(self.powerups)

    def draw(self, display):
        start = self.w * 0.2
        spacing = self.w * 0.6 / (len(self.powerups) - 1)
        y = self.h * 0.6
        for i, powerup in enumerate(self.powerups):
            x = start + spacing * i
            r = powerup.draw(display, (x, y))

            if i == self.selected:
                color = powerup.color
                pygame.draw.rect(display, Color.DARKEST, (0, self.h - 100, self.w, 50))
                self.draw_text(display, powerup.descr, Color.BRIGHT, midbottom=(self.w / 2, self.h - 50))
            else:
                color = Color.BRIGHT
            self.draw_text(display, powerup.name, color, midtop=r.midbottom)
