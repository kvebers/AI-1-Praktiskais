from config import config

class GameState():
    def __init__(self):
        self.NUMBER = 0 # Tagadējais cipars
        self.P1_SCORE = 1 # Pirmā spēlētāja punkti
        self.P2_SCORE = 2 # Otrā spēlētāja punkti
        self.BANK_SCORE = 3 # Bankas punkti
        self.TURN = 4 # Kuram spēlētājam ir gājiens
        self.DIVISORS = config["divisors"]
        self.BANK_DIVISORS = config["bankDivisors"]
        self.maxDepth = config["maxDepth"]


    def init_state(self, start_number, starting_player=0):
        return (start_number, 0, 0, 0, starting_player)

    def whose_turn(self, state):
        return state[self.TURN]

    def possible_divisions(self, state):
        number = state[self.NUMBER]
        if number <= 10:
            return []
        possible = []
        
        for divisor in self.DIVISORS:
            if number % divisor == 0:
                possible.append(divisor)
        return possible

    #pārbauda vai spēle ir beigusies

    def is_game_over(self, state):
        if state[self.NUMBER] <= 10:
            return True

        return len(self.possible_divisions(state)) == 0

    #piešķir bankas punktus, ja spēle beidzas spēlētājam, kuram bija pēdējais gājiens

    def give_bank_score(self, state):
        number = state[self.NUMBER]
        p1_score = state[self.P1_SCORE]
        p2_score = state[self.P2_SCORE]
        bank_score = state[self.BANK_SCORE]
        turn = state[self.TURN]

        if bank_score > 0:
            if turn == 0:
                p2_score += bank_score
            else:
                p1_score += bank_score
            bank_score = 0
        return (number, p1_score, p2_score, bank_score, turn)

    def result_of_turn(self, state, divisor):
        number = state[self.NUMBER]
        p1_score = state[self.P1_SCORE]
        p2_score = state[self.P2_SCORE]
        bank_score = state[self.BANK_SCORE]
        turn = state[self.TURN]

        if self.is_game_over(state):
            raise ValueError("game is over")
        
        if divisor not in self.possible_divisions(state):
            raise ValueError("Invalid turn, number is not divisible by divisor") #
                                                                                                            
        new_number = number // divisor

        score_change = 1 if (new_number % 2 == 1) else -1
        if turn == 0:
            p1_score += score_change
        else:
            p2_score += score_change

        if new_number % 10 in self.BANK_DIVISORS:
            bank_score += 1

        next_turn = 1 if turn == 0 else 0
        new_state = (new_number, p1_score, p2_score, bank_score, next_turn)

        if self.is_game_over(new_state):
            new_state = self.give_bank_score(new_state)
        
        return new_state