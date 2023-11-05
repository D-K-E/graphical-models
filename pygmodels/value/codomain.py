"""!
\file codomain.py Represents a codomain of a function. Since we are dealing
with probabilities and related concepts the codomain should be a measurable
value
"""

from typing import Any, Callable, Dict, FrozenSet, List, Optional, Set, Tuple

from pygmodels.utils import is_type
from pygmodels.value.value import SetValue


class Outcome:
    def __init__(self, v):
        self.data = v


class CodomainValue(SetValue):
    """"""

    def __init__(
        self,
        value: Any,
        set_name: str,
        mapping_name: str,
        domain_name: Optional[str] = None,
    ):
        super().__init__(v=value, set_id=set_name)

        is_type(
            mapping_name,
            originType=str,
            shouldRaiseError=True,
            val_name="mapping_name",
        )
        self._fn = mapping_name
        if domain_name is not None:
            is_type(
                domain_name,
                originType=str,
                shouldRaiseError=True,
                val_name="domain_name",
            )
        self._fn_domain = domain_name

    @property
    def mapped_by(self) -> str:
        "name of the function mapping to the codomain"
        if self._fn is None:
            raise ValueError("Codomain is not associated with a function")
        return self._fn

    @property
    def mapped_from(self) -> Optional[str]:
        "the domain name of the function mapping to the codomain"
        return self._fn_domain

    def __str__(self):
        """"""
        m = "<CodomainValue: " + str(self.value)
        m += " of set " + str(self.belongs_to)
        m += " mapped by " + str(self.mapped_by)
        m += " from " + str(self.mapped_from)
        m += ">"
        return m


Codomain = Set[CodomainValue]
Range = FrozenSet[CodomainValue]
RangeSubset = Range
OrderedCodomain = List[CodomainValue]

FiniteCodomain = FrozenSet[CodomainValue]
OrderedFiniteCodomain = Tuple[CodomainValue]
