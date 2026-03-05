class Node():
    def __init__(self, number, player, score, moveUsed=None, parent=None):
        self.number = number
        self.player = player
        self.score = score
        self.moveUsed = moveUsed
        self.parent = parent
        self.children = []
        self.algorithmValue = None