from config import config
import pygame
from abc import ABC, abstractmethod
from src.button import Button
import math
from src.number_gen import simpleGen, oneNineGen



class GameData():
    def __init__(self):
        self.mode = config["algorithm"]
        self.startingPlayer = config["start"]
        self.genAlgorithm = config['genAlgorithm'] # start number
        self.score = [0, 0]
        self.startingNumber = None
        self.numbersToPlay = []
        print("Game Script is running")

    def updateMode(self, algorithm):
        self.mode = algorithm


    def updateStartingPlayer(self, start):
        self.startingPlayer = start

    def updateGenAlgorithm(self, genAlgorithm):
        self.genAlgorithm = genAlgorithm

    def updateScore(self, score):
        self.score = score

    def newGame(self):
        self.updateScore([0,0])
        self.startingPlayer = 0
        self.generateNumbers()

    def generateNumbers(self):
        numbs = set()
        while len(numbs) < 5:
            if self.genAlgorithm == "simple":
                numbs.add(simpleGen())
            else:
                numbs.add(oneNineGen())
        self.numbersToPlay = list(numbs)


    def chooseNumberToPlay(self, number):
        self.startingNumber = number


    def generateTree(self):
        pass

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
        layers = 16
        layerList = []
        for i in range(layers):
            t = (i + self.wallOffset) % layers
            layerList.append(t)
        layerList.sort()
        deltaMovment = 5
        colorReduction = 3
        shiftCoefficient = 150
        for t in layerList:
            x = int((t / layers) * shiftCoefficient)
            color = max(0, min(255/ colorReduction, x / colorReduction))
            pygame.draw.polygon(screen, (color, color, color), [(600 + x, 300 - deltaMovment * x), (800,0), (1280 ,0), (1280,720), (800,720), (600 + x,300 + deltaMovment * x)])


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
    def __init__(self, game):
        super().__init__(game)
        color = (20, 20, 20, 10)
        self.genAlgorithmButton = Button(600, 400, 300, 60, f"Gen: {self.game.gameData.genAlgorithm}", None, color)
        self.algorithmButton = Button(600, 470, 300, 60, f"Algorithm: {self.game.gameData.mode}", None, color)
        self.backButton = Button(600, 540, 300, 60, "Back", None, color)
    
    def playScreen(self, screen, dt, events):
        screen.fill("black")
        self.genAlgorithmButton.draw(screen)
        self.algorithmButton.draw(screen)
        self.backButton.draw(screen)

        for event in events:
            if self.genAlgorithmButton.clicked(event):
                if self.game.gameData.genAlgorithm == "simple":
                    newGen = "oneNineGen"
                else:
                    newGen = "simple"
                self.game.gameData.updateGenAlgorithm(newGen)
                self.genAlgorithmButton.setText(newGen)
            elif self.algorithmButton.clicked(event):
                if self.game.gameData.mode == "minMax":
                    newMode = "alfaBeta"
                else:
                    newMode = "minMax"
                self.game.gameData.updateMode(newMode)
                self.algorithmButton.setText(newMode)
            elif self.backButton.clicked(event):
                self.game.setScreen(IntroScreen(self.game))

class EndScreen(Screen):
    def playScreen(self, screen, dt, events):
        screen.fill("black")

# https://www.pygame.org/docs/
class Game():
    def __init__(self):
        self.currentScreen = None
        self.gameData = GameData()
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