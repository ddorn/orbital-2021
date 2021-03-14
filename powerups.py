from typing import Callable, TYPE_CHECKING

import pygame

from objects import Bar

if TYPE_CHECKING:
    from states.game import GameState

from locals import Color, Config, Paths, sprite, sprite_sheet

POWERUPS = []


class Powerup:
    SIZE = 50

    def __init__(self, name, descr, color, img_idx, effect):
        self.name = name
        self.descr = descr
        self.color = color
        self.img = sprite(img_idx, 5)
        self.apply = effect  # type: Callable[[GameState], None]

    def draw(self, display, center):
        r = self.img.get_rect(center=center)
        display.blit(self.img, r)

        # r = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        # r.center = center
        # pygame.draw.rect(display, self.color, r, 2, 4)

        return r


def make_powerup(name, descr, color, img_path):
    def wrapper(effect):
        p = Powerup(name, descr, color, img_path, effect)
        POWERUPS.append(p)
        return p

    return wrapper


bad = Color.ORANGE
very_bad = 'red'
good = Color.GREEN


@make_powerup(
    "Life up",
    "Soon even cats will be jalous !",
    good, 0,
)
def life_up(game: "GameState"):
    game.lives += 2


@make_powerup(
    'Bigger bar',
    'Size does matter sometimes...',
    good, 2,
)
def bigger_bar(game):
    for bar in game.get_all(Bar):
        bar.size.x += Bar.START_SIZE[0] / 2
@make_powerup(
    'Smalled bar',
    'A small bar teaches you to be more precise...',
    bad, 6,
)
def smaller_bar(game):
    for bar in game.get_all(Bar):
        bar.size.x *= 0.8


@make_powerup(
    'Speed up',
    "Turn into a wasp on steroids, one km/h at a time.",
    good, 1,
)
def speed_up(game):
    for bar in game.get_all(Bar):
        bar.velocity += 1


@make_powerup(
    'Speed down',
    "Good luck caching up with the balls !",
    bad, 4,
)
def speed_up(game):
    for bar in game.get_all(Bar):
        bar.velocity += 1


@make_powerup(
    'Stronger bricks',
    'All brick go to workout and need one more hit to pop.',
    bad, 3,
)
def stronger_bricks(game):
    Config().brick_life += 1