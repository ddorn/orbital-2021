from pathlib import Path


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

