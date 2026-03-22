import math

from src.game_logic import possible_divisions, result_of_turn, is_game_over


# aprekinam punktu starpibu no ai skatu punkta
def score_difference(state, ai_player):
    # ja ai ir pirmais speletajs
    if ai_player == 0:
        return state[1] - state[2]
    # ja ai ir otrais speletajs
    else:
        return state[2] - state[1]


# alfa-beta algoritms atgriez labako gajienu dotaja stavokli
def alpha_beta_search(state, ai_player):
    result = max_value(state, -math.inf, math.inf, ai_player)
    best_move = result[1]
    return best_move


# max dala - ai gajiens, mekle lielako vertibu
def max_value(state, alpha, beta, ai_player):
    if is_game_over(state):
        return score_difference(state, ai_player), None

    best_value = -math.inf
    best_move = None

    for divisor in possible_divisions(state):
        new_state = result_of_turn(state, divisor)
        value = min_value(new_state, alpha, beta, ai_player)[0]

        if value > best_value:
            best_value = value
            best_move = divisor

        alpha = max(alpha, best_value)

        # nogriez liekos zarus
        if beta <= alpha:
            break

    return best_value, best_move


# min dala - cilveka gajiens, mekle mazako vertibu
def min_value(state, alpha, beta, ai_player):
    if is_game_over(state):
        return score_difference(state, ai_player), None

    best_value = math.inf
    best_move = None

    for divisor in possible_divisions(state):
        new_state = result_of_turn(state, divisor)
        value = max_value(new_state, alpha, beta, ai_player)[0]

        if value < best_value:
            best_value = value
            best_move = divisor

        beta = min(beta, best_value)

        # nogriez liekos zarus
        if beta <= alpha:
            break

    return best_value, best_move
