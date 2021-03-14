import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from random import gauss, random, uniform

import pygame

DEBUG = 0
VOLUME = {
    'BG_MUSIC': 0.8,
    'bong': 1,
    'hit': 1,
}


def clamp(x, mini=0, maxi=1):
    if x < mini:
        return mini
    if x > maxi:
        return maxi
    return x


def ease(x, mini=0.0, maxi=1.0):
    x = clamp(x, mini, maxi)
    x = (x - mini) / (maxi - mini)
    return x ** 2 * (3 - 2 * x)


def weighted_choice(items, count=1):
    items = list(items)
    print(count, len(items))
    count = min(count, len(items))

    choice = []
    for _ in range(count):
        cum = []
        p = 0
        for (item, proba) in items:
            p += proba
            cum.append((item, p))
        cut = uniform(0, p)
        for i, (item, p) in enumerate(cum):
            if p > cut:
                choice.append(item)
                items.pop(i)
                break

    if count == 1:
        return choice[0]
    return choice


def polar(r, phi):
    """Return a 2D vector with the given polar coordinates. The angle is in degrees."""

    vec = pygame.Vector2()
    vec.from_polar((r, phi))
    return vec


def vec2int(vec):
    return int(round(vec[0])), int(round(vec[1]))


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
def _get_sound(name):
    return pygame.mixer.Sound(Files.SOUNDS / (name + '.wav'))


def get_sound(name):
    sound = _get_sound(name)
    sound.set_volume(VOLUME.get(name, 1) * Settings().sfx)
    return sound


@lru_cache()
def get_level_surf(idx):
    x = idx % 4
    y = idx // 4
    return get_img(Files.LEVELS).subsurface(x * 16, y * 16, 16, 16)


@lru_cache()
def get_font(size):
    return pygame.font.Font(Files.FONT, size)


@lru_cache(maxsize=100)
def get_text(txt, color, size):
    if color is None:
        color = Color.BRIGHTEST
    # noinspection PyTypeChecker
    return get_font(size * round(Config().zoom)).render(str(txt), 1, color)


def draw_text(surf, txt, color=None, size=32, **anchor):
    assert len(anchor) == 1
    tmp_surf = get_text(txt, color, size)
    rect = tmp_surf.get_rect(**anchor)
    surf.blit(tmp_surf, rect)
    return rect


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

        self.flip_controls = False

        self.mouse_control = False
        self.ball_speed = 7
        self.brick_life = 1

        self.bricks_levels = defaultdict(int)

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

    @property
    def zoom(self):

        from core import App
        zoom = min(self.w / App.SIZE[0], self.h / App.SIZE[1])
        return zoom

    def scale(self, *size):
        return self.zoom * pygame.Vector2(*size)

    def iscale(self, value: int):
        return round(self.zoom * value)

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
                    self._wind_speed_goal = gauss(3, 0.2) * direction  # px/frame
                    self._wind_end = self.timer + gauss(60 * 3, 30)  # 3s ± 0.5s
                    get_sound('wind').play()
                else:  # const -> down
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
        if self.ball_spawn_level and self.timer > self._last_ball_spawn + 60 * 60 / (1 + self.ball_spawn_level):
            self._last_ball_spawn = self.timer
            return True
        return False


class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is not None:
            return cls._instance
        self = super(Settings, cls).__new__(cls)
        cls._instance = self

        self.reset()
        self.load()
        return self

    def reset(self):
        self.music = 1
        self.sfx = 1

        # Stats
        self.games = 0
        self.highscore = 0
        self.total_score = 0
        self.explosions = 0
        self.balls_lost = 0
        self.time_played = 0

    def load(self):
        if Files.SETTINGS.exists():
            self.__dict__.update(json.loads(Files.SETTINGS.read_text()))

    def save(self):
        s = json.dumps(self.__dict__)
        Files.SETTINGS.write_text(s)
        print(self.__dict__)


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
    SETTINGS = TOP / 'settings.json'
