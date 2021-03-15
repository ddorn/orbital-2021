from math import sqrt
from random import choice, gauss, randrange, uniform
from typing import List, Union

import pygame

from core import App, Object
from locals import Color, clamp, Config, get_img, get_level_surf, get_sound, get_text, polar, settings, sprite

config = Config()
scale = config.scale


def draw_diamond(display, pos, vel, scale, color):
    dir = vel.normalize()
    cross = pygame.Vector2(-dir.y, dir.x)
    vertices = [
        pos + dir * scale,
        pos + cross * scale,
        pos - dir * scale * 3,
        pos - cross * scale,
    ]
    pygame.draw.polygon(display, color, vertices)


class Particle(Object):
    DIAMOND = 0
    LINE = 1
    Z = 1

    def __init__(self, pos, vel, lifespan, decay=0.95, size=2, color=Color.BRIGHTEST, shape=DIAMOND):
        super().__init__(pos, scale(size, size))
        self.vel = pygame.Vector2(vel) * Config().zoom
        self.lifespan = lifespan
        self.age = 0
        self.decay = decay
        self.shape = shape
        self.color = color

    def resize(self, old, new):
        super().resize(old, new)
        self.vel *= new.x / old.x

    def logic(self, state):
        self.age += 1
        if self.age > self.lifespan:
            self.alive = False
        self.pos += self.vel
        self.vel *= self.decay

    def draw(self, display):
        super(Particle, self).draw(display)

        r = 5 * self.decay ** self.age
        if self.shape == self.DIAMOND:
            draw_diamond(display, self.pos, self.vel, r, self.color)
        elif self.shape == self.LINE:
            pygame.draw.line(display, self.color, self.pos, self.pos + self.vel * 3, round(self.size.x))
        else:
            pygame.draw.circle(display, self.color, self.pos, self.size.y)

    @classmethod
    def wind_particle(cls):
        conf = Config()
        speed = conf.wind_speed
        if speed > 0:
            speed = max(1, speed)
            x = 0
        else:
            speed = min(-1, speed)
            x = conf.w
        y = uniform(0, conf.h)

        return Particle(
            (x, y), (speed * 5, 0), 9999, 1,
            size=randrange(1, 5),
            shape=Particle.LINE,
        )

    @classmethod
    def death_particles(cls, pos):
        return Particle(
            pos, polar(gauss(15, 3), uniform(0, 360)),
            20,
            color=Color.ORANGE,
        )


class TextParticle(Particle):
    def __init__(self, txt, pos, vel, lifespan=30, decay=1, size=32, color=Color.GOLD):
        super().__init__(pos, vel, lifespan, decay, color=color)
        self.txt = txt
        self.surf = get_text(txt, color, config.iscale(size))
        self.font_size = size

    def resize(self, old, new):
        super().resize(old, new)
        self.surf = get_text(self.txt, self.color, config.iscale(self.font_size))

    def logic(self, state):
        super().logic(state)

    def draw(self, display):
        r = self.surf.get_rect(center=self.pos)
        display.blit(self.surf, r)
        Object.draw(self, display)


class BackgroundShape(Object):
    Z = -1

    def __init__(self, pos, radius, color, shape=5):
        size = (radius * 2, radius * 2)
        super().__init__(pos, scale(size))

        self.color = color
        self.sides = shape
        self.angle = 0
        self.vel = polar(gauss(2, 0.5), uniform(0, 360))

    def logic(self, state):
        self.pos += self.vel
        self.angle += 2
        r = self.size.x
        w, h = Config().size
        if self.pos.x < -r and self.vel.x < 0:
            self.pos.x = w + r
        elif self.pos.x > w and self.vel.x > 0:
            self.pos.x = -r

        if self.pos.y < -r and self.vel.y < 0:
            self.pos.y = h + r
        elif self.pos.y > h and self.vel.y > 0:
            self.pos.y = -r

    def draw(self, display):
        super().draw(display)
        points = [
            self.rect.center + polar(self.size.x / 2, self.angle + 360 / self.sides * i)
            for i in range(self.sides)
        ]
        pygame.draw.polygon(display, self.color, points)

    @classmethod
    def random(cls):
        w, h = Config().size
        return cls((uniform(0, w), uniform(0, h)), gauss(30, 5), Color.DARK, randrange(3, 7))


class Bar(Object):
    START_SIZE = (75, 12)
    START_VELOCITY = 10
    K_LEFT = (pygame.K_LEFT, pygame.K_a, pygame.K_q)
    K_RIGHT = (pygame.K_RIGHT, pygame.K_d)

    def __init__(self, pos_y):
        x = Config().w / 2 - self.START_SIZE[0] / 2
        super().__init__((x, pos_y), Config().scale(self.START_SIZE))
        self.velocity = self.START_VELOCITY
        self.mouse_goal = None

    @property
    def flip(self):
        return -1 if Config().flip_controls else 1

    def handle_mouse_event(self, event):
        if Config().mouse_control:
            x, _ = event.pos
            if Config().flip_controls:
                x = Config().w - x
            self.mouse_goal = clamp(
                x - self.size.x / 2,
                0,
                Config().w - self.size.x
            )

    def logic(self, state):
        keys = pygame.key.get_pressed()
        if any(keys[k] for k in self.K_LEFT):
            self.mouse_goal = None
            self.pos.x -= self.velocity * self.flip * Config().zoom
        if any(keys[k] for k in self.K_RIGHT):
            self.mouse_goal = None
            self.pos.x += self.velocity * self.flip * Config().zoom

        if self.mouse_goal is not None:
            self.pos.x += clamp(self.mouse_goal - self.pos.x, -self.velocity * Config().zoom,
                                self.velocity * Config().zoom)

        self.pos.x += Config().wind_speed

        self.pos.x = clamp(
            self.pos.x,
            0,
            Config().w - self.size.x
        )

    def draw(self, display):
        display.fill(Color.BRIGHTEST, self)
        pygame.draw.rect(display, Color.BRIGHT, self.rect, 2)
        super().draw(display)

    def spawn_ball(self):
        return Ball(self.rect.center + pygame.Vector2(0, -30), -90)

    def resize(self, old, new):
        y = self.pos.y + new.y - old.y
        super().resize(old, new)
        self.pos.y = y


class Ball(Object):
    RADIUS = 10

    def __init__(self, center, angle=None):
        size = scale(self.RADIUS, self.RADIUS) * 2
        pos = center - size / 2
        super().__init__(pos, size)

        if angle is None:
            angle = gauss(-90, 10)
        self.vel = polar(1, angle)

    def logic(self, state):
        vel = self.vel * Config().ball_speed * Config().zoom
        if abs(vel.y) < 1:
            vel.y = 1 if vel.y > 0 else -1
        self.pos += vel
        self.pos.x += Config().wind_speed

        if self.pos.x < 0:
            self.pos.x = 0
            self.vel.x *= -1
        if self.pos.x > state.w - self.size.x:
            self.pos.x = state.w - self.size.x
            self.vel.x *= -1
        if self.pos.y < 0:
            self.pos.y = 0
            self.vel.y *= -1
        if self.pos.y > state.h:
            self.alive = False

        # Collision with bars
        if self.vel.y > 0:
            for bar in state.get_all(Bar):
                r = self.rect
                br: pygame.Rect = bar.rect
                if self.rect_collision(br) is not None:
                    dx = (r.centerx - br.centerx) / br.width * 2  # proportion on the side
                    dx = clamp(dx, -0.8, 0.8)

                    angle = (-dx + 1) * 90
                    self.vel.from_polar((1, -angle))

                    get_sound('bong').play()

        # Collision against bricks
        for bricks in state.get_all(Bricks):
            for brick in bricks.all_bricks():
                # TODO: only the bricks in the ball's rectangle
                if (n := self.rect_collision(brick.rect)) is not None:
                    vel_along_normal = n.dot(self.vel)
                    if vel_along_normal < 0:
                        continue  # Already separating
                    brick.hit(state)
                    # invert velocity along the normal
                    if brick.SOLID:
                        self.vel -= 2 * vel_along_normal * n

    def draw(self, display):
        super(Ball, self).draw(display)

        pygame.draw.circle(display, Color.BRIGHT, self.rect.center, self.size.x / 2)
        pygame.draw.circle(display, Color.BRIGHTEST, self.rect.center, self.size.x / 2 * 0.75)

    def rect_collision(self, rect):
        """Return the normal of the collision between a ball and a rect.

        Return None if there is no collision. The velocity of the ball """

        center = pygame.Vector2(self.rect.center)
        # Find the closest point to the circle within the rectangle
        closest = pygame.Vector2(
            clamp(center.x, rect.left, rect.right),
            clamp(center.y, rect.top, rect.bottom)
        )

        # Calculate the distance between the circle's center and self closest point
        d = center - closest

        # If the distance is less than the circle's radius, an intersection occurs
        norm2 = d.length_squared()
        if norm2 >= (self.size.x / 2) ** 2:  # .x == .y and is the diameter
            return None

        if closest == center:
            # Circle is inside the AABB, so we need to clamp the circle's center
            # to the closest edge

            left = center.x - rect.left
            top = center.y - rect.top
            right = rect.right - center.x
            bottom = rect.bottom - center.y

            mini = min(left, top, right, bottom)
            if mini == left:
                closest.x = rect.left
                normal_bkp = (-1, 0)  # Those normal are for the rare case when the center is exactly on the border
            elif mini == right:
                closest.x = rect.right
                normal_bkp = (1, 0)
            elif mini == top:
                closest.y = rect.top
                normal_bkp = (0, -1)
            elif mini == bottom:
                closest.y = rect.bottom
                normal_bkp = (0, 1)

            normal = center - closest
            n = normal.length()

            if n == 0:
                # noinspection PyUnboundLocalVariable
                return pygame.Vector2(normal_bkp)

            return normal / n
            # return (
            #     normal.dividedBy(-n),  # Out direction
            #     self.RADIUS - n  # penetration
            # )
        else:
            norm = sqrt(norm2)
            return d / -norm
            # return (
            #     d.dividedBy(-norm),  # Out direction
            #     self.RADIUS - norm  # penetration
            # )

    def on_death(self, game):
        settings.balls_lost += 1
        game.do_shake(5)
        nb = 10 if len(list(game.get_all(Ball))) > 1 else 45
        for _ in range(nb):
            game.add(Particle.death_particles(self.pos))


class EnemyBullet(Object):
    SIZE = (6, 2)
    EXPLOSION_PARTICLES = 100
    VELOCITY = 7

    def __init__(self, pos, dir):
        super().__init__(pos, scale(self.SIZE))
        self.vel = pygame.Vector2(dir).normalize() * self.VELOCITY

    def logic(self, game):
        self.pos += self.vel * Config().zoom

        # Bar collision
        for bar in game.get_all(Bar):
            if self.rect.colliderect(bar.rect):
                settings.bullet_hit += 1
                game.loose_life()
                self.alive = False
                for _ in range(self.EXPLOSION_PARTICLES):
                    game.add(Particle.death_particles(self.pos))

        w, h = Config().size
        if not self.rect.colliderect((0, 0, w, h)):
            self.alive = False

    def draw(self, display):
        super().draw(display)
        draw_diamond(display, self.rect.center, self.vel, self.size.x, Color.ORANGE)


class Bricks(Object):
    WINDOW_PROP = 0.8

    def __init__(self, lines=15, cols=15):
        size = (Config().w, Config().h * self.WINDOW_PROP)
        super(Bricks, self).__init__((0, 0), size)
        self.lines = lines
        self.cols = cols

        self.bricks = [
            [None] * cols
            for _ in range(lines)
        ]  # type: List[List[Union[None, Brick]]]

    def resize(self, old, new):
        super().resize(old, new)
        self.size = pygame.Vector2(new.x, new.y * self.WINDOW_PROP)

        for (l, c), brick in self.all_bricks(True):
            brick.resize(old, new)
            brick.pos = self.to_screen(l, c)
            brick.size = self.brick_size

    def __len__(self):
        return sum(1 for _ in self.all_bricks())

    @property
    def line_height(self):
        return self.size.y / self.lines

    @property
    def col_width(self):
        return self.size.x / self.cols

    @property
    def brick_size(self):
        return pygame.Vector2(self.col_width, self.line_height)

    def to_screen(self, line, col):
        return pygame.Vector2(
            col * self.col_width,
            line * self.line_height
        )

    def to_grid(self, pos):
        return pos[1] // self.line_height, pos[0] // self.col_width

    def all_bricks(self, indices=False):
        for l, line in enumerate(self.bricks):
            for c, brick in enumerate(line):
                if brick is not None:
                    if indices:
                        yield (l, c), brick
                    else:
                        yield brick

    def brick_range(self, x, y, w, h):
        for (c, l), brick in self.all_bricks(True):
            if x <= c < x + w and y <= l < y + h:
                yield brick

    def draw(self, display):
        super().draw(display)
        for brick in self.all_bricks():
            if brick is not None:
                brick.draw(display)

    def logic(self, state):
        for (l, c), brick in self.all_bricks(True):
            if brick is not None:
                if not brick.alive:
                    self.bricks[l][c] = None
                else:
                    brick.logic(state)

    @classmethod
    def load(cls, level):
        sprite = get_level_surf(level)
        lvl = Bricks()
        palette = list(sprite.get_palette())
        for l in range(15):
            for c in range(15):
                color = sprite.get_at((c, l))
                kind = palette.index(color)
                brick = lvl.make_brick(kind, l, c)
                lvl.bricks[l][c] = brick

        # Power up some bricks
        for brick, nb in Config().bricks_levels.items():
            for _ in range(nb):
                (l, c), _ = choice(list(lvl.all_bricks(True)))
                lvl.bricks[l][c] = lvl.make_brick(brick, l, c)
        return lvl

    def make_brick(self, kind, l, c):

        if isinstance(kind, int):
            if kind < 1:
                return None

            kind = {
                3: GlassBrick,
                5: Brick,
                10: DoubleBrick,
                12: BombBrick,
            }[kind]

        return kind(self.to_screen(l, c), self.brick_size)

    @classmethod
    def random(cls):
        idx = randrange(0, 13)
        return cls.load(idx)

class Brick(Object):
    PARTICLES = 6
    SPRITE = None
    SINGLE_HIT = False
    COLOR = Color.BRIGHT
    SOLID = True

    def __init__(self, pos, size):
        super().__init__(pos, size)
        self.life = Config().brick_life if not self.SINGLE_HIT else 1

    def __repr__(self):
        return f"<Brick({self.pos.x}, {self.pos.y})>"

    def draw(self, display):
        if self.COLOR:
            display.fill(self.COLOR, self.rect)
        border = 2 + 2 * self.life
        tl, tr, br, bl = [
            self.rect.topleft,
            self.rect.topright,
            self.rect.bottomright,
            self.rect.bottomleft
        ]
        for i in range(border):
            d1 = pygame.Vector2(i, i)
            d2 = pygame.Vector2(-i, i)
            pygame.draw.line(display, Color.DARK, br - d1, bl - d2)
            pygame.draw.line(display, Color.DARK, br - d1, tr + d2)
            pygame.draw.line(display, Color.BRIGHTEST, tl + d1, tr + d2)
            pygame.draw.line(display, Color.BRIGHTEST, tl + d1, bl - d2)

        if self.SPRITE is not None:
            img = sprite(self.SPRITE, round(self.size.y / 16))
            r = img.get_rect(center=self.rect.center)
            display.blit(img, r)

        super().draw(display)

    def hit(self, game, sound=True, damage=1):
        get_sound('hit').play()
        self.life -= damage
        if self.life <= 0:
            settings.bricks_destroyed += 1
            self.alive = False

            score = game.increase_score()
            game.add(TextParticle(f"+{score}", self.rect.center, (0, -1)))

            particles = self.PARTICLES
        else:
            score = game.increase_score(hit=True)
            game.add(TextParticle(f"+{score}", self.rect.center, (0, -1), 20, size=24))
            particles = self.PARTICLES // 2

        for _ in range(particles):
            game.add(Particle(
                self.rect.center,
                polar(gauss(13, 3), uniform(0, 360)),
                15
            ))

    def logic(self, state):
        if Config().fire():
            bar = next(state.get_all(Bar))
            get_sound('pre-shot').play()

            # Compute earlier, it is more forgiving
            dir = bar.rect.center - self.pos
            @state.add
            @Schedule.at(+60)
            def _():
                get_sound('shot').play()
                state.add(EnemyBullet(self.rect.center, dir))


class BombBrick(Brick):
    SPRITE = 16
    PARTICLES = 35
    SINGLE_HIT = True

    def hit(self, game, sound=True, damage=1):
        if not self.alive:
            return
        settings.explosions += 1
        get_sound('bomb').play()
        super(BombBrick, self).hit(game, False)

        level: Bricks = game.bricks
        x, y = level.to_grid(self.rect.center)
        for brick in level.brick_range(x - 1, y - 1, 3, 3):
            if brick is not self:
                brick.hit(game, sound=False, damage=3)

class DoubleBrick(Brick):
    SPRITE = 17
    PARTICLES = 20
    SINGLE_HIT = True

    def hit(self, game, sound=True, damage=1):
        super(DoubleBrick, self).hit(game, sound, damage)
        game.add(Ball(self.rect.center))


class GlassBrick(Brick):
    COLOR = None
    SPRITE = 18
    SINGLE_HIT = True
    SOLID = False



class Schedule(Object):
    def __init__(self, func, delay):
        super().__init__((0, 0), (0, 0))
        self.func = func
        self.delay = delay

    def logic(self, state):
        self.delay -= 1
        if self.delay <= 0:
            self.func()
            self.alive = False

    @classmethod
    def at(cls, delay):
        def wrapper(f):
            return Schedule(f, delay)

        return wrapper
