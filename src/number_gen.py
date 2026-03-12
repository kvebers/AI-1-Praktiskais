import random
from config import config


# https://docs.python.org/3/library/random.html
low_bound=config['upperBound']
up_bound=config['lowerBound']


def generateRandom(up=low_bound, low=up_bound):
    return random.randint(up, low)
    
def simpleGen():
    rand = generateRandom()
    while (rand % 2 != 0 or rand % 3 != 0):
        rand = generateRandom()
    return rand


def oneNineGen():
    value = generateRandom(1, 9)
    multi = generateRandom(2, 4)
    while (value * multi < up_bound):
        value *= multi
        multi = generateRandom(2, 4)
        if (value >= low_bound and value <= up_bound):
            break
    if (value <= low_bound or value >= up_bound):
        value = oneNineGen()
    return value




