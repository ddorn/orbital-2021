from pathlib import Path

import pygame


def clamp(x, mini, maxi):
    if x < mini:
        return mini
    if x > maxi:
        return maxi
    return x


def polar(r, phi):
    """Return a 2D vector with the given polar coordinates. The angle is in degrees."""

    vec = pygame.Vector2()
    vec.from_polar((r, phi))
    return vec


class Color:
    ORANGE = "#ffa500"
    DARKEST = "#331727"
    DARK = "#440a67"
    MIDDLE = '#93329e'
    BRIGHT = '#b4aee8'
    BRIGHTEST = '#ffe3fe'


class Paths:
    TOP = Path(__file__).parent
    ASSETS = TOP / "assets"
    FONT = ASSETS / "fonts" / "ThaleahFat.ttf"

