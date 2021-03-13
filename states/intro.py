from random import gauss, uniform

import pygame

from core import State
from locals import Color, polar
from objects import Bar, Particle
from states.game import GameState


class IntroState(State):
    BG_COLOR = Color.DARKEST

    def __init__(self, size):
        super().__init__(size)

        self.ended = False
        self.timer = 0
        self.text ="Use the arrow keys to move"
        self.add(Bar(self.h - 50))

    def logic(self):
        super(IntroState, self).logic()

        self.timer += 1

        if self.timer == 60 * 4:
            self.text = "Press SPACE to start"
            for _ in range(20):
                self.add(Particle(
                    self.size / 2,
                    polar(gauss(15, 2), uniform(0, 360)),
                    20
                ))

        if self.ended:
            return GameState(self.size)
        return self

    def handle_event(self, event):
        super(IntroState, self).handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.ended = True

    def draw(self, display):
        super(IntroState, self).draw(display)

        if self.timer % 60 > 10:
            self.draw_text(display, self.text, center=self.size / 2)
