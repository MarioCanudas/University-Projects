from random import random
from math import comb

def binomial_mass(x: int, n: int, p: float) -> float:
    """
    Calculates the probability mass function of a binomial distribution, given x, n and p
    """
    return comb(n, x)*(p**x)*((1 - p)**(n - x)) if 0 <= x <= n else 0

def binomial_simulation(n: int, p: float) -> int:
    """
    Simulates a binomial random variable with parameters n and p using the inverse transform method
    """
    num = random() 
    prob = 0

    for i in range(n + 1):
        prob += binomial_mass(i, n, p) 

        if num < prob:
            return i