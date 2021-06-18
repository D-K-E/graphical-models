"""!
Different types or aliases for codomains of pgm objects
"""

from typing import Callable, Set, Any, List, Dict, FrozenSet, Tuple

NumericValue = float


class Outcome:
    def __init__(self, v):
        self = v


class CodomainValue:
    def __init__(self, v):
        self = v


class PossibleOutcomes:
    """!
    \brief set of possible outcomes from Koller, Friedman 2009, p. 15, 20

    This is simply a frozenset. We assume that possible outcomes contained in
    this object are measurable.
    """

    def __init__(self, omega: FrozenSet[Outcome]):
        self.data = omega
