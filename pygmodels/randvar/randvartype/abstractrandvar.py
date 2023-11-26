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
from pygmodels.value.valuetype.value import NumericValue, Value
from pygmodels.value.valuetype.abstractvalue import Countable

from xml.etree import ElementTree as ET


class PossibleOutcome(CodomainValue):
    """"""

    def __init__(self, v: Value, randvar_id: str, domain_name: Optional[str] = None):
        super().__init__(
            v=v,
            set_id=type(v).__name__,
            mapping_name=randvar_id,
            domain_name=domain_name,
        )


class PossibleOutcomes(Countable):
    """"""

    def __init__(self, iterable, name):
        super().__init__(iterable=iterable, member_type=PossibleOutcome, name=name)

    def __str__(self):
        """"""
        m = ET.Element("PossibleOutcomes")
        m.set("name", self._name)
        for o in self:
            m.append(ET.fromstring(str(o)))
        ET.indent(m)
        return ET.tostring(m, encoding="unicode")

    def __eq__(self, other):
        """"""
        if not isinstance(other, PossibleOutcomes):
            return False

        return self._name == other._name

    def deep_eq(self, other):
        """
        compares
        """
        shallow_eq = other == self
        if not shallow_eq:
            return False
        #
        olst = [o for o in other]
        slst = [s for s in self]
        s_in_o = all(o in slst for o in olst)
        o_in_s = all(s in olst for s in slst)
        return s_in_o and o_in_s


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


class AbstractObserver(AbstractNode):
    """"""

    @abstractmethod
    def assert_observation(self, rvar: AbstractRandomNumber) -> AbstractRandomNumber:
        """"""
        raise NotImplementedError

    def __call__(self, rvar: AbstractRandomNumber) -> AbstractRandomNumber:
        """
        The assertions are the mechanism which permits us to assign evidences
        to random numbers. See the discussion in
        De Finetti, B. (2017). Theory of probability: A critical introductory
        treatment, p. 33-35
        They are necessary for introducing a lot of the relations that govern
        """
        return self.assert_observation(rvar=rvar)


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
