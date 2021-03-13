from typing import Callable, TYPE_CHECKING

import pygame

from objects import Bar

if TYPE_CHECKING:
    from states.game import GameState

from locals import Color


POWERUPS = []


class Powerup:
    SIZE = 50

    def __init__(self, name, descr, color, img_path, effect):
        self.name = name
        self.descr = descr
        self.color = color
        self.img_path = img_path
        self.apply = effect  # type: Callable[[GameState], None]

    def draw(self, display, center):
        r = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        r.center = center
        return pygame.draw.rect(display, self.color, r, 2, 4)



def make_powerup(name, descr, color, img_path):
    def wrapper(effect):
        p = Powerup(name, descr, color, img_path, effect)
        POWERUPS.append(p)
        return p

    return wrapper


@make_powerup(
    "Life up",
    "Soon even cats will be jalous !",
    'green',
    '',
)
def life_up(game: "GameState"):
    game.lives += 1


@make_powerup(
    'Bigger bar',
    'Size does matter sometimes...',
    'green',
    ''
)
def bigger_bar(game):
    for bar in game.get_all(Bar):
        bar.size.x += 25


@make_powerup(
    'Speed up',
    "Turn into a wasp on steroids, one km/h at a time.",
    "green",
    ''
)
def speed_up(game):
    for bar in game.get_all(Bar):
        bar.velocity += 1
