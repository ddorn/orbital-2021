import pygame
import pygame.gfxdraw

from core import State
from locals import Color, Config, ease, weighted_choice
from powerups import bad, brick, god_like, good, random_powerup, very_bad


class PickPowerUpState(State):
    bg_color = None

    def __init__(self, game_state, *kinds):
        super(PickPowerUpState, self).__init__()
        self.game_state = game_state
        if not kinds:
            kinds = weighted_choice([
                ((very_bad, bad), 1),
                ((good, god_like, brick), 1),
            ])
        self.powerups = random_powerup(3, *kinds, game=game_state)
        self._selected = 0
        self.selected_at = 0
        self.last_selected = None
        self.timer = 0

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        value %= len(self.powerups)
        if value != self._selected:
            self.last_selected = self._selected
            self._selected = value
            self.selected_at = self.timer

    def on_mouse_move(self, event):
        if Config().mouse_control:
            best = 0
            mini = 99999

            for i in range(len(self.powerups)):
                d = abs(self.pos_x(i) - event.pos[0])
                if d < mini:
                    mini = d
                    best = i
            self.selected = best

    def on_click(self, event):
        if Config().mouse_control:
            self.validate()

    def on_key_down(self, event):
        if event.key == pygame.K_SPACE:
            # Avoid using multiple times a powerup
            if self.next_state == self:
                self.validate()
        elif event.key == pygame.K_LEFT:
            self.selected -= 1
        elif event.key == pygame.K_RIGHT:
            self.selected += 1

    def logic(self):
        super().logic()
        self.timer += 1

    def pos_x(self, i):
        if len(self.powerups) == 1:
            return self.w / 2
        start = self.w * 0.2
        spacing = self.w * 0.6 / (len(self.powerups) - 1)
        return start + spacing * i

    def draw(self, display):
        self.game_state.draw(display)
        pygame.gfxdraw.box(display, display.get_rect(), (0, 0, 0, 120), )

        y = self.h * 0.6
        displacement = ease((self.timer - self.selected_at) / 15) * 50 * Config().zoom
        for i, powerup in enumerate(self.powerups):
            if i == self.selected:
                dy = displacement
                self.draw_text(display, powerup.descr, Color.BRIGHT, midbottom=(self.w / 2, self.h - 50))
            elif i == self.last_selected:
                dy = 50 - displacement
            else:
                dy = 0

            x = self.pos_x(i)
            r = powerup.draw(display, (x, y - dy))

            color = powerup.color
            r = self.draw_text(display, powerup.name, color, midtop=r.midbottom)
            if i == self.selected:
                pygame.draw.line(display, color, r.bottomleft, r.bottomright)

    def validate(self):
        powerup = self.powerups[self.selected]
        powerup.apply(self.game_state)
        self.next_state = self.game_state
        self.game_state.next_state = self.game_state

    def resize(self, old, new):
        super(PickPowerUpState, self).resize(old, new)
        self.game_state.resize(old, new)