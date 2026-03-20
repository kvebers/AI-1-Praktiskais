import sys
import os

# ļauj importēt config.py no projekta saknes (AI-1-Praktiskais-main/config.py)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import config
import pygame
from abc import ABC, abstractmethod
from src.button import Button
import math
from src.graph import Node
from src.number_gen import simpleGen, oneNineGen
from src.game_logic import *
from src.algorithms.mini_max import minimax_search
from src.algorithms.alfa_beta import alpha_beta_search


# -----------------------------
# Data
# -----------------------------
class GameData():
    def __init__(self):
        self.mode = config["algorithm"]
        self.startingPlayer = config["start"]
        self.genAlgorithm = config['genAlgorithm']
        self.score = [0, 0]
        self.startingNumber = None
        self.numbersToPlay = []
        self.head = None
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
        self.updateScore([0, 0])
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

    def generateTree(self, number):
        self.head = Node(
            number=number,
            player=self.startingPlayer,
            score=[0, 0],
            bank=0
        )
        self.recursiveTree(self.head)

    def recursiveTree(self, node):
        state = (node.number, node.score[0], node.score[1], node.bank, node.player)
        for divisor in possible_divisions(state):
            new_state = result_of_turn(state, divisor)
            child = Node(
                number=new_state[0],
                player=new_state[4],
                score=[new_state[1], new_state[2]],
                bank=new_state[3],
                moveUsed=divisor,
                parent=node
            )
            node.children.append(child)
            self.recursiveTree(child)


# -----------------------------
# Screen base
# -----------------------------
class Screen(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def playScreen(self, screen, dt, events):
        pass


# -----------------------------
# Intro / Menu
# -----------------------------
class IntroScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        color = (20, 20, 20, 140)

        self.bgImage = pygame.image.load("assets/RobBanks.png").convert_alpha()

        # pogas (CAST pa vidu)
        self.startButton = Button(800, 420, 300, 60, "Aplaupīt Banku", None, color)
        self.castButton = Button(800, 490, 300, 60, "Biedri", None, color)
        self.settingsButton = Button(800, 560, 300, 60, "Iestatījumi", None, color)

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
            c = max(0, min(255, x / 2))
            pygame.draw.polygon(
                screen,
                (c, c, c),
                [(600 + x, 300 - 3 * x), (800, 0), (1280, 0), (1280, 720), (800, 720), (600 + x, 300 + 3 * x)],
            )

    def playScreen(self, screen, dt, events):
        self.time += dt
        screen.fill("black")
        self.wallOffset += 1.5 * dt
        self.drawWall(screen)
        self.walking(screen)

        self.startButton.draw(screen)
        self.castButton.draw(screen)
        self.settingsButton.draw(screen)
        self.eventLoop(events)

    def eventLoop(self, events):
        for event in events:
            if self.startButton.clicked(event):
                self.game.gameData.generateNumbers()
                self.game.setScreen(StartGameScreen(self.game))
            elif self.castButton.clicked(event):
                self.game.setScreen(CastScreen(self.game))
            elif self.settingsButton.clicked(event):
                self.game.setScreen(SettingsScreen(self.game))



# -----------------------------
# CAST screen
# -----------------------------
class CastScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.fontTitle = pygame.font.SysFont("Roboto", 56, bold=True)
        self.font = pygame.font.SysFont("Roboto", 32)

        color = (20, 20, 20, 140)
        self.backButton = Button(510, 620, 300, 60, "Back to main menu", None, color)

        self.names = [
            "Valērija Brankova",
            "Kārlis Vilhelms Vēbers",
            "Lukass Mackevičs",
            "Kristofers Jekševics",
            "Reinis Blaubergs",
            "Arvīds Rancāns",
        ]

    def playScreen(self, screen, dt, events):
        screen.fill((10, 10, 12))
        title = self.fontTitle.render("CAST", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(640, 120)))
        y = 230
        for name in self.names:
            txt = self.font.render(name, True, (230, 230, 230))
            screen.blit(txt, txt.get_rect(center=(640, y)))
            y += 48
        self.backButton.draw(screen)
        self.eventLoop(events)

    def eventLoop(self, events):
        for event in events:
            if self.backButton.clicked(event):
                self.game.setScreen(IntroScreen(self.game))



class SettingsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        color = (20, 20, 20, 10)
        self.genAlgorithmButton = Button(600, 400, 300, 60, self.game.gameData.genAlgorithm, None, color)
        self.algorithmButton = Button(600, 470, 300, 60, self.game.gameData.mode, None, color)
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


# -----------------------------
# Game screen (Bank BG + coins + AI RobBanks animation)
# -----------------------------
class GameScreen(Screen):
    def __init__(self, game, startNumber):
        super().__init__(game)
        # spēles stāvoklis
        self.initPyGameForScene()
        self.initGame(game, startNumber)

 
    def initPyGameForScene(self):
        self.fontTitle = pygame.font.SysFont("Roboto", 44, bold=True)
        self.font = pygame.font.SysFont("Roboto", 28)
        # Background bilde: assets/banka.png (fallback, ja nav)
        self.bg = pygame.image.load("assets/banka.png").convert()
        self.bg = pygame.transform.scale(self.bg, (1280, 720))
        # RobBanks bilde AI animācijai
        self.rob = pygame.image.load("assets/RobBanks.png").convert_alpha()
        self.rob = pygame.transform.smoothscale(self.rob, (260, 340))

    def initGame(self, game, startNumber):
        self.state = init_state(startNumber, starting_player=0)
        self.humanPlayerIndex = 0 if game.gameData.startingPlayer == 0 else 1
        self.aiPlayerIndex = 1 - self.humanPlayerIndex
        self.divisionButtons = []
        self.aiThinkTimer = 0.0
        self.aiThinkDuration = 0.8
        self.aiMove = None
        self.addDivisionButtons()

    def getAIMove(self):
        if self.game.gameData.mode == "alfaBeta":
            return alpha_beta_search(self.state)
        else:
            return minimax_search(self.state)
        
    def humanTurn(self):
        return whose_turn(self.state) == self.humanPlayerIndex
 
    def getHumanScore(self):
        return self.state[P1_SCORE] if self.humanPlayerIndex == 0 else self.state[P2_SCORE]
 
    def getAIScore(self):
        return self.state[P1_SCORE] if self.aiPlayerIndex == 0 else self.state[P2_SCORE]
 
    def applyMove(self, divisor, who="Human"):
        self.state = result_of_turn(self.state, divisor)
        self.addDivisionButtons()
 
    def addDivisionButtons(self):
        self.divisionButtons = []
        divisions = possible_divisions(self.state)
        buttonStartPosition = 640 - (len(divisions) * 160) // 2
        x, y, w, h = 160, 500, 80, 100
        color = (30, 80, 30, 200)
        hoverColor = (50, 140, 50, 220)
        for i, div in enumerate(divisions):
            label = f"{div}"
            btn = Button(buttonStartPosition + i * x, y, w, h, label, color, hoverColor)
            self.divisionButtons.append((div, btn))
 

    def draw_bg(self, screen):
        if self.bg:
            screen.blit(self.bg, (0, 0))
            overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill((15, 15, 20))
 
    def draw_hud(self, screen):
        title = self.fontTitle.render("Robs Banks Apciemo Banku", True, (255, 255, 255))
        screen.blit(title, (70, 20))
        screen.blit(self.font.render(f"Cilvēks: {self.getHumanScore()}", True, (100, 255, 100)), (70, 80))
        screen.blit(self.font.render(f"Advancēta Drošības Sistēma: {self.getAIScore()}", True, (255, 100, 100)), (800, 80))
        screen.blit(self.font.render(f"Banka: {self.state[BANK_SCORE]}", True, (255, 215, 0)), (580, 80))
 
    def draw_number(self, screen):
        number = self.state[NUMBER]
        txt = self.font.render(str(number), True, (255, 255, 255))
        rect = txt.get_rect(center=(640, 340))
        pygame.draw.circle(screen, (40, 40, 60), (640, 340), 100)
        pygame.draw.circle(screen, (80, 80, 120), (640, 340), 100, 3)
        screen.blit(txt, rect)
 
    def playScreen(self, screen, dt, events):
        self.draw_bg(screen)
        if is_game_over(self.state):
            self.game.setScreen(EndScreen(self.game, self.getHumanScore(), self.getAIScore()))
            return 
        self.draw_hud(screen)
        self.draw_number(screen)
        if self.rob:
            screen.blit(self.rob, (1050, 370))
        # AI kārta -> animācija
        self.AIMoveAnimation(screen, dt)
        self.eventLoop(events)

    def AIMoveAnimation(self, screen, dt):
        if not self.humanTurn():
            if self.aiMove is None:
                self.aiThinkTimer = 0.0
                self.aiMove = self.getAIMove()
            self.aiThinkTimer += dt
            if self.aiThinkTimer >= self.aiThinkDuration and self.aiMove is not None:
                self.applyMove(self.aiMove, who="AI")
                self.aiMove = None
        else:
            for div, btn in self.divisionButtons:
                btn.draw(screen)

    def eventLoop(self, events):
        for event in events:
            if self.humanTurn() and self.aiMove is None:
                for div, btn in self.divisionButtons:
                    if btn.clicked(event):
                        self.applyMove(div, who="Human")
                        return


class StartGameScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.fontTitle = pygame.font.SysFont("Roboto", 44, bold=True)
        self.font = pygame.font.SysFont("Roboto", 28)
        color = (20, 20, 20, 140)
        hover = (60, 60, 60, 180)
        numbers = self.game.gameData.numbersToPlay
        self.numberButtons = []
        startX = 640 - (len(numbers) * 150) // 2
        for i, num in enumerate(numbers):
            btn = Button(startX + i * 150, 350, 130, 70, str(num), color, hover)
            self.numberButtons.append((num, btn))
        start_text = "Uzsāk Laupītājs" if self.game.gameData.startingPlayer == 0 else "Uzsāk Drošības Sistēma"
        self.startButton = Button(340, 480, 600, 50, start_text, color, hover)
        self.backButton = Button(540, 560, 200, 50, "Back", None, color)

    def playScreen(self, screen, dt, events):
        screen.fill((10, 10, 15))
        title = self.fontTitle.render("Rob Banks Apciemo Banku", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(640, 150)))
        info = self.font.render("Izvēlies numuru, lai sāktu spēli", True, (180, 180, 180))
        screen.blit(info, info.get_rect(center=(640, 260)))
        for numb, button in self.numberButtons:
            button.draw(screen)
        self.startButton.draw(screen)
        self.backButton.draw(screen)
        self.eventLoop(events)

    def eventLoop(self, events):
        for event in events:
            if self.startButton.clicked(event):
                if self.game.gameData.startingPlayer == 0:
                    self.game.gameData.updateStartingPlayer(1)
                    self.startButton.setText("Advancēta Drošības Sistēma sāk")
                else:
                    self.game.gameData.updateStartingPlayer(0)
                    self.startButton.setText("Sāk Laupītājs")
                return
            for numb, button in self.numberButtons:
                if button.clicked(event):
                    self.game.gameData.chooseNumberToPlay(numb)
                    self.game.setScreen(GameScreen(self.game, numb))
                    return
            if self.backButton.clicked(event):
                self.game.setScreen(IntroScreen(self.game))

# -----------------------------
# End screen
# -----------------------------
class EndScreen(Screen):
    def __init__(self, game, humanScore, aiScore):
        super().__init__(game)
        self.humanScore = humanScore
        self.aiScore = aiScore
        self.initPyGameForSceen()

    def initPyGameForSceen(self):
        self.fontBig = pygame.font.SysFont("Roboto", 60, bold=True)
        self.font = pygame.font.SysFont("Roboto", 32)
        color = (20, 20, 20, 140)
        self.menuButton = Button(540, 520, 220, 60, "Menu", None, color)
        self.restartButton = Button(540, 600, 220, 60, "Restart", None, color)

    def playScreen(self, screen, dt, events):
        screen.fill((0, 0, 0))
        if self.humanScore > self.aiScore:
            result = "Tu aplaupīji banku!"
        elif self.humanScore < self.aiScore:
            result = "Tevi apturēja drošības sistēma!"
        else:
            result = "Tevi nepieķēra"
        txt = self.fontBig.render(result, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=(640, 240)))
        score = self.font.render(f"Human: {self.humanScore}   AI: {self.aiScore}", True, (255, 255, 255))
        screen.blit(score, score.get_rect(center=(640, 330)))
        self.menuButton.draw(screen)
        self.restartButton.draw(screen)
        for event in events:
            if self.menuButton.clicked(event):
                self.game.setScreen(IntroScreen(self.game))
            if self.restartButton.clicked(event):
                self.game.gameData.generateNumbers()
                self.game.setScreen(StartGameScreen(self.game))


# -----------------------------
# Game loop
# -----------------------------
class Game:
    def __init__(self):
        self.gameData = GameData()
        self.currentScreen = None
        self.gameLoop()

    def setScreen(self, screen: Screen):
        self.currentScreen = screen

    def gameLoop(self):
        pygame.init()
        screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Rob Banks - AI Practical")

        self.currentScreen = IntroScreen(self)
        clock = pygame.time.Clock()
        dt = 0.0

        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            self.currentScreen.playScreen(screen, dt, events)
            pygame.display.flip()
            dt = clock.tick(60) / 1000.0


if __name__ == "__main__":
    Game()