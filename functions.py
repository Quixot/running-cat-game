import random

def random_even(min_val, max_val):
    while True:
        num = random.randint(min_val, max_val)
        if num % 2 == 0:
            return num