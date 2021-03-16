from core import App
from states.intro import IntroState

if __name__ == '__main__':
    import pygame
    print(pygame.init())

    App(IntroState).run()
