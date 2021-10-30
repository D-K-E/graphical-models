"""!
\file domain.py Represents the domain of a function. It can be anything.
"""

from typing import Any, Optional, Tuple, Set, FrozenSet, List


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


Domain = Set[DomainValue]
OrderedCodomain = List[DomainValue]

FiniteDomain = FrozenSet[DomainValue]
OrderedFiniteDomain = Tuple[DomainValue]
