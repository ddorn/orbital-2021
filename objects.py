from math import sqrt
from random import gauss, randrange, uniform
from typing import List, Union

import pygame

from core import App, Object
from locals import Color, clamp, Config, polar


class Particle(Object):
    DIAMOND = 0
    LINE = 1

    def __init__(self, pos, vel, lifespan, decay=0.95, size=2, color=Color.BRIGHTEST, shape=DIAMOND):
        super().__init__(pos, (size, size))
        self.vel = pygame.Vector2(vel)
        self.lifespan = lifespan
        self.age = 0
        self.decay = decay
        self.shape = shape
        self.color = color

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
            dir = self.vel.normalize()
            cross = pygame.Vector2(-dir.y, dir.x)
            vertices = [
                self.pos + dir * r,
                self.pos + cross * r,
                self.pos - dir * r * 2,
                self.pos - cross * r,
            ]
            pygame.draw.polygon(display, self.color, vertices)
        elif self.shape == self.LINE:
            pygame.draw.line(display, self.color, self.pos, self.pos + self.vel * 3, 3)
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


class Bar(Object):
    START_SIZE = (75, 12)
    START_VELOCITY = 9
    K_LEFT = (pygame.K_LEFT, pygame.K_a, pygame.K_q)
    K_RIGHT = (pygame.K_RIGHT, pygame.K_d)

    def __init__(self, pos_y):
        x = App.width() / 2 - self.START_SIZE[0] / 2
        # x = pygame.mouse.get_pos()[0] - self.SIZE[0] / 2
        super().__init__((x, pos_y), self.START_SIZE)
        self.velocity = self.START_VELOCITY

    # def handle_mouse_event(self, event):
    #     x, y = event.pos
    #     self.pos.x = clamp(
    #         x - self.size.x / 2,
    #     0,
    #     App.state().w - self.size.x
    # )

    def logic(self, state):
        keys = pygame.key.get_pressed()
        if any(keys[k] for k in self.K_LEFT):
            self.pos.x -= self.velocity
        if any(keys[k] for k in self.K_RIGHT):
            self.pos.x += self.velocity

        self.pos.x += Config().wind_speed

        self.pos.x = clamp(
            self.pos.x,
            0,
            App.state().w - self.size.x
        )

    def draw(self, display):
        display.fill(Color.BRIGHTEST, self)
        pygame.draw.rect(display, Color.BRIGHT, self.rect, 2)

    def spawn_ball(self):
        return Ball(self.rect.center + pygame.Vector2(0, -30))


class Ball(Object):
    VELOCITY = 7
    RADIUS = 10

    def __init__(self, center):
        pos = center - pygame.Vector2(self.RADIUS, self.RADIUS)
        super().__init__(pos, (self.RADIUS * 2, self.RADIUS * 2))
        self.vel = pygame.Vector2(0, -self.VELOCITY)

    def logic(self, state):
        self.pos += self.vel
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
        for bar in state.get_all(Bar):
            r = self.rect
            br: pygame.Rect = bar.rect
            if self.rect_collision(br) is not None:
                dx = (r.centerx - br.centerx) / br.width * 2  # proportion on the side
                dx = clamp(dx, -0.8, 0.8)
                dx = round(8 * dx) / 8  # discrete steps like in the original game

                angle = (-dx + 1) * 90
                self.vel.from_polar((self.VELOCITY, -angle))

        # Collision against bricks
        for bricks in state.get_all(Bricks):
            for brick in bricks.all_bricks():
                # TODO: only the bricks in the ball's rectangle
                if (n := self.rect_collision(brick.rect)) is not None:
                    vel_along_normal = n.dot(self.vel)
                    if vel_along_normal < 0:
                        continue  # Already separating
                    # invert velocity along the normal
                    self.vel -= 2 * vel_along_normal * n
                    brick.hit(state)

    def draw(self, display):
        super(Ball, self).draw(display)

        pygame.draw.circle(display, Color.BRIGHT, self.rect.center, self.RADIUS)
        pygame.draw.circle(display, Color.BRIGHTEST, self.rect.center, self.RADIUS * 0.75)

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
        if norm2 >= (self.RADIUS ** 2):
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
        game.do_shake(5)
        nb = 10 if len(list(game.get_all(Ball))) > 1 else 45
        for _ in range(nb):
            game.add(Particle.death_particles(self.pos))


class EnemyBullet(Object):
    SIZE = (4, 7)
    EXPLOSION_PARTICLES = 100
    VELOCITY = 7

    def __init__(self, pos, dir):
        super().__init__(pos, self.SIZE)
        self.vel = pygame.Vector2(dir).normalize() * self.VELOCITY

    def logic(self, game):
        self.pos += self.vel

        # Bar collision
        for bar in game.get_all(Bar):
            if self.rect.colliderect(bar.rect):
                game.loose_life()
                self.alive = False
                for _ in range(self.EXPLOSION_PARTICLES):
                    game.add(Particle.death_particles(self.pos))

    def draw(self, display):
        super().draw(display)
        pygame.draw.line(display, Color.ORANGE, self.pos, self.pos - self.vel * 2, 4)
        display.fill(Color.ORANGE, self.rect)


class Bricks(Object):
    def __init__(self, lines, cols, size):
        super(Bricks, self).__init__((0, 0), size)
        self.lines = lines
        self.cols = cols

        self.bricks = [
            [None] * cols
            for _ in range(lines)
        ]  # type: List[List[Union[None, Brick]]]

        for c in range(lines // 3, 2 * lines // 3 + 1):
            for l in range(4, 6):
                # l = randrange(0, lines)
                # c = randrange(0, cols)
                if c != cols // 2:
                    self.bricks[l][c] = Brick(self.grid_to_screen(l, c), self.brick_size)

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
        return self.col_width, self.line_height

    def grid_to_screen(self, line, col):
        return pygame.Vector2(
            col * self.col_width,
            line * self.line_height
        )

    def screen_to_grid(self, pos):
        return pos.x // self.col_width, pos.y // self.line_height

    def all_bricks(self, indices=False):
        for l, line in enumerate(self.bricks):
            for c, brick in enumerate(line):
                if brick is not None:
                    if indices:
                        yield (l, c), brick
                    else:
                        yield brick

    def draw(self, display):
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


class Brick(Object):
    PARTICLES = 6

    def __init__(self, pos, size):
        super().__init__(pos, size)
        self.color = Color.BRIGHT
        self.life = Config().brick_life

    def __repr__(self):
        return f"<Brick({self.pos.x}, {self.pos.y})>"

    def draw(self, display):
        display.fill(self.color, self.rect)
        pygame.draw.rect(display, Color.DARKEST, self.rect, 2)

    def hit(self, game):
        self.life -= 1
        if self.life <= 0:
            self.alive = False

            from states.game import GameState
            if isinstance(game, GameState):
                game.score += 1

            particles = self.PARTICLES
        else:
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
            state.add(EnemyBullet(self.pos, bar.rect.center - self.pos))

