from random import random


def random_decision(probability):
    return random() >= 0.5 - (min(probability, 1.0) / 2)
