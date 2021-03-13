from core import App
from states.game import GameState
from states.intro import IntroState

if __name__ == '__main__':
    App(IntroState).run()
