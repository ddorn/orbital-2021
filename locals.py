from functools import lru_cache
from pathlib import Path
from random import gauss, random

import pygame

DEBUG = 1
VOLUME = {
    'BG_MUSIC': 0.8,
    'bong': 1,
    'hit': 1,
}


def clamp(x, mini, maxi):
    if x < mini:
        return mini
    if x > maxi:
        return maxi
    return x

def ease(x, mini=0.0, maxi=1.0):
    x = clamp(x, mini, maxi)
    x = (x - mini) / (maxi - mini)
    return x ** 2 * (3 - 2*x)


def polar(r, phi):
    """Return a 2D vector with the given polar coordinates. The angle is in degrees."""

    vec = pygame.Vector2()
    vec.from_polar((r, phi))
    return vec


@lru_cache()
def get_img(path):
    return pygame.image.load(path)


@lru_cache()
def sprite(idx, scale=2):
    S = 16
    x = idx % 4
    y = idx // 4
    img = get_img(Files.SPRITE_SHEET).subsurface(x * S, y * S, S, S)
    if scale > 1:
        img = pygame.transform.scale(img, (S * scale, S * scale))
    return img


@lru_cache()
def get_sound(name):
    sound = pygame.mixer.Sound(Files.SOUNDS / (name + '.wav'))
    sound.set_volume(VOLUME.get(name, 1))
    return sound

@lru_cache()
def get_level_surf(idx):
    x = idx % 4
    y = idx // 4
    return get_img(Files.LEVELS).subsurface(x * 16, y * 16, 16, 16)


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is not None:
            return cls._instance
        self = super(Config, cls).__new__(cls)
        cls._instance = self

        self.size = (0, 0)  # Set by App, we don't want it to be reset on new levels
        self.reset()
        return self

    def reset(self):
        self.timer = 0

        self.mouse_control = 1
        self.ball_speed = 7
        self.brick_life = 1


        self.bricks = {10, 12} if DEBUG else set()

        self.wind = False
        self.wind_speed = 0
        self._wind_speed_goal = 0
        self._wind_end = 0
        self._wind_start = 0
        self._wind_phase = 'const'

        self.brick_fire_probability = 0
        self._last_fire = 0

        self.ball_spawn_level = 0
        self._last_ball_spawn = -9999

    @property
    def w(self):
        return self.size[0]
    @property
    def h(self):
        return self.size[1]

    def logic(self):
        self.timer += 1

        # Wind
        if self.wind:
            if self.wind_speed != self._wind_speed_goal:
                self.wind_speed = ease(self.timer, self._wind_start, self._wind_end) * self._wind_speed_goal
            elif self._wind_end <= self.timer:
                if self._wind_phase == 'up':
                    self._wind_end = self.timer + gauss(60 * 6, 60)  # 6s ± 1s
                    self._wind_phase = 'const'
                elif self._wind_phase == 'down':
                    self._wind_end = self.timer + gauss(60 * 20, 60 * 3)  # 20s ± 3s
                    self._wind_speed_goal = 0
                    self.wind_speed = 0
                    self._wind_phase = 'const'
                elif self._wind_speed_goal == 0:  # const -> up
                    self._wind_phase = 'up'
                    direction = (random() > 0.5) * 2 - 1
                    self._wind_speed_goal = gauss(3, 0.2) * direction   # px/frame
                    self._wind_end = self.timer + gauss(60 * 3, 30)  # 3s ± 0.5s
                    get_sound('wind').play()
                else: # const -> down
                    self._wind_phase = 'down'
                    self._wind_speed_goal = 0
                    self._wind_end = self.timer + gauss(60 * 3, 30)  # 3s ± 0.5s
                    get_sound('wind').fadeout(int((self.timer - self._wind_end) / 60 * 1000))

    def fire(self):
        if not self.brick_fire_probability:
            return False

        if self.timer - self._last_fire < 60 * 3 * 1 / self.brick_fire_probability:
            return False
        t = random() < 0.001
        if t:
            self._last_fire = self.timer
        return t

    def spawn_ball(self):
        # Spawn every 60s / level
        if self.ball_spawn_level and self.timer > self._last_ball_spawn + 60*60 / (1 + self.ball_spawn_level):
            self._last_ball_spawn = self.timer
            return True
        return False


class Color:
    GOLD = "#FFD700"
    GREEN = "#7ED16F"
    ORANGE = "#ffa500"
    DARKEST = "#331727"
    DARK = "#440a67"
    MIDDLE = '#93329e'
    BRIGHT = '#b4aee8'
    BRIGHTEST = '#ffe3fe'


class Files:
    TOP = Path(__file__).parent
    ASSETS = TOP / "assets"
    FONT = ASSETS / "fonts" / "ThaleahFat.ttf"
    SPRITE_SHEET = ASSETS / 'sprite_sheet.png'
    LEVELS = ASSETS / "levels.png"
    SOUNDS = ASSETS / 'sounds'

