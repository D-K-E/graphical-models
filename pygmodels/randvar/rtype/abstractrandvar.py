"""!
\file abstractrandvar.py Represents an abstract random variable
"""
from pygmodels.gtype.abstractobj import AbstractNode
from pygmodels.value.value import NumericValue
from pygmodels.value.codomain import Outcome
from abc import ABC, abstractmethod


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
