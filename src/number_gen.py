import random


# https://docs.python.org/3/library/random.html

low_bound=20000
up_bound=30000


def generate_random(up=low_bound, low=up_bound):
    return random.randint(up, low)
    


def simple_gen():
    rand = generate_random()
    while (rand % 2 != 0 or rand % 3 != 0):
        rand = generate_random()
    return rand


def one_nine_gen():
    value = generate_random(1, 9)
    multi = generate_random(2, 4)
    while (value * multi < up_bound):
        value *= multi
        multi = generate_random(2, 4)
        if (value >= low_bound and value <= up_bound):
            break
    if (value <= low_bound or value >= up_bound):
        value = one_nine_gen()
    return value

print(one_nine_gen())
print(simple_gen())




