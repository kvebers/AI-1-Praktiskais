import math 
import sys
import os

from src.game_logic import possible_divisions, result_of_turn, is_game_over
# pa cik Ai uzvar
def score_difference(state): 
    return state[1] - state[2]

# minimax algoritms atgriež labāko gājienu dotajā stāvoklī

def minimax_search(state):
    result = max_value(state)
    best_move = result[1]
    return best_move

#iziet cauri visiem iespējamiem gājieniem un izvēlas to, kas dod vislabāko rezultātu

def max_value(state):
    if is_game_over(state):
        return score_difference(state), None
    best_value = -math.inf
    best_move = None

    for divisor in possible_divisions(state):
        new_state = result_of_turn(state, divisor)
        value = min_value(new_state)[0]
        if value > best_value:
            best_value = value
            best_move = divisor

    return best_value, best_move
        
#iziet cauri visiem iespējamiem gājieniem un izvēlas to, kas dod visliktāko rezultātu

def min_value(state):
    if is_game_over(state):
        return score_difference(state), None
    best_value = math.inf
    best_move = None

    for divisor in possible_divisions(state):
        new_state = result_of_turn(state, divisor)
        value = max_value(new_state)[0]
        if value < best_value:
            best_value = value
            best_move = divisor

    return best_value, best_move