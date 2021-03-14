from random import random, shuffle

import pygame

from core import App, State
from locals import Color, Config
from objects import Bar, Bricks, Ball, Particle
from powerups import POWERUPS, wind
from states.gameover import GameOverState
from states.pickpowerup import PickPowerUpState

pygame.init()


class Data:
    brick_life = 1


class GameState(State):
    BG_COLOR = Color.DARKEST
    _INSTANCE = None

    def __init__(self, size):
        super().__init__(size)

        Config().reset()

        self.score = 0
        self.level = 0
        self.lives = 3

        self.data = Data()
        GameState._INSTANCE = self

        self.bar = self.add(Bar(self.h - 30))
        self.bricks = self.add(Bricks(15, 15, (self.w, self.h - 100)))
        self.add(self.bar.spawn_ball())

    @classmethod
    def data(cls):
        if cls._INSTANCE:
            return cls._INSTANCE.data
        return Data()

    def handle_event(self, event):
        super(GameState, self).handle_event(event)

        if event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_SPACE:
                self.add(self.bar.spawn_ball())

    def logic(self):
        super().logic()
        config = Config()
        config.logic()

        if not list(self.get_all(Ball)):
            # No more balls, spawn one
            self.add(self.bar.spawn_ball())
            self.lives -= 1

        if config.wind:
            speed = config.wind_speed
            if speed and random() < abs(speed) / 3 / 10:
                self.add(Particle.wind_particle())

        if len(self.bricks) < 3:
            shuffle(POWERUPS)
            pows = POWERUPS[:3]
            self.next_state = PickPowerUpState(self, pows)
            self.bricks.alive = False
            self.bricks = self.add(Bricks(17, 17, (self.w, self.h - 40)))

        if self.lives <= 0:
            self.next_state = GameOverState(self.size, self.level, self.score)

    def draw(self, display):
        super(GameState, self).draw(display)

        self.draw_text(display, f"Score: {self.score}", topright=(self.w - 5, 3))
        self.draw_text(display, f"Level: {self.level}", topleft=(5, 3))
        self.draw_text(display, "<3" * self.lives, Color.ORANGE, midtop=(self.w / 2, 3))
