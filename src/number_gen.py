import random
from config import config


# https://docs.python.org/3/library/random.html
upBound=config['upperBound']
lowBound=config['lowerBound']


def generateRandom(low=lowBound, up=upBound):
    return random.randint(low, up)
    
def simpleGen():
    rand = generateRandom()
    while (rand % 2 != 0 or rand % 3 != 0):
        rand = generateRandom()
    return rand


def oneNineGen():
    value = generateRandom(1, 9)
    multi = generateRandom(2, 4)
    while (value * multi < upBound):
        value *= multi
        multi = generateRandom(2, 4)
        if (value >= lowBound and value <= upBound):
            break
    if (value <= lowBound or value >= upBound):
        value = oneNineGen()
    return value




