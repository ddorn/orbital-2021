from random import random

import pygame

from core import DEBUG, State
from locals import Color, Config, get_level_surf, settings
from objects import BackgroundShape, Ball, Bar, Bricks, Particle
from powerups import brick, god_like, very_bad
from states.gameover import GameOverState
from states.pause import PauseState
from states.pickpowerup import PickPowerUpState

pygame.init()


class GameState(State):
    BG_COLOR = Color.DARKEST
    BG_MUSIC = 'ambience.wav'
    BG_SHAPES = 10
    BALL_SPEED_GAIN = 0.2

    def __init__(self):
        super().__init__()

        Config().reset()
        settings.games += 1

        self.score = 0
        self.level = 0
        self.lives = 3

        self.powerups = []
        self.score_level = 0

        self.bar = self.add(Bar(self.h - 30))
        self.bricks = self.add(Bricks.load(0))
        self.add(self.bar.spawn_ball())

        for _ in range(self.BG_SHAPES):
            self.add(BackgroundShape.random())

    @property
    def level_size(self):
        return self.w, self.h - 100

    def on_key_down(self, event):
        key = event.key
        if DEBUG:
            if key == pygame.K_SPACE:
                self.add(self.bar.spawn_ball())
                return
            elif key == pygame.K_n:
                self.end_level()

        if key in (pygame.K_p, pygame.K_SPACE):
            self.next_state = PauseState(self)

    def logic(self):
        if not self.bricks.alive:
            # We would like it to be after the line alive=False,
            # but then modifications of powerups would not apply directly
            self.bricks = self.add(Bricks.random())

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
            self.next_state = GameOverState(self.level, self.score, self.powerups)

    def draw(self, display):
        super(GameState, self).draw(display)

        self.draw_text(display, f"Score: {self.score}", topright=(self.w - 5, 3))
        self.draw_text(display, f"Level: {self.level}", topleft=(5, 3))
        self.draw_text(display, "<3" * self.lives, Color.ORANGE, midtop=(self.w / 2, 3))

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

        self.next_state = PickPowerUpState(self, kind) if kind else PickPowerUpState(self)
        self.bricks.alive = False

    def get_powerup(self):
        self.score_level += 1
        self.next_state = PickPowerUpState(self)

    def score_for_next_powerup(self):
        return {
            0: 100,
            1: 250,
            2: 500
        }.get(self.score_level,
              500 * self.score_level * int(1 + self.score_level / 10)
              )

    def increase_score(self, hit=False):
        if hit:
            ds = 1
        else:  # Brick break
            bonus = sum(p.kind.value for p in self.powerups)
            if bonus > 0:
                bonus = -bonus // 2
            else:
                bonus = -bonus
            ds = max(10 + bonus, 2)
            if ds > 10:
                ds += ds - 10

        self.score += ds
        settings.total_score += ds
        return ds
