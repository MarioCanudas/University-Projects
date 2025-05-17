from math import log
from random import random

def exp_dist_inverse(u: float, lambda_: float) -> float:
    """
    Calculates the inverse of the exponential distribution, given u and lambda
    """
    return -log(1 - u)/lambda_

def exp_simulation(lambda_: float) -> float:
    """
    Simulates an exponential random variable with parameter lambda using the inverse transform method
    """
    return exp_dist_inverse(random(), lambda_)