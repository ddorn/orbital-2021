from pathlib import Path


def clamp(x, mini, maxi):
    if x < mini:
        return mini
    if x > maxi:
        return maxi
    return x


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

