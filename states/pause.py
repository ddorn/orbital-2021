import pygame
import pygame.gfxdraw

from core import State
from locals import clamp, Color, Config, Settings


class PauseState(State):
    def __init__(self, paused):
        super().__init__()
        self.paused = paused
        self.index = 0
        self.settings = ['music', 'sfx']
        self.timer = 0

    def on_key_down(self, event):
        if event.key in (pygame.K_SPACE, pygame.K_p):
            self.next_state = self.paused
        elif event.key == pygame.K_UP:
            self.index -= 1
        elif event.key == pygame.K_DOWN:
            self.index += 1
        elif event.key == pygame.K_LEFT:
            self.edit(-0.1)
        elif event.key == pygame.K_RIGHT:
            self.edit(+0.1)
        self.index %= len(self.settings)

    def value_of(self, idx):
        return getattr(Settings(), self.settings[idx])

    def edit(self, change=0.0):
        value = clamp(self.value_of(self.index) + change, 0, 1)
        setattr(Settings(), self.settings[self.index], value)

    def draw(self, display):
        super().draw(display)
        self.paused.draw(display)
        pygame.gfxdraw.box(display, display.get_rect(), (0, 0, 0, 120))

        w, h = Config().size
        r = self.draw_text(display, "PAUSED", Color.GOLD, Config().iscale(64), midtop=(w / 2, h * 0.2))

        for i, s in enumerate(self.settings):
            v = self.value_of(i)
            txt = f"{s}: {round(v * 100)}%"
            if i == self.index:
                color = Color.GOLD
                if self.timer % 120 > 15:
                    txt = f"< {txt} >"
            else:
                color = Color.BRIGHTEST

            r = self.draw_text(display, txt, color, Config().iscale(32), midtop=r.midbottom)

    def logic(self):
        super().logic()
        self.timer += 1
