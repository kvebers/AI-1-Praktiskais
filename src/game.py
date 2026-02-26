from config import config



class GameData():
    def __init__(self):
        self.mode = "minimax" # alfa-beta
        self.start = 0 # 0 is player
        self.number = config['gen_algorithm']
        self.nodes = []
        self.player_score_1 = 0
        self.player_score_2 = 0
        print("Game Script is running")

