"""!
\file abstractrandvar.py Represents an abstract random variable
"""
from abc import ABC, abstractmethod
from typing import Callable, List, Optional

from pygmodels.graph.graphtype.abstractobj import (
    AbstractGraphObj,
    AbstractNode,
)
from pygmodels.value.codomain import Codomain, CodomainValue
from pygmodels.value.codomain import Range
from pygmodels.value.domain import Domain, DomainValue
from pygmodels.value.value import NumericValue

PossibleOutcomes = Codomain
PossibleOutcome = CodomainValue


class AbstractRandomVariableMember(AbstractGraphObj):
    """"""

    @abstractmethod
    def belongs_to(self) -> str:
        "Output the identifier of the random variable associated with the evidence"
        raise NotImplementedError

    @abstractmethod
    def description(self) -> Optional[str]:
        """!
        Supplementary information about member
        """
        raise NotImplementedError


class AbstractEvent(AbstractRandomVariableMember):
    """"""

    @abstractmethod
    def __call__(self, sample: DomainValue) -> PossibleOutcome:
        """An event that maps a sample to outcome"""
        raise NotImplementedError


class AbstractEvidence(AbstractRandomVariableMember):
    """!
    An evidence interface.
    """

    @abstractmethod
    def value(self) -> PossibleOutcome:
        raise NotImplementedError


class AbstractRandomVariable(AbstractNode):
    """!
    Abstract random variable
    """

    @abstractmethod
    def __call__(self, out: PossibleOutcome) -> float:
        """!
        Measure the probability of the given outcome
        """
        raise NotImplementedError
