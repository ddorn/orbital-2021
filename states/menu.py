from random import random, uniform

import pygame
import pygame.gfxdraw

from core import State
from locals import Color, Config
from objects import BackgroundShape, Particle
from states.game import GameState


class MenuState(State):
    def __init__(self):
        super().__init__()

        self.timer = 0
        self.buttons = {
            "Play": GameState,
            "Settings": MenuState,
            "Highscore": MenuState,
            "Statistics": MenuState,
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

        for _ in range(3):
            x = uniform(0, self.w)
            y = uniform(0, self.h)

            if random() < 0.5:
                x = 0 if random() < 0.5 else self.w
            else:
                y = 0 if random() < 0.5 else self.h

            center = pygame.Vector2(self.play_button_center)
            path = center - (x, y)
            lifespan = 80
            vel = path / lifespan / Config().zoom


            self.add(Particle((x, y) - vel * 3, vel, lifespan, 0.97, decay_velocity=False))

    def draw(self, display):
        super().draw(display)

        pygame.gfxdraw.box(display, (self.w / 4, self.h / 3 * 0, self.w  / 2, self.h ), (0, 0, 0, 80))

        r = self.draw_text(display, "Violet", Color.GOLD, 80, midtop=(self.w / 2, self.h * 0.1))
        r.y += self.h * 0.15

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