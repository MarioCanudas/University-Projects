from random import random
from math import exp
from exponential import exp_simulation

def f(x: float) -> float:
    """
    Calculates the probability density function of the gamma(3,1) distribution, given x
    """
    return (1/2)*(x**2)*(exp(-x))

def g(x: float) -> float:
    """
    Calculates the probability density function of the exponential(1/2) distribution, given x
    """
    return (1/2)*(exp(-x/2))

def gamma_3_1_simulation() -> float:
    """
    Simulates a gamma(3,1) random variable using the acceptance-rejection method
    """
    c = 16*exp(-2)

    while True:
        num_sim = exp_simulation(1/2)
        U = random()

        if U < f(num_sim)/(g(num_sim)*c):
            return num_sim