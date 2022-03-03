"""!
\file domain.py Represents the domain of a function. It can be anything.
"""

from typing import Any, FrozenSet, List, Optional, Set, Tuple

from pygmodels.value.abstractvalue import AbstractSetValue


class DomainValue(AbstractSetValue):
    def __init__(self, v: Any, dom_id: Optional[str]):
        self.v = v
        self._domain = dom_id

    @property
    def belongs_to(self):
        if self._domain is None:
            raise ValueError("Value is not associated to a domain")
        return self._domain

    @property
    def value(self):
        return self.v

    def __eq__(self, other):
        """"""
        if isinstance(other, DomainValue):
            c1 = other.value == self.value
            c2 = other.belongs_to == self.belongs_to
            return c1 and c2
        return False

    def __str__(self):
        """"""
        m = "<DomainValue: " + str(self.value)
        m += " of domain " + str(self.belongs_to)
        m += ">"
        return m

    def __hash__(self):
        """"""
        return hash(str(self))


Domain = Set[DomainValue]
OrderedCodomain = List[DomainValue]

FiniteDomain = FrozenSet[DomainValue]
OrderedFiniteDomain = Tuple[DomainValue]
