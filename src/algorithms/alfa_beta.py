import math
from src.algorithms.heuristic import heuristic

node_count = 0


def score_difference(gameState, state, ai_player):
    if ai_player == 0:
        return state[gameState.P1_SCORE] - state[gameState.P2_SCORE]
    else:
        return state[gameState.P2_SCORE] - state[gameState.P1_SCORE]


# alpha-beta algoritms atgriež labāko gājienu dotajā stāvoklī
def alpha_beta_search(gameState, state, ai_player):
    global node_count
    node_count = 0
    result = max_value(gameState, state, -math.inf, math.inf, ai_player, 0)
    best_move = result[1]
    return best_move, node_count


# iziet cauri visiem iespējamajiem gājieniem un izvēlas to, kas dod vislabāko rezultātu
def max_value(gameState, state, alpha, beta, ai_player, depth):
    global node_count
    node_count += 1

    if gameState.is_game_over(state):
        return score_difference(gameState, state, ai_player), None
    if depth >= gameState.maxDepth:
        return heuristic(gameState, state, ai_player), None

    best_value = -math.inf
    best_move = None

    for divisor in gameState.possible_divisions(state):
        new_state = gameState.result_of_turn(state, divisor)
        value = min_value(gameState, new_state, alpha, beta, ai_player, depth + 1)[0]

        if value > best_value:
            best_value = value
            best_move = divisor

        alpha = max(alpha, best_value)

        if beta <= alpha:
            break

    return best_value, best_move


# iziet cauri visiem iespējamajiem gājieniem un izvēlas to, kas dod visliktāko rezultātu
def min_value(gameState, state, alpha, beta, ai_player, depth):
    global node_count
    node_count += 1

    if gameState.is_game_over(state):
        return score_difference(gameState, state, ai_player), None
    if depth >= gameState.maxDepth:
        return heuristic(gameState, state, ai_player), None

    best_value = math.inf
    best_move = None

    for divisor in gameState.possible_divisions(state):
        new_state = gameState.result_of_turn(state, divisor)
        value = max_value(gameState, new_state, alpha, beta, ai_player, depth + 1)[0]

        if value < best_value:
            best_value = value
            best_move = divisor

        beta = min(beta, best_value)

        if beta <= alpha:
            break

    return best_value, best_move