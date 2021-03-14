from random import random, shuffle

import pygame

from core import App, DEBUG, State
from locals import Color, Config, get_level_surf
from objects import BackgroundShape, Bar, Bricks, Ball, Particle
from powerups import auto_ball_spawn, brick, enemy_fire, god_like, POWERUPS, random_powerup, very_bad, wind
from states.gameover import GameOverState
from states.pickpowerup import PickPowerUpState

pygame.init()



class GameState(State):
    BG_COLOR = Color.DARKEST
    BG_MUSIC = 'ambience.wav'
    BG_SHAPES = 10
    BALL_SPEED_GAIN = 0.5
    _INSTANCE = None

    def __init__(self, size):
        super().__init__(size)

        Config().reset()

        self.score = 0
        self.level = 0
        self.lives = 3

        self.powerups = []
        self.score_level = 0

        GameState._INSTANCE = self

        self.bar = self.add(Bar(self.h - 30))
        self.bricks = self.add(Bricks.load(self.level_size, 0))
        self.add(self.bar.spawn_ball())

        for _ in range(self.BG_SHAPES):
            self.add(BackgroundShape.random())

    def score_for_next_powerup(self):
        if self.score_level == 0:
            return 10
        return 40 * self.score_level

    @property
    def level_size(self):
        return self.w, self.h - 100

    def handle_event(self, event):
        super(GameState, self).handle_event(event)

        if event.type == pygame.KEYDOWN:
            key = event.key
            if DEBUG:
                if key == pygame.K_SPACE:
                    self.add(self.bar.spawn_ball())
                elif key == pygame.K_n:
                    self.end_level()

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

        if self.score > self.score_for_next_powerup():
            self.get_powerup()

        if config.wind:
            speed = config.wind_speed
            if speed and random() < abs(speed) / 3 / 10:
                self.add(Particle.wind_particle())

        if config.spawn_ball():
            self.add(self.bar.spawn_ball())

        if len(self.bricks) < 3:
            self.end_level()

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

    def end_level(self):
        self.level += 1
        Config().ball_speed += self.BALL_SPEED_GAIN
        kind = {
            1: brick,
            2: very_bad,
            3: god_like,
        }.get(self.level)
        pows = random_powerup(3, kind) if kind else random_powerup(3)

        self.next_state = PickPowerUpState(self, pows)
        self.bricks.alive = False

    def get_powerup(self):
        self.score_level += 1
        pows = random_powerup(3)
        self.next_state = PickPowerUpState(self, pows)