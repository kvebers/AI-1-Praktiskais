import math
from src.graph import Node
from src.algorithms.heuristic import heuristic


# parveido node uz state tuple, ja vajag
def to_state(position):
    if isinstance(position, Node):
        return (position.number, position.score[0], position.score[1], position.bank, position.player)
    return position


# aprekinam punktu starpibu no ai skatu punkta
def score_difference(gameState, position, ai_player):
    state = to_state(position)
    if ai_player == 0:
        return state[gameState.P1_SCORE] - state[gameState.P2_SCORE]
    else:
        return state[gameState.P2_SCORE] - state[gameState.P1_SCORE]

# izveido bernus atkariba no ta, kas tiek padots ieksa
def get_children(gameState, position):
    state = to_state(position)

    if isinstance(position, Node):
        if len(position.children) > 0:
            return position.children

        children = []

        for divisor in gameState.possible_divisions(state):
            new_state = gameState.result_of_turn(state, divisor)

            child = Node(
                number=new_state[0],
                player=new_state[4],
                score=[new_state[1], new_state[2]],
                bank=new_state[3],
                moveUsed=divisor,
                parent=position
            )

            children.append(child)

        position.children = children
        return children

    children = []
    for divisor in gameState.possible_divisions(state):
        new_state = gameState.result_of_turn(state, divisor)
        children.append((divisor, new_state))

    return children


# galvena funkcija, kas atrod labako gajenu ai
def alpha_beta_search(gameState, position, ai_player=0):
    _, best_move = max_value(gameState, position, -math.inf, math.inf, ai_player, 0)
    return best_move


# max dala - ai gajiens, mekle lielako vertibu
def max_value(gameState, position, alpha, beta, ai_player, depth):
    state = to_state(position)

    # ja spele ir beigusies, atgriezam gala vertibu
    if gameState.is_game_over(state):
        value = score_difference(gameState, position, ai_player)

        # ja stradam ar node, saglabajam vertibu mezgla
        if isinstance(position, Node):
            position.algorithmValue = value

        return value, None

    if depth >= gameState.maxDepth:
        value = heuristic(gameState, state, ai_player)
        if isinstance(position, Node):
            position.algorithmValue = value
        return value, None

    # sakuma labakais rezultats ir loti mazs
    best_score = -math.inf
    best_move = None

    # iegustam visus nakamos bernus
    children = get_children(gameState, position)

    for child in children:
        # ja stradam ar node, gajiens ir child.moveUsed
        if isinstance(position, Node):
            next_position = child
            move_used = child.moveUsed
        else:
            # ja stradam ar state, child ir (divisor, state)
            move_used, next_position = child

        # pec ai gajiena nakamais ir cilveks
        score = min_value(gameState, next_position, alpha, beta, ai_player, depth + 1)[0]

        # ja atrasts labaks rezultats, saglabajam to
        if score > best_score:
            best_score = score
            best_move = move_used

        # atjaunojam alpha robezu
        alpha = max(alpha, best_score)

        # ja beta <= alpha, talakos zarus nav jegas skatities
        if beta <= alpha:
            break

    # ja stradam ar node, saglabajam algoritma vertibu mezgla
    if isinstance(position, Node):
        position.algorithmValue = best_score

    return best_score, best_move


# min dala - cilveka gajiens, mekle mazako vertibu
def min_value(gameState, position, alpha, beta, ai_player, depth):
    state = to_state(position)

    # ja spele ir beigusies, atgriezam gala vertibu
    if gameState.is_game_over(state):
        value = score_difference(gameState, position, ai_player)

        # ja stradam ar node, saglabajam vertibu mezgla
        if isinstance(position, Node):
            position.algorithmValue = value

        return value, None

    if depth >= gameState.maxDepth:
        value = heuristic(gameState, state, ai_player)
        if isinstance(position, Node):
            position.algorithmValue = value
        return value, None

    # sakuma labakais rezultats ir loti liels
    best_score = math.inf
    best_move = None

    # iegustam visus nakamos bernus
    children = get_children(gameState, position)

    for child in children:
        # ja stradam ar node, gajiens ir child.moveUsed
        if isinstance(position, Node):
            next_position = child
            move_used = child.moveUsed
        else:
            # ja stradam ar state, child ir (divisor, state)
            move_used, next_position = child

        # pec cilveka gajiena nakamais ir ai
        score = max_value(gameState, next_position, alpha, beta, ai_player, depth + 1)[0]

        # cilveks izvelas ai sliktako variantu
        if score < best_score:
            best_score = score
            best_move = move_used

        # atjaunojam beta robezu
        beta = min(beta, best_score)

        # ja beta <= alpha, talakos zarus nav jegas skatities
        if beta <= alpha:
            break

    # ja stradam ar node, saglabajam algoritma vertibu mezgla
    if isinstance(position, Node):
        position.algorithmValue = best_score
    return best_score, best_move