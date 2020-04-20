import random


def pick_random(collection):
    choice = random.randrange(len(collection))
    try:
        return collection[choice]
    except KeyError:
        collection = list(collection)  # Sometimes we need an explicit cast
        return collection[choice]


def generate_n(constructor, n=0):
    return [constructor(i) for i in range(n)]
