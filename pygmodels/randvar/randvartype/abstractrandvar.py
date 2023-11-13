"""!
\file abstractrandvar.py Represents an abstract random variable
"""
from abc import ABC, abstractmethod
from typing import Callable, List, Optional

from pygmodels.graph.graphtype.abstractobj import (
    AbstractGraphObj,
    AbstractNode,
)
from pygmodels.value.valuetype.codomain import Codomain, CodomainValue
from pygmodels.value.valuetype.codomain import Range
from pygmodels.value.valuetype.domain import Domain, DomainValue
from pygmodels.value.valuetype.value import NumericValue


class PossibleOutcome(CodomainValue):
    """"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PossibleOutcomes(Codomain):
    """"""

    def __init__(self, iterable):
        super().__init__(iterable)


class AbstractRandomNumber(AbstractNode):
    """"""

    @property
    @abstractmethod
    def upper_bound(self) -> float:
        "Biagini, Campanino, 2016, p. 3"
        raise NotImplementedError

    @property
    @abstractmethod
    def lower_bound(self) -> float:
        "Biagini, Campanino, 2016, p. 3"
        raise NotImplementedError

    def is_upper_bounded(self) -> bool:
        "Biagini, Campanino, 2016, p. 3"
        return self.upper_bound != float("inf")

    def is_lower_bounded(self) -> bool:
        "Biagini, Campanino, 2016, p. 3"
        return self.lower_bound != float("-inf")

    def is_bounded(self) -> bool:
        "Biagini, Campanino, 2016, p. 3"
        return self.is_upper_bounded() and self.is_lower_bounded()

    def is_independent(self, other) -> bool:
        "Biagini, Campanino, 2016, p. 4"
        raise NotImplementedError

    @abstractmethod
    def __and__(self, other):
        "Biagini, Campanino, 2016, p. 4"
        raise NotImplementedError

    @abstractmethod
    def __or__(self, other) -> float:
        "Biagini, Campanino, 2016, p. 4"
        raise NotImplementedError

    @abstractmethod
    def __invert__(self):
        "Biagini, Campanino, 2016, p. 4"
        raise NotImplementedError


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
