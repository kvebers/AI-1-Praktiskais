from config import config
import pygame
from abc import ABC, abstractmethod
from src.button import Button
import math


class GameData():
    def __init__(self):
        self.mode = config["algorithm"]
        self.start = config["start"]
        self.number = config['genAlgorithm']
        self.nodes = []
        self.playerScore1 = 0
        self.playerScore2 = 0
        print("Game Script is running")

# http://datacamp.com/tutorial/python-abstract-classes
class Screen(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def playScreen(self, screen, dt, events):
        pass

class IntroScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        color = (20, 20, 20, 10)
        self.bgImage = pygame.image.load("assets/RobBanks.png").convert_alpha()
        self.startButton = Button(800, 540, 300, 60, "Start Game", None, color)
        self.settingsButton = Button(800, 600, 300, 60, "Settings", None, color)
        self.time = 0
        self.wallOffset = 0

    def walking(self, screen):
        sineRotation = math.sin(self.time * 2 * math.pi * 2) * 2
        screenWidth, screenHeight = screen.get_size()
        angle = math.sin(self.time * 2 * math.pi * 1.5) * 1
        scaled = pygame.transform.scale(self.bgImage, (screenWidth + 50, screenHeight + 50))
        rotated = pygame.transform.rotate(scaled, angle)
        rect = rotated.get_rect(center=(screenWidth // 2, screenHeight // 2 + sineRotation))
        screen.blit(rotated, rect)

    def drawWall(self, screen):
        layers = 15
        layerList = []
        for i in range(layers):
            t = (i + self.wallOffset) % layers
            layerList.append(t)
        layerList.sort() 
        for t in layerList:
            x = int((t / layers) * 150)
            color = max(0, min(255, x / 2))
            pygame.draw.polygon(screen, (color, color, color), [(600 + x, 300 - 3 * x), (800,0), (1280 ,0), (1280,720), (800,720), (600 + x,300 + 3 * x)])


    def playScreen(self, screen, dt, events):
        self.time += dt
        screen.fill("black")
        self.wallOffset += 1.5 * dt 
        self.drawWall(screen)
        self.walking(screen)
        self.startButton.draw(screen)
        self.settingsButton.draw(screen)

        for event in events:
            if self.startButton.clicked(event):
                self.game.setScreen(GameScreen(self.game))
            elif self.settingsButton.clicked(event):
                self.game.setScreen(SettingsScreen(self.game))

class GameScreen(Screen):
    def playScreen(self, screen, dt, events):
        screen.fill("purple")

class SettingsScreen(Screen):
    def playScreen(self, screen, dt, events):
        screen.fill("grey")

class EndScreen(Screen):
    def playScreen(self, screen, dt, events):
        screen.fill("black")

# https://www.pygame.org/docs/
class Game():
    def __init__(self):
        self.currentScreen = None
        self.gameLoop()

    def setScreen(self, screen: Screen):
        self.currentScreen = screen

    def gameLoop(self):
        pygame.init()
        screen = pygame.display.set_mode((1280, 720))
        self.currentScreen = IntroScreen(self)
        clock = pygame.time.Clock()
        dt = 0
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            self.currentScreen.playScreen(screen, dt, events)
            pygame.display.flip()
            dt = clock.tick(60) / 1000