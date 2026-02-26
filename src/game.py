from config import config



class GameData():
    def __init__(self):
        self.mode = "minimax" # alfa-beta
        self.start = 0 # 0 is player
        self.number = config['gen_algorithm']
        print("Game Script is running")