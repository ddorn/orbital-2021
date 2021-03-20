from core import App
from states.menu import MenuState

if __name__ == '__main__':
    import pygame
    print(pygame.init())

    App(MenuState).run()
