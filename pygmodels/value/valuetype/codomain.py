"""!
\file codomain.py Represents a codomain of a function. Since we are dealing
with probabilities and related concepts the codomain should be a measurable
value
"""

from typing import Any, Callable, Dict, FrozenSet, List, Optional, Set, Tuple

from pygmodels.utils import is_type, is_optional_type
from pygmodels.value.valuetype.value import SetValue
from pygmodels.value.valuetype.value import Value
from pygmodels.value.valuetype.abstractvalue import TypedMutableSet
from pygmodels.value.valuetype.abstractvalue import TypedOrderedSequence
from pygmodels.value.valuetype.abstractvalue import FiniteTypedSet
from pygmodels.value.valuetype.abstractvalue import OrderedFiniteTypedSequence


class CodomainValue(SetValue):
    """"""

    def __init__(
        self,
        v: Value,
        set_id: str,
        mapping_name: str,
        domain_name: Optional[str] = None,
    ):
        super().__init__(v=v, set_id=set_id)

        is_type(mapping_name, "mapping_name", str, True)
        self._fn = mapping_name
        is_optional_type(domain_name, "domain_name", str, True)
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


class Codomain(TypedMutableSet):
    """"""

    def __init__(self, iterable):
        super().__init__(iterable, CodomainValue)


class Range(Codomain):
    """"""

    def __init__(self, *args):
        """"""
        super().__init__(*args)


class RangeSubset(Range):
    """"""

    def __init__(self, *args):
        """"""
        super().__init__(*args)


class OrderedCodomain(TypedOrderedSequence):
    """"""

    def __init__(self, iterable):
        super().__init__(iterable, CodomainValue)


class FiniteCodomain(FiniteTypedSet):
    """"""

    def __init__(self, iterable):
        super().__init__(iterable, CodomainValue)


class OrderedFiniteCodomain(OrderedFiniteTypedSequence):
    """"""

    def __init__(self, iterable):
        super().__init__(iterable, CodomainValue)
