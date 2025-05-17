from random import random

def geometric_mass(x: int, p: float) -> float:
    """
    Calculates the probability mass function of a geometric distribution, given x and p
    """
    return p*((1 - p)**(x - 1)) if x >= 1 else 0

def geometric_simulation(p: float) -> int:
    """
    Simulates a geometric random variable with parameter p using the inverse transform method
    """
    num = random() 
    prob = 0

    x = 1
    while not num < prob:
        prob += geometric_mass(x, p)
        x += 1

    return x