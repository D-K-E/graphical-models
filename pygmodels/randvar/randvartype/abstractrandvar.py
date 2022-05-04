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
from pygmodels.value.domain import Domain, DomainValue
from pygmodels.value.value import NumericValue

PossibleOutcomes = Domain
PossibleOutcome = DomainValue
AssociatedValueSet = Codomain


class AbstractEvidence(AbstractGraphObj):
    """!
    An evidence interface.
    """

    @abstractmethod
    def belongs_to(self) -> str:
        "Output the identifier of the random variable associated with the evidence"
        raise NotImplementedError

    @abstractmethod
    def value(self) -> CodomainValue:
        raise NotImplementedError

    @abstractmethod
    def description(self) -> Optional[str]:
        """!
        Observation conditions and the nature of evidence
        """
        raise NotImplementedError


class AbstractRandomVariable(AbstractNode):
    """!
    Abstract random variable
    """

    @property
    @abstractmethod
    def inputs(self) -> PossibleOutcomes:
        """!
        Inputs, that is outcomes of the random variable.
        """
        raise NotImplementedError

    @abstractmethod
    def image(
        self,
        sampler: Optional[Callable[[PossibleOutcomes], List[PossibleOutcome]]],
    ) -> AssociatedValueSet:
        """!
        Image/Range of the random variable. It can be either a representation
        or the full range.
        """
        raise NotImplementedError

    @abstractmethod
    def p(self, out: CodomainValue) -> NumericValue:
        """!
        Measure the probability of the given outcome
        """
        raise NotImplementedError
