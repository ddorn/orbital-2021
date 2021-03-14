from dataclasses import dataclass
from random import choice, shuffle, uniform
from typing import Callable, TYPE_CHECKING

from objects import Bar

if TYPE_CHECKING:
    from states.game import GameState

from locals import Color, Config, sprite, weighted_choice

POWERUPS = []


class Powerup:
    SIZE = 50

    def __init__(self, name, descr, kind, img_idx, effect):
        self.name = name
        self.descr = descr
        self.kind = kind
        self.img = sprite(img_idx, 5)
        self.apply = effect  # type: Callable[[GameState], None]

    @property
    def color(self):
        return self.kind.color

    def draw(self, display, center):
        r = self.img.get_rect(center=center)
        display.blit(self.img, r)

        # r = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        # r.center = center
        # pygame.draw.rect(display, self.kind, r, 2, 4)

        return r


def make_powerup(name, descr, kind, img_idx):
    def wrapper(effect):
        p = Powerup(name, descr, kind, img_idx, effect)
        POWERUPS.append(p)
        return p

    return wrapper


@dataclass
class Kind:
    color: str
    proba: int

very_bad = Kind('red', 1)
god_like = Kind(Color.GOLD, 1)
bad = Kind(Color.ORANGE, 5)
good = Kind(Color.GREEN, 4)
brick = Kind(Color.MIDDLE, 1)

KINDS = [
    bad, very_bad, good, god_like, brick
]

def random_kind():
    return weighted_choice([(k, k.proba) for k in KINDS])

def random_powerup(maxi=3, *kinds):
    if not kinds:
        kinds = KINDS
    pows = [(p, p.kind.proba) for p in POWERUPS if p.kind in kinds]
    print(kinds, pows)
    return weighted_choice(pows, maxi)


@make_powerup("Life up", "Soon even cats will be jalous !", good, 0, )
def life_up(game: "GameState"):
    game.lives += 1


@make_powerup('Bigger bar', 'Size does matter sometimes...', good, 2, )
def bigger_bar(game):
    for bar in game.get_all(Bar):
        bar.size.x += Bar.START_SIZE[0] / 2


@make_powerup('Smaller bar', 'A small bar teaches you to be more precise...', bad, 6, )
def smaller_bar(game):
    for bar in game.get_all(Bar):
        bar.size.x *= 0.8


@make_powerup('Speed up', "Turn into a wasp on steroids, one km/h at a time.", good, 1, )
def speed_up(game):
    for bar in game.get_all(Bar):
        bar.velocity += 2


@make_powerup('Speed down', "Good luck caching up with the balls !", bad, 4, )
def speed_down(game):
    for bar in game.get_all(Bar):
        bar.velocity -= 0.5


@make_powerup('Stronger bricks', 'All brick go to workout and need one more hit to pop.', very_bad, 3, )
def stronger_bricks(game):
    Config().brick_life += 1


@make_powerup('Wind', 'Wooooosh', very_bad, 5)
def wind(game):
    Config().wind = True


@make_powerup('American bricks', 'Gun control is inefficient... take cover !', very_bad, 7)
def enemy_fire(game):
    Config().brick_fire_probability += 1


@make_powerup('Ball spawn', 'Get a new ball every sometimes', god_like, 8)
def auto_ball_spawn(game):
    Config().ball_spawn_level += 1

@make_powerup('Mouse control', 'A good cat plays with the mouse', god_like, 9)
def mouse_control(game):
    Config().mouse_control = True

@make_powerup('Clone brick', 'Spawn a new ball when broken', brick, 12)
def clone_brick(game):
    Config().bricks.add(10)

@make_powerup('Explosive bricks', 'BOOOOOM', brick, 13)
def explosive_bricks(game):
    Config().bricks.add(12)

@make_powerup('Mirror', "You have two left hands but swapping controls won't help", very_bad, 14)
def flip_controls(game):
    Config().flip_controls = not Config().flip_controls


