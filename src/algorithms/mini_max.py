import math
# pa cik Ai uzvar
from src.algorithms.alfa_beta import score_difference
from src.algorithms.heuristic import heuristic

node_count = 0

# minimax algoritms atgriež labāko gājienu dotajā stāvoklī

def minimax_search(gameState, state, ai_player):
    global node_count
    node_count = 0
    result = max_value(gameState, state, ai_player, 0)
    best_move = result[1]
    return best_move, node_count

#iziet cauri visiem iespējamiem gājieniem un izvēlas to, kas dod vislabāko rezultātu

def max_value(gameState, state, ai_player, depth):
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
        value = min_value(gameState, new_state, ai_player, depth + 1)[0]
        if value > best_value:
            best_value = value
            best_move = divisor

    return best_value, best_move

#iziet cauri visiem iespējamiem gājieniem un izvēlas to, kas dod visliktāko rezultātu

def min_value(gameState, state, ai_player, depth):
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
        value = max_value(gameState, new_state, ai_player, depth + 1)[0]
        if value < best_value:
            best_value = value
            best_move = divisor

    return best_value, best_move