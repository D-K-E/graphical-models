"""!
\file codomain.py Represents a codomain of a function. Since we are dealing
with probabilities and related concepts the codomain should be a measurable
value
"""

from typing import Any, Callable, Dict, FrozenSet, List, Optional, Set, Tuple

from pygmodels.value.abstractvalue import AbstractSetValue


class Outcome:
    def __init__(self, v):
        self.data = v


class CodomainValue(AbstractSetValue):
    """"""

    def __init__(
        self,
        value: Any,
        set_name: str,
        mapping_name: str,
        domain_name: Optional[str] = None,
    ):
        self.v = value
        if not isinstance(set_name, str):
            raise TypeError("Set name should be a string")
        self._set = set_name

        if not isinstance(mapping_name, str):
            raise TypeError("mapping_name should be a string")
        self._fn = mapping_name
        if domain_name is not None:
            if not isinstance(domain_name, str):
                raise TypeError(
                    "domain_name must be a string if it is provided"
                )
        self._fn_domain = domain_name

    @property
    def belongs_to(self) -> str:
        if self._set is None:
            raise ValueError("Value is not associated to a domain")
        return self._set

    @property
    def value(self) -> Any:
        return self.v

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

    def __eq__(self, other):
        """"""
        if isinstance(other, CodomainValue):
            c1 = other.value == self.value
            c2 = other.belongs_to == self.belongs_to
            return c1 and c2
        return False

    def __str__(self):
        """"""
        m = "<CodomainValue: " + str(self.value)
        m += " of set " + str(self.belongs_to)
        m += " mapped by " + str(self.mapped_by)
        m += " from " + str(self.mapped_from)
        m += ">"
        return m

    def __hash__(self):
        """"""
        m = "<CodomainValue: " + str(self.value)
        m += " of set " + str(self.belongs_to)
        return hash(m)


Codomain = Set[CodomainValue]
OrderedCodomain = List[CodomainValue]

FiniteCodomain = FrozenSet[CodomainValue]
OrderedFiniteCodomain = Tuple[CodomainValue]
