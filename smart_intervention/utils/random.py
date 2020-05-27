from random import random


def random_decision(rand_rate):
    """
    :param rand_rate: (-1,1) rate, which may swing the choice to either side
    :return: a random choice based on rate
    """
    true_rate = rand_rate / 2
    return random() >= 0.5 + true_rate
