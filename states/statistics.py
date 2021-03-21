from math import ceil, sin
from random import random, uniform

import pygame
import pygame.gfxdraw

from core import State
from locals import Color, Config, config, get_text, rrange, settings
from objects import BackgroundShape, Particle
from states.game import GameState


class StatisticsState(State):
    def __init__(self):
        super().__init__()

        self.timer = 0
        self.stats = [
            'games',
            'highscore',
            'total_score',
            'explosions',
            'bricks_destroyed',
            'balls_lost',
            'bullet_hit',
            'minutes_played',
            'powerups',
        ]

        for _ in range(15):
            self.add(BackgroundShape.random())

    def on_key_down(self, event):
        if event.key == pygame.K_SPACE:
            from states.menu import MenuState
            self.next_state = MenuState()


    def logic(self):
        super().logic()

        self.timer += 1


        if self.timer == 1:
            return

        for _ in rrange(min(3, self.timer / 100)):
            self.add(Particle.from_edges(self.size / 2))

    def draw(self, display):
        super().draw(display)

        pygame.gfxdraw.box(display, (self.w / 6, self.h / 3 * 0, self.w * 4 / 6, self.h ), (0, 0, 0, 100))

        center = self.w / 2, self.h * 0.15
        r = self.draw_text(display, "Statistics", Color.GOLD, 80, center=center)
        r.bottom = self.h * 0.3
        r.right = self.w * 0.55

        stats = {
            name.replace('_', ' '): str(round(getattr(settings, name)))
            for name in self.stats
        }
        # name_length = max(map(len, stats))
        # value_length = max(map(len, stats.values()))
        font_size = 32
        for name, value in stats.items():
            # text = f'{name:>{name_length}}: {value:>{value_length}}'

            self.draw_text(display, f"  {value}", Color.VIVID, font_size, topleft=r.bottomright)
            r = self.draw_text(display, f"{name}:", Color.BRIGHTEST, font_size, topright=r.bottomright)

