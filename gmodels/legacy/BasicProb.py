"""
Simple probability structures
"""
Omega = set(["d", "a", "b", "c"])
M = set([1, 2, 3, 46, 42.0, 1.0, 0.465])

# -----------------------------------
"""
P(Omega, M):

    - P(a) >= 0 \forall a \in M
    - P(Omega) = 1
    - a,b \in M a \cap b = \emptyset, P(a \cup b) = P(a) + P(b)

p(a|b) = p(a \cap b) / p(a)

p(a \cap b) = p(a) p(a|b) = p(b) p(b|a)

Chain rule:
p(a_1, \cap ..., \cap a_n) = p(a_1) p(a_2 | a_1) ... p(a_n | a_1 \cap ..., \cap a_{n-1})

Bayes rule:
    p(a|b) = p(b|a) p(a)/ p(b)

Random Variables
"""
a = 1
b = 486

import random


def X():
    return random.choice([1, 58, 6, 89, 123, 9, 13, 89, 4])


"""
p(X): marginal distribution
"""


def Y():
    return random.choice(["a", "b", "c", "d"])


"""
P(X,Y): joint distribution

bayes rule:
P(X | Y): P(X) P(Y | X) / P(Y)


P(a \perp b) \iff P(a|b) = p(a)
P(a \perp b) \iff P( a \cap b) = P(a) P(b)
P(X \perp Y) \iff P(X, Y) = P(X) P(Y)

P(a \perp b | g) = P(a | g) P(b | g)
P(X \perp Y | Z) = P(X | Z) P(Y | Z)
"""


def YAD():
    return random.choice(["islak", "kuru", "lavli", "temiz", "pis"])


def HAD():
    return random.choice(["yagmurlu", "gunesli", "soguk", "sicak"])


"""
Probability query
P(YAD = islak | HAD = yagmurlu) = P(YAD) P(HAD | YAD) / P(HAD)

Maximum likelihood query
P(YAD = [islak, kuru,...] | HAD = yagmurlu) = P(YAD) P(HAD | YAD) / P(HAD)
"""
