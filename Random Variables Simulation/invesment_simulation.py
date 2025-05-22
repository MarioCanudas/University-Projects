# Assume that a person saves a monthly amount of money that is distributed
# according to an exponential random variable with a mean of 1000 pesos.
# The money is deposited at the beginning of the month into an investment fund
# to generate returns, which are paid at the end of the month and deposited
# into the same fund for reinvestment. The fund generates random monthly
# returns according to a Beta(1, 6) distribution.

from random import random
import pandas as pd
import numpy as np
from scipy.stats import norm
from exponential import exp_simulation

def beta_dist_1_6_inverse(u: float) -> float:
  """
  Calculates the inverse of the beta(1,6) distribution, given u
  """
  return 1 - (1 - u)**(1/6) if 0 <= u <= 1 else 0

def beta_dist_1_6_simulation() -> float:
  """
  Simulates a beta(1,6) random variable using the inverse transform method
  """
  return beta_dist_1_6_inverse(random())

def investment_simulation(months: int) -> pd.DataFrame:
  """
  Simulates an investment for a given number of months
  """
  df = {'month': [], 'saved': [], 'return': [], 'generated': [], 'accumulated': []}

  valor_acumulado = 0

  for month in range(1, months + 1):
    df['month'].append(month)

    ahorrado = exp_simulation(1/1000)
    df['saved'].append(ahorrado)

    return_ = beta_dist_1_6_simulation()
    df['return'].append(return_)

    generated = (valor_acumulado + ahorrado)*return_
    df['generated'].append(generated)

    valor_acumulado = (valor_acumulado + ahorrado)*(1 + return_)
    df['accumulated'].append(valor_acumulado)

  return pd.DataFrame(df)

def accumulated_saved_simulation(months: int):
  accumulated = 0

  for month in range(1, months + 1):
    saved = exp_simulation(1/1000)
    rate_of_return = beta_dist_1_6_simulation()
    accumulated = (accumulated + saved)*(1 + rate_of_return)

  return accumulated

def accumulated_saved_average_simulation(confidence: float):
  accumulated = np.array([])

  coef_conf = 1 - confidence
  z = norm.ppf(1 - coef_conf/2)

  error = 10000

  while error > 5000:
    accumulated_final = accumulated_saved_simulation(36)

    accumulated = np.append(accumulated, accumulated_final)

    n = len(accumulated)

    mean = np.mean(accumulated)
    s = np.std(accumulated)

    error = z * s / (n ** 0.5) if n > 1 else error

  return mean, error, n