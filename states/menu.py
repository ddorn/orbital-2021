from math import ceil, pi, sin
from random import random, uniform

import pygame
import pygame.gfxdraw

from core import State
from locals import Color, Config, config, get_text, rrange
from objects import BackgroundShape, Particle
from states.game import GameState
from states.statistics import StatisticsState


class MenuState(State):
    def __init__(self):
        super().__init__()

        self.timer = 0
        self.buttons = {
            "Play": GameState,
            "Settings": MenuState,
            "Highscores": MenuState,
            "Statistics": StatisticsState,
            "Quit": None
        }
        self.selected = 0
        self.play_button_center = (0, 0)

        for _ in range(15):
            self.add(BackgroundShape.random())

    def on_key_down(self, event):
        if event.key == pygame.K_DOWN:
            self.selected += 1
        elif event.key == pygame.K_UP:
            self.selected -= 1
        elif event.key == pygame.K_SPACE:
            self.go_next()

        self.selected %= len(self.buttons)

    def go_next(self):
        key = list(self.buttons)[self.selected]
        state = self.buttons[key]
        if state is not None:
            state = state()
        self.next_state = state

    def logic(self):
        super().logic()

        self.timer += 1


        if self.timer == 1:
            return

        for _ in rrange(min(3, self.timer / 100)):
            self.add(Particle.from_edges(self.play_button_center))

    def draw(self, display):
        super().draw(display)

        pygame.gfxdraw.box(display, (self.w / 4, self.h / 3 * 0, self.w  / 2, self.h ), (0, 0, 0, 80))

        center = self.w / 2, self.h * 0.2
        t = self.timer / 40
        # r = self.draw_text(display, "Violet", Color.GOLD, 80, midtop=midtop)
        s = get_text("Violet", Color.GOLD, config.iscale(90 * (1 + 0.10 * (sin(2.5*t)))))
        s = pygame.transform.rotate(s, 5*sin(t*pi))
        r = s.get_rect(center=center)
        display.blit(s, r)

        # r.y += self.h * 0.15
        r.bottom = self.h * 0.4

        for i, text in enumerate(self.buttons):
            if i == self.selected:
                color = Color.GOLD
                if self.timer % 120 > 10:
                    text = f"> {text} <"
            else:
                color = Color.BRIGHTEST

            if i == 0:
                size = 60
                # color = Color.VIVID
            else:
                size = 50

            r = self.draw_text(display, text, color, size, midtop=r.midbottom)

            if i == 0:
                self.play_button_center = r.center
                r.y -= 5
                pygame.draw.line(display, color, r.bottomleft, r.bottomright)
                r.y += 25