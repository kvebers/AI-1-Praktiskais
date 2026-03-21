

def heuristic(gameState, state, ai_player):
    numb = state[gameState.NUMBER]
    ai = state[gameState.P2_SCORE]
    robber = state[gameState.P1_SCORE]
    bank = state[gameState.BANK_SCORE]
    if (ai_player):
        ai = state[gameState.P1_SCORE]
        robber = state[gameState.P2_SCORE]
    diff = ai - robber
    return heuristic_helper(numb, bank, diff, gameState.DIVISORS)

def heuristic_helper(numb, bank, diff, div):
    endGameCoefficientMagicNumber = 30
    value = 0
    for devision in div:
        if numb % devision == 0 and numb // devision % 2 == 1:
            value += 1
            break
    value += 10 if numb < endGameCoefficientMagicNumber else 0
    value += bank
    value += diff
