# src/game.py
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
from src.game_logic import possible_divisions, result_of_turn, is_game_over


# -----------------------------
# Data
# -----------------------------
class GameData():
    def __init__(self):
        self.mode = config["algorithm"]
        self.startingPlayer = config["start"]
        self.genAlgorithm = config['genAlgorithm'] # start number
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
        self.generateTree(number)


    def generateTree(self, number):
        self.head = Node(number=number)
        print(number)
        self._recursiveTree(self.head)

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
        self.startButton = Button(800, 520, 300, 60, "Start Game", None, color)
        self.castButton = Button(800, 590, 300, 60, "CAST", None, color)
        self.settingsButton = Button(800, 660, 300, 60, "Settings", None, color)

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

        for event in events:
            if self.startButton.clicked(event):
                self.game.setScreen(GameScreen(self.game))
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
    def __init__(self, game):
        super().__init__(game)
        self.fontTitle = pygame.font.SysFont("Roboto", 44, bold=True)
        self.font = pygame.font.SysFont("Roboto", 28)

        # Background bilde: assets/banka.png (fallback, ja nav)
        self.bg = None
        try:
            self.bg = pygame.image.load("assets/banka.png").convert()
            self.bg = pygame.transform.scale(self.bg, (1280, 720))
        except Exception:
            self.bg = None

        # RobBanks bilde AI animācijai
        self.rob = pygame.image.load("assets/RobBanks.png").convert_alpha()
        self.rob = pygame.transform.smoothscale(self.rob, (260, 340))

        # spēles stāvoklis
        self.numbers = [4, 9, 1, 7, 8, 2, 6, 3, 5, 0, 9, 4]
        self.humanScore = 0
        self.aiScore = 0
        self.turn = "HUMAN"
        self.lastMoveText = ""

        # pogas
        color = (20, 20, 20, 140)
        self.restartButton = Button(80, 620, 220, 60, "Restart", None, color)
        self.menuButton = Button(320, 620, 220, 60, "Menu", None, color)

        # monētu rinda
        self.startX = 90
        self.startY = 330
        self.cell = 80
        self.gap = 18

        # AI animācija
        self.ai_anim = None  # dict vai None

    # zelta monēta (vienkāršs gradients)
    def draw_coin(self, screen, center, radius, value, alpha=255):
        cx, cy = center

        for i in range(radius, 0, -4):
            t = i / radius
            r = int(255 * (0.75 + 0.25 * (1 - t)))
            g = int(215 * (0.75 + 0.25 * (1 - t)))
            b = int(40 * 0.9)
            col = (min(255, r), min(255, g), b, alpha)
            surf = pygame.Surface((i * 2, i * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, col, (i, i), i)
            screen.blit(surf, (cx - i, cy - i))

        ring = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(ring, (255, 245, 180, alpha), (radius + 3, radius + 3), radius + 3, 3)
        screen.blit(ring, (cx - radius - 3, cy - radius - 3))

        txt = self.fontTitle.render(str(value), True, (30, 20, 0))
        tr = txt.get_rect(center=(cx, cy))
        screen.blit(txt, tr)

    def coin_center(self, idx):
        x = self.startX + idx * (self.cell + self.gap) + self.cell // 2
        y = self.startY + self.cell // 2
        return (x, y)

    def get_clicked_end(self, pos):
        if len(self.numbers) == 0:
            return None
        left_center = self.coin_center(0)
        right_center = self.coin_center(len(self.numbers) - 1)
        r = self.cell // 2

        if (pos[0] - left_center[0]) ** 2 + (pos[1] - left_center[1]) ** 2 <= r * r:
            return "L"
        if (pos[0] - right_center[0]) ** 2 + (pos[1] - right_center[1]) ** 2 <= r * r:
            return "R"
        return None

    def apply_move_pop(self, side):
        return self.numbers.pop(0) if side == "L" else self.numbers.pop()

    def check_end(self):
        if len(self.numbers) == 0:
            self.game.setScreen(EndScreen(self.game, self.humanScore, self.aiScore))

    def ai_choose_move(self):
        # pagaidām greedy (vēlāk pieslēgsiet minimax/alphabeta)
        left = self.numbers[0]
        right = self.numbers[-1]
        return "L" if left >= right else "R"

    def start_ai_animation(self, side):
        idx = 0 if side == "L" else (len(self.numbers) - 1)
        start = self.coin_center(idx)

        end = (1080, 150)  # AI score zona labajā pusē

        rob_start = (900, 220)
        rob_end = (980, 160)

        value = self.numbers[idx]

        self.ai_anim = {
            "side": side,
            "value": value,
            "t": 0.0,
            "dur": 0.75,
            "start": start,
            "end": end,
            "rob_start": rob_start,
            "rob_end": rob_end,
        }

    def update_ai_animation(self, dt):
        a = self.ai_anim
        if not a:
            return

        a["t"] += dt
        if a["t"] >= a["dur"]:
            v = self.apply_move_pop(a["side"])
            self.aiScore += v
            self.lastMoveText = f"AI stole {v} from {'LEFT' if a['side']=='L' else 'RIGHT'}"
            self.ai_anim = None
            self.check_end()
            self.turn = "HUMAN"

    def draw_hud(self, screen):
        title = self.fontTitle.render("ROB BANKS: NUMBER HEIST", True, (255, 255, 255))
        screen.blit(title, (70, 30))

        human = self.font.render(f"Human: {self.humanScore}", True, (255, 255, 255))
        ai = self.font.render(f"AI: {self.aiScore}", True, (255, 255, 255))
        screen.blit(human, (70, 90))
        screen.blit(ai, (1020, 90))

        turn = self.font.render(f"Turn: {self.turn}", True, (240, 240, 240))
        screen.blit(turn, (70, 130))

        log = self.font.render(self.lastMoveText, True, (220, 220, 220))
        screen.blit(log, (70, 170))

    def draw_row(self, screen):
        for i, v in enumerate(self.numbers):
            # ja AI animē, ne-zīmē animēto monētu rindā
            if self.ai_anim:
                idx_anim = 0 if self.ai_anim["side"] == "L" else (len(self.numbers) - 1)
                if i == idx_anim:
                    continue

            center = self.coin_center(i)
            clickable = (self.turn == "HUMAN") and (i == 0 or i == len(self.numbers) - 1)
            r = self.cell // 2

            if clickable:
                glow = pygame.Surface((r * 2 + 20, r * 2 + 20), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 215, 0, 70), (r + 10, r + 10), r + 10)
                screen.blit(glow, (center[0] - r - 10, center[1] - r - 10))

            self.draw_coin(screen, center, r, v)

    def draw_ai_anim(self, screen):
        a = self.ai_anim
        if not a:
            return

        p = max(0.0, min(1.0, a["t"] / a["dur"]))
        p = p * p * (3 - 2 * p)  # smoothstep

        sx, sy = a["start"]
        ex, ey = a["end"]
        cx = sx + (ex - sx) * p
        cy = sy + (ey - sy) * p

        alpha = int(255 * (1 - p))

        # monēta kustībā
        self.draw_coin(screen, (int(cx), int(cy)), self.cell // 2, a["value"], alpha=alpha)

        # RobBanks kustībā
        rsx, rsy = a["rob_start"]
        rex, rey = a["rob_end"]
        rx = rsx + (rex - rsx) * p
        ry = rsy + (rey - rsy) * p

        rob_surf = self.rob.copy()
        rob_surf.set_alpha(max(0, min(255, int(255 * (0.4 + 0.6 * (1 - p))))))
        screen.blit(rob_surf, (int(rx), int(ry)))

    def playScreen(self, screen, dt, events):
        # fons
        if self.bg:
            screen.blit(self.bg, (0, 0))
            overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 110))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill((15, 15, 20))

        self.draw_hud(screen)
        self.draw_row(screen)

        self.restartButton.draw(screen)
        self.menuButton.draw(screen)

        # AI kārta -> animācija
        if self.turn == "AI":
            if self.ai_anim is None:
                side = self.ai_choose_move()
                self.start_ai_animation(side)
            self.update_ai_animation(dt)

        # zīmē animāciju virsū
        self.draw_ai_anim(screen)

        # input
        for event in events:
            if self.restartButton.clicked(event):
                self.game.setScreen(GameScreen(self.game))
                return
            if self.menuButton.clicked(event):
                self.game.setScreen(IntroScreen(self.game))
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.turn == "HUMAN" and self.ai_anim is None:
                    side = self.get_clicked_end(event.pos)
                    if side:
                        v = self.apply_move_pop(side)
                        self.humanScore += v
                        self.lastMoveText = f"Human stole {v} from {'LEFT' if side=='L' else 'RIGHT'}"
                        self.check_end()
                        if len(self.numbers) > 0:
                            self.turn = "AI"


# -----------------------------
# End screen
# -----------------------------
class EndScreen(Screen):
    def __init__(self, game, humanScore, aiScore):
        super().__init__(game)
        self.humanScore = humanScore
        self.aiScore = aiScore
        self.fontBig = pygame.font.SysFont("Roboto", 60, bold=True)
        self.font = pygame.font.SysFont("Roboto", 32)

        color = (20, 20, 20, 140)
        self.menuButton = Button(540, 520, 220, 60, "Menu", None, color)
        self.restartButton = Button(540, 600, 220, 60, "Restart", None, color)

    def playScreen(self, screen, dt, events):
        screen.fill((0, 0, 0))

        if self.humanScore > self.aiScore:
            result = "YOU WIN!"
        elif self.humanScore < self.aiScore:
            result = "AI WINS!"
        else:
            result = "DRAW!"

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
                self.game.setScreen(GameScreen(self.game))


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
