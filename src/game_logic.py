from config import config

NUMBER = 0 # Tagadējais cipars
P1_SCORE = 1 # Pirmā spēlētāja punkti
P2_SCORE = 2 # Otrā spēlētāja punkti
BANK_SCORE = 3 # Bankas punkti
TURN = 4 # Kuram spēlētājam ir gājiens

DIVISORS = config["divisors"]
BANK_DIVISORS = config["bankDivisors"]

def init_state(start_number, starting_player=1):
    return (start_number, 0, 0, 0, starting_player)

def whose_turn(state):
    return state[TURN]

def possible_divisions(state):
    number = state[NUMBER]
    if number <= 10:
        return []
    possible = []
    
    for divisor in DIVISORS:
        if number % divisor == 0:
            possible.append(divisor)
    return possible

def is_game_over(state):
    if state[NUMBER] <= 10:
        return True

    return len(possible_divisions(state)) == 0

def give_bank_score(state):
    number = state[NUMBER]
    p1_score = state[P1_SCORE]
    p2_score = state[P2_SCORE]
    bank_score = state[BANK_SCORE]
    turn = state[TURN]

    if bank_score > 0:
        if turn == 1:
            p2_score += bank_score
        else:
            p1_score += bank_score
        bank_score = 0
    return (number, p1_score, p2_score, bank_score, turn)

def result_of_turn(state, divisor):
    number = state[NUMBER]
    p1_score = state[P1_SCORE]
    p2_score = state[P2_SCORE]
    bank_score = state[BANK_SCORE]
    turn = state[TURN]

    if is_game_over(state):
        raise ValueError("game is over")
    
    if divisor not in possible_divisions(state):
        raise ValueError("Invalid turn, number is not divisible by divisor")
                                                                                                        
    new_number = number // divisor

    score_change = 1 if (new_number % 2 == 1) else -1
    if turn == 1:
        p1_score += score_change
    else:
        p2_score += score_change

    if new_number % 10 in BANK_DIVISORS:
        bank_score += 1

    next_turn = 2 if turn == 1 else 1
    new_state = (new_number, p1_score, p2_score, bank_score, next_turn)

    if is_game_over(new_state):
        new_state = give_bank_score(new_state)
    
    return new_state