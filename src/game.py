from config import config
import pygame
from abc import ABC, abstractmethod


class GameData():
    def __init__(self):
        self.mode = config["algorithm"]
        self.start = config["start"]
        self.number = config['gen_algorithm']
        self.nodes = []
        self.playerScore1 = 0
        self.playerScore2 = 0
        print("Game Script is running")

# http://datacamp.com/tutorial/python-abstract-classes
class Screen(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def playScreen(self, screen, dt):
        pass

class IntroScreen(Screen):
    def playScreen(self, screen, dt):
        screen.fill("blue")


class GameScreen(Screen):
    def playScreen(self, screen, dt):
        screen.fill("purple")

class SettingsScreen(Screen):
    def playScreen(self, screen, dt):
        screen.fill("grey")

class EndScreen(Screen):
    def playScreen(self, screen, dt):
        screen.fill("black")

# https://www.pygame.org/docs/

class Game():
    def __init__(self):
        self.currentScreen = IntroScreen(self)
        self.gameLoop()

    def setScreen(self, screen: Screen):
        self.currentScreen = screen

    def gameLoop(self):
        pygame.init()
        screen = pygame.display.set_mode((1280, 720))
        clock = pygame.time.Clock()
        running = True
        dt = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.currentScreen.playScreen(screen, dt)
            pygame.display.flip()
            dt = clock.tick(60) / 1000
        pygame.quit()