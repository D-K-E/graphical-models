"""!
\file abstractrandvar.py Represents an abstract random variable
"""
from abc import ABC, abstractmethod

from pygmodels.gtype.abstractobj import AbstractNode
from pygmodels.value.codomain import Outcome
from pygmodels.value.value import NumericValue


class AbstractRandomVariable(AbstractNode):
    """!
    Abstract random variable
    """

    @abstractmethod
    def p(self, out: Outcome) -> NumericValue:
        """!
        Measure the probability of the given outcome
        """
        raise NotImplementedError
