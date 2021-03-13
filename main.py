import random
from math import pi, tau
from pathlib import Path
from random import gauss
from time import time

import pygame

pygame.init()

DEBUG = True


def clamp(x, mini, maxi):
    if x < mini:
        return mini
    if x > maxi:
        return maxi
    return x

class Color:
    DARKEST = "#331727"
    DARK = "#440a67"
    # 93329e
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

    def draw(self, display):
        if DEBUG:
            pygame.draw.rect(display, 'red', (self.pos, self.size), 1)


class Bar(Object):
    SIZE = (50, 10)

    def __init__(self, pos_y):
        x = pygame.mouse.get_pos()[0] - self.SIZE[0] / 2
        super().__init__((x, pos_y), self.SIZE)

    def handle_mouse_event(self, event):
        x, y = event.pos
        self.pos.x = x - self.size.x / 2

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
            if r.colliderect(br):
                dx = (r.centerx - br.centerx) / br.width   # proportion on the side
                dx = round(8 * dx) / 8  # discrete steps like in the original game

                angle = (-dx + 1) * 90
                self.vel.from_polar((self.VELOCITY, -angle))
                self.pos.y = br.top - self.size.y

    def draw(self, display):
        super(Ball, self).draw(display)

        pygame.draw.circle(display, Color.BRIGHT, self.rect.center, self.RADIUS)
        pygame.draw.circle(display, Color.BRIGHTEST, self.rect.center, self.RADIUS * 0.75)


class Game:
    SIZE = (800, 500)
    FPS = 60
    BG_COLOR = Color.DARKEST

    def __init__(self):
        self.running = False
        self.display = pygame.display.set_mode(self.SIZE)
        self.clock = pygame.time.Clock()

        self.debug = "debug"
        self.font = pygame.font.Font(Paths.FONT, 20)

        self.objects = []
        self.bar = self.add(Bar(self.SIZE[1] - 30))
        self.add(self.bar.spawn_ball())

    def add(self, object):
        self.objects.append(object)
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
        # Logic for all objects
        for object in self.objects:
            object.logic(self)

        # Clean dead objects
        to_remove = []
        for i, object in enumerate(self.objects):
            if not object.alive:
                to_remove.append(i)
        for idx in reversed(to_remove):
            self.objects.pop(idx)

        # Global logic
        if not list(self.get_all(Ball)):
            # No more balls
            self.add(self.bar.spawn_ball())

    def draw(self):
        self.display.fill(self.BG_COLOR)
        if DEBUG and self.debug:
            txt = self.font.render(self.debug, 1, Color.BRIGHTEST, self.BG_COLOR)
            self.display.blit(txt, (3, 3))

        for object in self.objects:
            object.draw(self.display)


if __name__ == '__main__':
    Game().run()
