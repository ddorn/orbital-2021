import random
from functools import lru_cache
from math import pi, sqrt, tau
from pathlib import Path
from random import gauss, randrange, uniform
from time import time
from typing import List
from typing import Union

import pygame

pygame.init()

DEBUG = 0


def clamp(x, mini, maxi):
    if x < mini:
        return mini
    if x > maxi:
        return maxi
    return x


class Color:
    DARKEST = "#331727"
    DARK = "#440a67"
    MIDDLE = '#93329e'
    BRIGHT = '#b4aee8'
    BRIGHTEST = '#ffe3fe'


class Paths:
    TOP = Path(__file__).parent
    ASSETS = TOP / "assets"
    FONT = ASSETS / "fonts" / "ThaleahFat.ttf"


class Object:
    def __init__(self, pos, size):
        self.pos = pygame.Vector2(pos)
        self.size = pygame.Vector2(size)
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(self.pos, self.size)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.handle_mouse_event(event)

    def handle_mouse_event(self, event):
        pass

    def logic(self, game):
        pass

    def draw(self, display: pygame.Surface):
        if DEBUG:
            pygame.draw.rect(display, 'red', (self.pos, self.size), 1)


class Particle(Object):
    def __init__(self, pos, vel, lifespan, decay=0.95):
        super().__init__(pos, (1, 1))
        self.vel = pygame.Vector2(vel)
        self.lifespan = lifespan
        self.age = 0
        self.decay = decay

    def logic(self, game):
        self.age += 1
        if self.age > self.lifespan:
            self.alive = False
        self.pos += self.vel
        self.vel *= self.decay

    def draw(self, display):
        super(Particle, self).draw(display)
        r = 5 * (1 - self.age / self.lifespan) ** 0.5
        dir = self.vel.normalize()
        cross = pygame.Vector2(-dir.y, dir.x)
        vertices = [
            self.pos + dir * r,
            self.pos + cross * r,
            self.pos - dir * r * 2,
            self.pos - cross * r,
        ]
        pygame.draw.polygon(display, Color.BRIGHTEST, vertices)

        # pygame.draw.circle(display, Color.BRIGHTEST, self.pos, radius)


class Bar(Object):
    SIZE = (50, 10)

    def __init__(self, pos_y):
        x = pygame.mouse.get_pos()[0] - self.SIZE[0] / 2
        super().__init__((x, pos_y), self.SIZE)

    def handle_mouse_event(self, event):
        x, y = event.pos
        self.pos.x = x - self.size.x / 2

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

    def logic(self, game):
        self.pos += self.vel

        if self.pos.x < 0:
            self.pos.x = 0
            self.vel.x *= -1
        if self.pos.x > game.SIZE[0] - self.size.x:
            self.pos.x = game.SIZE[0] - self.size.x
            self.vel.x *= -1
        if self.pos.y < 0:
            self.pos.y = 0
            self.vel.y *= -1
        if self.pos.y > game.SIZE[1]:
            self.alive = False

        # Collision with bars
        for bar in game.get_all(Bar):
            r = self.rect
            br: pygame.Rect = bar.rect
            if self.rect_collision(br) is not None:
                dx = (r.centerx - br.centerx) / br.width * 2  # proportion on the side
                dx = clamp(dx, -0.8, 0.8)
                dx = round(8 * dx) / 8  # discrete steps like in the original game

                angle = (-dx + 1) * 90
                self.vel.from_polar((self.VELOCITY, -angle))
                self.pos.y = br.top - self.size.y

        # Collision against bricks
        for brick in game.bricks.all_bricks():
            # TODO: only the bricks in the ball's rectangle
            if (n := self.rect_collision(brick.rect)) is not None:
                vel_along_normal = n.dot(self.vel)
                if vel_along_normal < 0:
                    continue  # Already separating
                # invert velocity along the normal
                self.vel -= 2 * vel_along_normal * n
                brick.hit(game)

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
                breakpoint()
                return normal_bkp

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
            for l in range(2, cols // 3):
                # l = randrange(0, lines)
                # c = randrange(0, cols)
                self.bricks[l][c] = Brick(self.grid_to_screen(l, c), self.brick_size)

        print(self.bricks)

    @property
    def line_height(self):
        return self.size.y / self.lines

    @property
    def col_width(self):
        return self.size.x / self.cols

    @property
    def brick_size(self):
        return (self.col_width, self.line_height)

    def grid_to_screen(self, line, col):
        return pygame.Vector2(
            col * self.col_width,
            line * self.line_height
        )

    def screen_to_grid(self, pos):
        return (pos.x // self.col_width, pos.y // self.line_height)

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

    def logic(self, game):
        for (l, c), brick in self.all_bricks(True):
            if brick is not None and not brick.alive:
                self.bricks[l][c] = None


class Brick(Object):
    PARTICLES = 6

    def __init__(self, pos, size):
        super().__init__(pos, size)
        self.color = Color.BRIGHT

    def __repr__(self):
        return f"<Brick({self.pos.x}, {self.pos.y})>"

    def draw(self, display):
        display.fill(self.color, self.rect)
        pygame.draw.rect(display, Color.DARKEST, self.rect, 2)

    def hit(self, game):
        self.alive = False
        game.score += 1
        for _ in range(self.PARTICLES):
            vel = pygame.Vector2()
            vel.from_polar((
                gauss(13, 3),
                uniform(0, 360)
            ))
            game.add(Particle(
                self.rect.center,
                vel,
                15
            ))


class Game:
    SIZE = (800, 500)
    FPS = 60
    BG_COLOR = Color.DARKEST

    def __init__(self):
        self.running = False
        self.display = pygame.display.set_mode(self.SIZE)
        self.clock = pygame.time.Clock()

        self.debug = "debug"

        self.score = 0

        self.add_later = []
        self.add_lock = False
        self.objects = set()
        self.bar = self.add(Bar(self.SIZE[1] - 30))
        self.bricks = self.add(Bricks(17, 17, (self.SIZE[0], self.SIZE[1] - 40)))
        self.add(self.bar.spawn_ball())

    def add(self, object):
        if self.add_lock:
            self.add_later.append(object)
        else:
            self.objects.add(object)
        return object

    def get_all(self, type_):
        for object in self.objects:
            if isinstance(object, type_):
                yield object

    def run(self):
        frame = 0
        start = time()
        self.running = True
        while self.running:
            if DEBUG:
                print("Frame: ", frame)

            for event in pygame.event.get():
                self.handle_event(event)
            self.logic()
            self.draw()

            pygame.display.update()
            self.clock.tick(self.FPS)
            frame += 1

        duration = time() - start
        print(f"Game played for {duration:.2} seconds, at {frame / duration:.1f} FPS.")

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_ESCAPE:
                self.running = False
            if key == pygame.K_SPACE:
                self.add(self.bar.spawn_ball())
            else:
                print(event)

        for object in self.objects:
            object.handle_event(event)

    def logic(self):
        # Add all object that have been queued
        self.add_lock = False
        for object in self.add_later:
            self.add(object)
        self.add_later =[]
        self.add_lock = True

        # Logic for all objects
        for object in self.objects:
            object.logic(self)

        # Clean dead objects
        to_remove = set()
        for object in self.objects:
            if not object.alive:
                to_remove.add(object)
        self.objects.difference_update(to_remove)

        # Global logic
        if not list(self.get_all(Ball)):
            # No more balls
            self.add(self.bar.spawn_ball())

    def draw(self):
        self.display.fill(self.BG_COLOR)
        if DEBUG and self.debug:
            self.draw_text(self.debug, topleft=(3, 3))

        self.draw_text(self.score, topright=(self.SIZE[0] - 3, 3))

        for object in self.objects:
            object.draw(self.display)

    def draw_text(self, txt, size=32, **anchor):
        assert len(anchor) == 1
        # noinspection PyTypeChecker
        surf = self.get_font(size).render(str(txt), 1, Color.BRIGHTEST, self.BG_COLOR)
        rect = surf.get_rect(**anchor)
        self.display.blit(surf, rect)

    @staticmethod
    @lru_cache()
    def get_font(size):
        return pygame.font.Font(Paths.FONT, size)


if __name__ == '__main__':
    Game().run()
