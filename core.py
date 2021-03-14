from functools import lru_cache
from operator import attrgetter
from random import randint
from time import time

import pygame

from locals import Color, Config, DEBUG, draw_text, Files, vec2int, VOLUME


class Object:
    Z = 0
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
        if event.type == pygame.KEYDOWN:
            self.hangle_key_press(event)

    def handle_mouse_event(self, event):
        pass

    def hangle_key_press(self, event):
        pass

    def logic(self, state):
        pass

    def draw(self, display: pygame.Surface):
        if DEBUG:
            pygame.draw.rect(display, 'red', (self.pos, self.size), 1)

    def on_death(self, game):
        pass

    def resize(self, old, new):
        ratio = new.x / old.x
        self.size *= ratio
        self.pos *= ratio


class State:
    BG_COLOR = Color.DARKEST
    BG_MUSIC = None

    def __init__(self):
        self.add_later = []
        self.add_lock = False
        self.objects = set()
        self.next_state = self
        self.shake = 0

    @property
    def size(self):
        return Config().size

    @property
    def w(self):
        return Config().w

    @property
    def h(self):
        return Config().h

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

    def logic(self):
        """All the logic of the state happens here.

        To change to an other state, you need to set self.next_state"""

        # Add all object that have been queued
        self.add_lock = False
        for object in self.add_later:
            self.add(object)
        self.add_later = []
        self.add_lock = True

        # Logic for all objects
        for object in self.objects:
            object.logic(self)

        # Clean dead objects
        to_remove = set()
        for object in self.objects:
            if not object.alive:
                to_remove.add(object)
                object.on_death(self)
        self.objects.difference_update(to_remove)

    def draw(self, display: pygame.Surface):
        if self.BG_COLOR:
            display.fill(self.BG_COLOR)

        for z in sorted(set(o.Z for o in self.objects)):
            for obj in self.objects:
                if z == obj.Z:
                    obj.draw(display)

        if self.shake:
            s = 3
            display.scroll(randint(-s, s), randint(-s, s))
            self.shake -= 1

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.on_key_down(event)
        if event.type == pygame.MOUSEMOTION:
            self.on_mouse_move(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.on_click(event)

        for object in self.objects:
            object.handle_event(event)

    # For compatibility wiiith the rest of the code
    def draw_text(self, surf, txt, color=None, size=32, **anchor):
        return draw_text(surf, txt, color, size, **anchor)

    @staticmethod
    @lru_cache()
    def get_font(size):
        return pygame.font.Font(Files.FONT, size)

    def on_key_down(self, event):
        pass

    def on_click(self, event):
        pass

    def on_mouse_move(self, event):
        pass

    def do_shake(self, frames):
        assert frames >= 0
        self.shake += frames

    def on_resume(self):
        self.next_state = self
        if self.BG_MUSIC:
            pygame.mixer.music.load(Files.SOUNDS / self.BG_MUSIC)
            pygame.mixer.music.set_volume(VOLUME['BG_MUSIC'])
            pygame.mixer.music.play(-1)

    def on_exit(self):
        pass

    def resize(self, old, new):
        for obj in self.objects:
            obj.resize(old, new)


class App:
    FPS = 60
    CURRENT_APP = None
    NAME = "Not a Brick Breaker"
    SIZE = pygame.Vector2(800, 500)  # Design size
    BORDER_COLOR = 'black'

    def __init__(self, initial_state):
        self.running = False
        self.clock = pygame.time.Clock()


        App.CURRENT_APP = self

        self.real_size = pygame.Vector2(pygame.display.list_modes()[0])
        self.view_port: pygame.Rect = None
        self.display: pygame.Surface = None
        self.real_display: pygame.Surface = None

        # Open the window
        self.set_display()
        pygame.display.set_caption(self.NAME)

        self.state = initial_state()

    @property
    def scale(self):
        return min(self.real_size.x / self.SIZE.x, self.real_size.y / self.SIZE.y)

    def set_display(self, size=None):
        """Setup the display to a given size."""
        real_size = pygame.Vector2(size or self.real_size)
        self.real_display = pygame.display.set_mode(vec2int(real_size), pygame.RESIZABLE)
        self.real_size = pygame.Vector2(self.real_display.get_size())
        self.real_display.fill(self.BORDER_COLOR)

        # We find the viewport so we have black border if the ratio do not match
        area = self.SIZE * self.scale
        rect = pygame.Rect((self.real_size - area) / 2, area)

        self.view_port = rect
        self.display = self.real_display.subsurface(rect)

        Config().size = pygame.Vector2(self.view_port.size)

    def run(self):
        frame = 0
        start = time()
        self.running = True
        self.state.on_resume()
        while self.running:
            self.events()
            self.state.logic()
            self.state.draw(self.display)

            pygame.display.update()
            self.clock.tick(self.FPS)
            frame += 1
            if self.state != self.state.next_state:
                self.state.on_exit()
                self.state = self.state.next_state
                self.state.on_resume()

        duration = time() - start
        print(f"Game played for {duration:.2f} seconds, at {frame / duration:.1f} FPS.")

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.VIDEORESIZE:
                old = Config().size
                self.set_display(event.size)
                new = Config().size
                self.state.resize(old, new)

            self.state.handle_event(event)


