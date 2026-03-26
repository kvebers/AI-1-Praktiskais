import sys
import os
import time

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
from src.game_logic import GameState

def count_tree_nodes(gameState, state, depth=0):
    if gameState.is_game_over(state) or depth >= gameState.maxDepth:
        return 1
    total = 1
    for divisor in gameState.possible_divisions(state):
        new_state = gameState.result_of_turn(state, divisor)
        total += count_tree_nodes(gameState, new_state, depth + 1)
    return total


class GameData():
    def __init__(self):
        self.mode = config["algorithm"]
        self.startingPlayer = config["start"]
        self.genAlgorithm = config['genAlgorithm']
        self.score = [0, 0]
        self.startingNumber = None
        self.numbersToPlay = []
        self.head = None
        self.gameState = GameState()
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
        self.recursiveTree(self.head, 0)

    def recursiveTree(self, node, depth):
        if depth >= self.gameState.maxDepth:
            return
        state = (node.number, node.score[0], node.score[1], node.bank, node.player)
        if self.gameState.is_game_over(state):
            return
        for divisor in self.gameState.possible_divisions(state):
            new_state = self.gameState.result_of_turn(state, divisor)
            child = Node(
                number=new_state[0],
                player=new_state[4],
                score=[new_state[1], new_state[2]],
                bank=new_state[3],
                moveUsed=divisor,
                parent=node
            )
            node.children.append(child)
            self.recursiveTree(child, depth + 1)

    def expandTree(self, node):
        if len(node.children) == 0:
            self.recursiveTree(node, 0)


class Screen(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def playScreen(self, screen, dt, events):
        pass


class IntroScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        color = (20, 20, 20, 140)

        self.bgImage = pygame.image.load("assets/RobBanks.png").convert_alpha()
        
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



class CastScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.fontTitle = pygame.font.SysFont("Roboto", 56, bold=True)
        self.font = pygame.font.SysFont("Roboto", 32)
        self.bg = pygame.image.load("assets/banka.png").convert()
        self.bg = pygame.transform.scale(self.bg, (1280, 720))
        color = (20, 20, 20, 140)
        self.darkness = 50
        self.order = True
        self.backButton = Button(500, 620, 280, 60, "Back to main menu", None, color)

        self.names = [
            "Valērija Brankova",
            "Kārlis Vilhelms Vēbers",
            "Lukass Mackevičs",
            "Kristofers Jekševics",
            "Reinis Blaubergs",
            "Arvīds Rancāns",
        ]

    def bg_logic(self, screen):
        dark = 240
        bright = 120
        if self.darkness < dark and self.order:
            self.darkness += 1
        elif self.darkness > bright and not self.order:
            self.darkness -= 1
        else:
            self.order = not self.order

        screen.fill((10, 10, 12))
        screen.blit(self.bg, (0, 0))
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.darkness))
        screen.blit(overlay, (0, 0))


    def playScreen(self, screen, dt, events):
        self.bg_logic(screen)
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
        color = (80, 80, 80, 50)
        bgColor = (0, 0, 0, 90)
        self.bg = pygame.image.load("assets/banka.png").convert()
        self.bg = pygame.transform.scale(self.bg, (1280, 720))
        self.genAlgorithmButton = Button(500, 400, 280, 60, self.game.gameData.genAlgorithm, bgColor, color)
        self.algorithmButton = Button(500, 470, 280, 60, self.game.gameData.mode, bgColor, color)
        self.backButton = Button(500, 540, 280, 60, "Back", bgColor, color)
    
    def bg_logic(self, screen):
        dark = 100
        screen.fill("black")
        screen.blit(self.bg, (0, 0))
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, dark))
        screen.blit(overlay, (0, 0))

    def playScreen(self, screen, dt, events):
        self.bg_logic(screen)
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


class GameScreen(Screen):
    def __init__(self, game, startNumber):
        super().__init__(game)
        # spēles stāvoklis
        self.initPyGameForScene()
        self.initGame(game, startNumber)

 
    def initPyGameForScene(self):
        self.fontTitle = pygame.font.SysFont("Roboto", 44, bold=True)
        self.font = pygame.font.SysFont("Roboto", 28)
        self.bg = pygame.image.load("assets/banka.png").convert()
        self.bg = pygame.transform.scale(self.bg, (1280, 720))
        self.rob = pygame.image.load("assets/RobBanks.png").convert_alpha()
        self.rob = pygame.transform.smoothscale(self.rob, (260, 340))

    def initGame(self, game, startNumber):
        self.gameState = game.gameData.gameState
        self.state = self.gameState.init_state(startNumber, starting_player=game.gameData.startingPlayer)
        self.humanPlayerIndex = 0
        self.aiPlayerIndex = 1
        self.divisionButtons = []
        self.aiThinkTimer = 0.0
        self.aiThinkDuration = 0.8
        self.aiMove = None
        self.totalNodes = 0
        self.totalTreeNodes = 0
        self.moveTimes = []
        game.gameData.generateTree(startNumber)
        self.currentNode = game.gameData.head
        self.addDivisionButtons()

    def getAIMove(self):
        start = time.time()
        if self.game.gameData.mode == "alfaBeta":
            move, nodes = alpha_beta_search(self.gameState, self.state, self.aiPlayerIndex)
        else:
            move, nodes = minimax_search(self.gameState, self.state, self.aiPlayerIndex)
        self.totalNodes += nodes
        self.totalTreeNodes += count_tree_nodes(self.gameState, self.state)
        self.moveTimes.append(time.time() - start)
        return move
        
    def humanTurn(self):
        return self.gameState.whose_turn(self.state) == self.humanPlayerIndex
 
    def getHumanScore(self):
        return self.state[self.gameState.P1_SCORE] if self.humanPlayerIndex == 0 else self.state[self.gameState.P2_SCORE]
 
    def getAIScore(self):
        return self.state[self.gameState.P1_SCORE] if self.aiPlayerIndex == 0 else self.state[self.gameState.P2_SCORE]
 
    def applyMove(self, divisor):
        self.state = self.gameState.result_of_turn(self.state, divisor)
        if self.currentNode is not None:
            for child in self.currentNode.children:
                if child.moveUsed == divisor:
                    self.currentNode = child
                    self.game.gameData.expandTree(self.currentNode)
                    break
        self.addDivisionButtons()
 
    def addDivisionButtons(self):
        self.divisionButtons = []
        divisions = self.gameState.possible_divisions(self.state)
        centerButton = 200
        buttonStartPosition = 640 - (len(divisions) * centerButton) // 2
        x, y, w, h = centerButton, 500, centerButton - 20, 80
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
        screen.blit(self.font.render(f"Banka: {self.state[self.gameState.BANK_SCORE]}", True, (255, 215, 0)), (580, 80))
 
    def draw_number(self, screen):
        number = self.state[self.gameState.NUMBER]
        txt = self.font.render(str(number), True, (255, 255, 255))
        rect = txt.get_rect(center=(640, 340))
        pygame.draw.circle(screen, (40, 40, 60), (640, 340), 100)
        pygame.draw.circle(screen, (80, 80, 120), (640, 340), 100, 3)
        screen.blit(txt, rect)
 
    def playScreen(self, screen, dt, events):
        self.draw_bg(screen)
        if self.gameState.is_game_over(self.state):
            avg_time = sum(self.moveTimes) / len(self.moveTimes) if self.moveTimes else 0.0
            self.game.setScreen(EndScreen(self.game, self.getHumanScore(), self.getAIScore(), self.totalNodes, self.totalTreeNodes, avg_time))
            return 
        self.draw_hud(screen)
        self.draw_number(screen)
        if self.rob:
            screen.blit(self.rob, (1050, 370))
        self.AIMoveAnimation(screen, dt)
        self.eventLoop(events)

    def AIMoveAnimation(self, screen, dt):
        if not self.humanTurn():
            if self.aiMove is None:
                self.aiThinkTimer = 0.0
                self.aiMove = self.getAIMove()
                if self.aiMove == None:
                    return
            self.aiThinkTimer += dt
            if self.aiThinkTimer >= self.aiThinkDuration and self.aiMove is not None:
                self.applyMove(self.aiMove)
                self.aiMove = None
        else:
            for div, btn in self.divisionButtons:
                btn.draw(screen)

    def eventLoop(self, events):
        for event in events:
            if self.humanTurn() and self.aiMove is None:
                for div, btn in self.divisionButtons:
                    if btn.clicked(event):
                        self.applyMove(div)
                        return


class StartGameScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.fontTitle = pygame.font.SysFont("Roboto", 44, bold=True)
        self.font = pygame.font.SysFont("Roboto", 28)
        color = (20, 20, 20, 140)
        hover = (60, 60, 60, 180)
        
        self.bg = pygame.image.load("assets/banka.png").convert()
        self.bg = pygame.transform.scale(self.bg, (1280, 720))
        numbers = self.game.gameData.numbersToPlay
        self.numberButtons = []
        startX = 640 - (len(numbers) * 150) // 2
        for i, num in enumerate(numbers):
            button = Button(startX + i * 150, 350, 130, 70, str(num), color, hover)
            self.numberButtons.append((num, button))
        start_text = "Uzsāk Laupītājs" if self.game.gameData.startingPlayer == 0 else "Uzsāk Drošības Sistēma"
        self.startButton = Button(340, 480, 600, 50, start_text, color, hover)
        self.backButton = Button(540, 560, 200, 50, "Back", None, color)

    def bg_logic(self, screen):
        dark = 100
        screen.fill("black")
        screen.blit(self.bg, (0, 0))
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, dark))
        screen.blit(overlay, (0, 0))


    def playScreen(self, screen, dt, events):
        self.bg_logic(screen)
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

class EndScreen(Screen):
    def __init__(self, game, humanScore, aiScore, totalNodes=0, totalTreeNodes=0, avgMoveTime=0.0):
        super().__init__(game)
        self.humanScore = humanScore
        self.aiScore = aiScore
        self.totalNodes = totalNodes
        self.totalTreeNodes = totalTreeNodes
        self.avgMoveTime = avgMoveTime
        self.bg = pygame.image.load("assets/banka.png").convert()
        self.bg = pygame.transform.scale(self.bg, (1280, 720))
        self.initPyGameForSceen()

    def bg_logic(self, screen):
        dark = 100
        screen.fill("black")
        screen.blit(self.bg, (0, 0))
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, dark))
        screen.blit(overlay, (0, 0))


    def initPyGameForSceen(self):
        self.fontBig = pygame.font.SysFont("Roboto", 60, bold=True)
        self.font = pygame.font.SysFont("Roboto", 32)
        self.fontSmall = pygame.font.SysFont("Roboto", 26)
        color = (20, 20, 20, 140)
        self.menuButton = Button(540, 560, 220, 60, "Menu", None, color)
        self.restartButton = Button(540, 640, 220, 60, "Restart", None, color)

    def playScreen(self, screen, dt, events):
        self.bg_logic(screen)
        if self.humanScore > self.aiScore:
            result = "Tu aplaupīji banku!"
        elif self.humanScore < self.aiScore:
            result = "Tevi apturēja drošības sistēma!"
        else:
            result = "Tevi nepieķēra"
        txt = self.fontBig.render(result, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=(640, 220)))
        score = self.font.render(f"Cilvēks: {self.humanScore}   AI: {self.aiScore}", True, (255, 255, 255))
        screen.blit(score, score.get_rect(center=(640, 310)))
        nodes_txt = self.fontSmall.render(f"Novērtētās virsotnes: {self.totalNodes} no {self.totalTreeNodes}", True, (180, 180, 255))
        screen.blit(nodes_txt, nodes_txt.get_rect(center=(640, 390)))
        time_txt = self.fontSmall.render(f"Vidējais AI gājiena laiks: {self.avgMoveTime * 1000:.2f} ms", True, (180, 255, 180))
        screen.blit(time_txt, time_txt.get_rect(center=(640, 435)))
        self.menuButton.draw(screen)
        self.restartButton.draw(screen)
        for event in events:
            if self.menuButton.clicked(event):
                self.game.setScreen(IntroScreen(self.game))
            if self.restartButton.clicked(event):
                self.game.gameData.generateNumbers()
                self.game.setScreen(StartGameScreen(self.game))


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