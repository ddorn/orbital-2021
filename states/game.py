from random import random, shuffle

import pygame

from core import App, State
from locals import Color, Config, get_level_surf
from objects import Bar, Bricks, Ball, Particle
from powerups import auto_ball_spawn, enemy_fire, POWERUPS, wind
from states.gameover import GameOverState
from states.pickpowerup import PickPowerUpState

pygame.init()


class Data:
    brick_life = 1


class GameState(State):
    BG_COLOR = Color.DARKEST
    BG_MUSIC = 'ambience.wav'
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
        self.bricks = self.add(Bricks.load(self.level_size, 0))
        self.add(self.bar.spawn_ball())

        auto_ball_spawn.apply(self)

    @property
    def level_size(self):
        return self.w, self.h - 40

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
        if not self.bricks.alive:
            # We would like it to be after the line alive=False,
            # but then modifications of powerups would not apply directly
            self.bricks = self.add(Bricks.random(self.level_size))

        super().logic()
        config = Config()
        config.logic()

        # No more balls, spawn one, loose life
        if not list(self.get_all(Ball)):
            self.add(self.bar.spawn_ball())
            self.loose_life()

        if config.wind:
            speed = config.wind_speed
            if speed and random() < abs(speed) / 3 / 10:
                self.add(Particle.wind_particle())

        if config.spawn_ball():
            self.add(self.bar.spawn_ball())

        if len(self.bricks) < 3:
            self.level += 1
            shuffle(POWERUPS)
            pows = POWERUPS[:3]
            self.next_state = PickPowerUpState(self, pows)
            self.bricks.alive = False

        if self.lives <= 0:
            self.next_state = GameOverState(self.size, self.level, self.score)

    def draw(self, display):
        super(GameState, self).draw(display)

        self.draw_text(display, f"Score: {self.score}", topright=(self.w - 5, 3))
        self.draw_text(display, f"Level: {self.level}", topleft=(5, 3))
        self.draw_text(display, "<3" * self.lives, Color.ORANGE, midtop=(self.w / 2, 3))

        display.blit(get_level_surf(0), (0, 0))

    def loose_life(self):
        self.lives -= 1
        self.do_shake(12)
