from functools import lru_cache
from time import time

import pygame

from locals import Color, Paths

DEBUG = 0


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


class State:
    BG_COLOR = Color.DARKEST

    def __init__(self, size):
        self.add_later = []
        self.add_lock = False
        self.objects = set()
        self.size = pygame.Vector2(size)
        self.next_state = self

    @property
    def w(self):
        return self.size[0]

    @property
    def h(self):
        return self.size[1]

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
        self.objects.difference_update(to_remove)

    def draw(self, display):
        if self.BG_COLOR:
            display.fill(self.BG_COLOR)

        for object in self.objects:
            object.draw(display)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.on_key_down(event)

        for object in self.objects:
            object.handle_event(event)

    def resize(self, new_size):
        self.size = pygame.Vector2(new_size)

    def draw_text(self, surf, txt, color=Color.BRIGHTEST, size=32, **anchor):
        assert len(anchor) == 1
        # noinspection PyTypeChecker
        tmp_surf = self.get_font(size).render(str(txt), 1, color, self.BG_COLOR)
        rect = tmp_surf.get_rect(**anchor)
        surf.blit(tmp_surf, rect)

        return rect

    def on_key_down(self, event):
        pass

    @staticmethod
    @lru_cache()
    def get_font(size):
        return pygame.font.Font(Paths.FONT, size)


class App:
    SIZE = (800, 500)
    FPS = 60
    CURRENT_APP = None

    def __init__(self, initial_state):
        self.running = False
        self.display = pygame.display.set_mode(self.SIZE)
        self.clock = pygame.time.Clock()

        self.state = initial_state(self.SIZE)

        App.CURRENT_APP = self

    def run(self):
        frame = 0
        start = time()
        self.running = True
        while self.running:
            self.events()
            self.state.logic()
            self.state.draw(self.display)

            pygame.display.update()
            self.clock.tick(self.FPS)
            frame += 1
            self.state = self.state.next_state

        duration = time() - start
        print(f"Game played for {duration:.2f} seconds, at {frame / duration:.1f} FPS.")

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

            self.state.handle_event(event)

    @classmethod
    def app(cls):
        return cls.CURRENT_APP

    @classmethod
    def state(cls):
        return cls.CURRENT_APP.state

    @classmethod
    def width(cls):
        if cls.CURRENT_APP:
            return cls.CURRENT_APP.SIZE[0]
        else:
            return cls.SIZE[0]

    @classmethod
    def height(cls):
        if cls.CURRENT_APP:
            return cls.CURRENT_APP.SIZE[1]
        else:
            return cls.SIZE[1]
