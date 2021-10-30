"""!
\file codomain.py Represents a codomain of a function. Since we are dealing
with probabilities and related concepts the codomain should be a measurable
value
"""

from typing import Any, Callable, Dict, FrozenSet, List, Set, Tuple

from pygmodels.value.value import SetValue


class Outcome:
    def __init__(self, v):
        self.data = v


CodomainValue = SetValue
Codomain = Set[CodomainValue]
OrderedCodomain = List[CodomainValue]

FiniteCodomain = FrozenSet[CodomainValue]
OrderedFiniteCodomain = Tuple[CodomainValue]


class PossibleOutcomes:
    """!
    \brief set of possible outcomes from Koller, Friedman 2009, p. 15, 20

    This is simply a frozenset. We assume that possible outcomes contained in
    this object are measurable.
    """

    def __init__(self, omega: FrozenSet[Outcome]):
        self.data = omega
