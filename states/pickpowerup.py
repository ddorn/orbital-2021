from typing import List

import pygame

from core import State
from locals import clamp, Color, ease
from powerups import Powerup


class PickPowerUpState(State):
    bg_color = None

    def __init__(self, game_state, powerups: List[Powerup]):
        super(PickPowerUpState, self).__init__(game_state.size)
        self.game_state = game_state
        self.powerups = powerups
        self._selected = 0
        self.selected_at = 0
        self.last_selected = None
        self.timer = 0

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        value %= len(self.powerups)
        if value != self._selected:
            self.last_selected = self._selected
            self._selected = value
            self.selected_at = self.timer

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

    def logic(self):
        super().logic()
        self.timer += 1

    def draw(self, display):
        self.game_state.draw(display)

        start = self.w * 0.2
        spacing = self.w * 0.6 / (len(self.powerups) - 1)
        y = self.h * 0.6
        displacement = ease((self.timer - self.selected_at) / 15) * 50
        for i, powerup in enumerate(self.powerups):
            if i == self.selected:
                dy = displacement
                pygame.draw.rect(display, Color.DARKEST, (0, self.h - 100, self.w, 50))
                self.draw_text(display, powerup.descr, Color.BRIGHT, midbottom=(self.w / 2, self.h - 50))
            elif i == self.last_selected:
                dy = 50 - displacement
            else:
                dy = 0

            x = start + spacing * i
            r = powerup.draw(display, (x, y - dy))

            color = powerup.color
            r = self.draw_text(display, powerup.name, color, midtop=r.midbottom)
            if i == self.selected:
                pygame.draw.line(display, color, r.bottomleft, r.bottomright)


