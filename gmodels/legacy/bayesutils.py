"""
Utility functions for bayesian statistics
"""

import numpy as np

from enum import Enum


class Distribution(Enum):
    GAUSSIAN = 1
    LOGISTIC = 2
    GUMBEL = 3
    LAPLACE = 4


def px_given_y_gaussian(x_value, y_mean: float, y_stdev: float):
    """!
    """
    term = 1 / (np.sqrt(2 * np.pi) * y_stdev)
    exponent = np.exp((-((x_value - y_mean) ** 2)) / (2 * (y_stdev * y_stdev)))
    return term * exponent


def px_given_y_logistic(x_value, y_mean: float, y_stdev: float):
    """!
    \f$ \frac{e^{-(x-ymean)/s}}{s (1 + e^{-(x-ymean)/s)^2} \f$
    where \f$ s= \sqrt(3)/ \pi * y_stdev \f$
    taken from: https://en.wikipedia.org/wiki/Logistic_distribution
    """
    s = np.sqrt(3) / np.pi * y_stdev
    nominator = np.exp(-(x_value - y_mean) / s)
    denominator = s * (1 + nominator) ** 2
    return nominator / denominator


def px_given_y_gumbel(x_value, y_mean: float, y_stdev: float):
    """!
    \f$ 1/B * e^{-(z+e^{-z})} \f$
    where \f$ z = \frac{x - ymode}{B} \f$
    and \f$ B = \sqrt(6)/ np.pi * y_stdev \f$
    where \f$ ymode = y_mean - B * gamma \f$
    gamma is a constant as defined in :
    https://en.wikipedia.org/wiki/Euler%E2%80%93Mascheroni_constant

    Entire formula
    taken from: https://en.wikipedia.org/wiki/Gumbel_distribution
    """
    beta = np.sqrt(6) / np.pi * y_stdev
    GAMMA = 0.5772156649
    y_mode = y_mean - (beta * GAMMA)
    zeta = (x_value - y_mode) / beta
    return 1.0 / beta * np.exp(-(zeta + np.exp(-zeta)))


def px_given_y_laplace(x_value, y_mean: float, y_stdev: float):
    """!
    \f$ 1/2b * e^{- |xvalue - ymean| / b} \f$

    variance is b*b*2
    taken from: https://en.wikipedia.org/wiki/Laplace_distribution
    """
    variance = y_stdev ** 2
    b = np.sqrt(variance / 2)
    return np.exp(-np.abs(x_value - y_mean) / b) / (2 * b)


def px_given_y_discrete_uniform(total_values: float):
    return 1 / total_values
