from functools import lru_cache
from pathlib import Path

import pygame


def clamp(x, mini, maxi):
    if x < mini:
        return mini
    if x > maxi:
        return maxi
    return x

def ease(x):
    x = clamp(x, 0, 1)
    return x ** 2 * (3 - 2*x)


def polar(r, phi):
    """Return a 2D vector with the given polar coordinates. The angle is in degrees."""

    vec = pygame.Vector2()
    vec.from_polar((r, phi))
    return vec


@lru_cache
def sprite_sheet():
    return pygame.image.load(Paths.SPRITE_SHEET)

@lru_cache()
def sprite(idx, scale=2):
    S = 16
    x = idx % 4
    y = idx // 4
    img = sprite_sheet().subsurface(x * S, y * S, S, S)
    if scale > 1:
        img = pygame.transform.scale(img, (S * scale, S * scale))
    return img

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is not None:
            return cls._instance
        self = super(Config, cls).__new__(cls)
        cls._instance = self

        self.reset()
        return self

    def reset(self):
        self.brick_life = 1


class Color:
    GREEN = "#7ED16F"
    ORANGE = "#ffa500"
    DARKEST = "#331727"
    DARK = "#440a67"
    MIDDLE = '#"93329e"'
    BRIGHT = '#b4aee8'
    BRIGHTEST = '#ffe3fe'


class Paths:
    TOP = Path(__file__).parent
    ASSETS = TOP / "assets"
    FONT = ASSETS / "fonts" / "ThaleahFat.ttf"
    SPRITE_SHEET = ASSETS / 'sprite_sheet.png'

