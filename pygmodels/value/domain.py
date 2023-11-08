"""!
\file domain.py Represents the domain of a function. It can be anything.
"""

from typing import Any, FrozenSet, List, Optional, Set, Tuple

from pygmodels.value.abstractvalue import AbstractSetValue
from pygmodels.value.value import SetValue
from pygmodels.value.value import Value


class DomainValue(SetValue):
    def __init__(self, value: Value, set_name: Optional[str]):
        super().__init__(v=value, set_id=set_name)


Domain = Set[DomainValue]
DomainSample = Set[DomainValue]
Sample = DomainSample
OrderedDomain = List[DomainValue]

FiniteDomain = FrozenSet[DomainValue]
OrderedFiniteDomain = Tuple[DomainValue]
