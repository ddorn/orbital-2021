from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING

from objects import Bar, BombBrick, Bricks, DoubleBrick

if TYPE_CHECKING:
    from states.game import GameState

from locals import Color, Config, sprite, weighted_choice

POWERUPS = []


class Powerup:
    SIZE = 50

    def __init__(self, name, descr, kind, img_idx, effect, limit=None):
        self.name = name
        self.descr = descr
        self.kind = kind
        self.img_idx = img_idx
        self.limit = limit
        self.effect = effect  # type: Callable[[GameState], None]

    def available(self, game_state):
        if self.limit is None:
            return True
        if callable(self.limit):
            return self.limit(game_state)
        return game_state.powerups.count(self) < self.limit

    def apply(self, game_state):
        if self.available(game_state):
            self.effect(game_state)
            game_state.powerups.append(self)

    @property
    def color(self):
        return self.kind.color

    def draw(self, display, center):
        img = sprite(self.img_idx, int(Config().zoom * 4))
        r = img.get_rect(center=center)
        display.blit(img, r)

        # r = pygame.Rect(0, 0, self.size, self.size)
        # r.center = center
        # pygame.draw.rect(display, self.kind, r, 2, 4)

        return r


def make_powerup(name, descr, kind, img_idx, **kwargs):
    def wrapper(effect):
        p = Powerup(name, descr, kind, img_idx, effect, **kwargs)
        POWERUPS.append(p)
        return p

    return wrapper


@dataclass
class Kind:
    color: str
    proba: int
    value: int  # How positive


very_bad = Kind('red', 1, -3)
god_like = Kind(Color.GOLD, 1, 3)
bad = Kind(Color.ORANGE, 6, -1)
good = Kind(Color.GREEN, 4, 1)
brick = Kind(Color.MIDDLE, 1, 3)

KINDS = [
    bad, very_bad, good, god_like, brick
]


def random_kind():
    return weighted_choice([(k, k.proba) for k in KINDS])


def random_powerup(maxi=3, *kinds, game):
    if not kinds:
        kinds = KINDS
    pows = [(p, p.kind.proba) for p in POWERUPS if p.kind in kinds and p.available(game)]
    choice =  weighted_choice(pows, maxi)
    if not choice:
        return [life_up]
    if not isinstance(choice, list):
        return [choice]
    return choice


@make_powerup("Life up", "I don't want to die !", good, 0)
def life_up(game: "GameState"):
    game.lives += 1

@make_powerup("<3 <3", "Soon even cats will be jalous !", god_like, 0)
def big_life_up(game: "GameState"):
    game.lives += 2


@make_powerup('Bigger bar', 'Size does matter sometimes...', good, 2,
              limit=lambda g: all(bar.size.x < Config().w / 4 for bar in g.get_all(Bar)))
def bigger_bar(game):
    for bar in game.get_all(Bar):
        bar.size.x += Bar.START_SIZE[0] / 2 * Config().zoom

@make_powerup('Huge bar', 'Size does matter sometimes...', god_like, 2,
              limit=lambda g: all(bar.size.x < Config().w / 4 for bar in g.get_all(Bar)))
def huger_bar(game):
    for bar in game.get_all(Bar):
        # 2 bigger bar
        bar.size.x += Bar.START_SIZE[0] * 1 * Config().zoom

@make_powerup('Smaller bar', 'A small bar teaches you to be more precise...', bad, 6,
              limit=lambda g: any(bar.size.x < Config().w / 12 for bar in g.get_all(Bar)))
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
    for bricks in game.get_all(Bricks):
        for b in bricks.all_bricks():
            b.life += 1


@make_powerup('Wind', 'Wooooosh', very_bad, 5, limit=1)
def wind(game):
    Config().wind = True


@make_powerup('American bricks', 'Gun control is inefficient... take cover !', very_bad, 7, limit=4)
def enemy_fire(game):
    Config().brick_fire_probability += 1


@make_powerup('Ball spawn', 'Get a new ball every sometimes', god_like, 8, limit=3)
def auto_ball_spawn(game):
    Config().ball_spawn_level += 1


@make_powerup('Mouse control', 'A good cat plays with the mouse', god_like, 9, limit=1)
def mouse_control(game):
    Config().mouse_control = True


@make_powerup('Clone brick', 'Spawn a new ball when broken', brick, 12, limit=4)
def clone_brick(game):
    Config().bricks_levels[DoubleBrick] += 1


@make_powerup('Explosive bricks', 'BOOOOOM', brick, 13, limit=4)
def explosive_bricks(game):
    Config().bricks_levels[BombBrick] += 2


@make_powerup('Mirror', "You have two left hands but swapping controls won't help", very_bad, 10)
def flip_controls(game):
    Config().flip_controls = not Config().flip_controls
