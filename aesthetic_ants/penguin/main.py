import pyglet

from .game import Game

pyglet.resource.path = ['../resources']
pyglet.resource.reindex()


def main():
    game = Game(fullscreen=True)
    game.run()


if __name__ == '__main__':
    main()
