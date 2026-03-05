class Node():
    def __init__(self, number, player, score, move_used=None, parent=None):
        self.number = number
        self.player = player
        self.score = score
        self.move_used = move_used
        self.parent = parent
        self.children = []
        self.algorithm_value = None
        