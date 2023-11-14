"""!
\file codomain.py Represents a codomain of a function. Since we are dealing
with probabilities and related concepts the codomain should be a measurable
value
"""

from typing import Any, Callable, Dict, FrozenSet, List, Optional, Set, Tuple

from pygmodels.utils import is_type, is_optional_type
from pygmodels.value.valuetype.value import SetValue
from pygmodels.value.valuetype.value import Value
from pygmodels.value.valuetype.value import NumericValue
from pygmodels.value.valuetype.abstractvalue import TypedMutableSet
from pygmodels.value.valuetype.abstractvalue import TypedOrderedSequence
from pygmodels.value.valuetype.abstractvalue import FiniteTypedSet
from pygmodels.value.valuetype.abstractvalue import OrderedFiniteTypedSequence
from pygmodels.value.valuetype.abstractvalue import NamedContainer


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


class Interval(NamedContainer):
    """"""

    def __init__(self, name: str, lower: CodomainValue, upper: CodomainValue):
        """"""
        super().__init__(name=name)
        is_type(lower, "lower", CodomainValue, True)
        is_type(lower.fetch(), "lower.fetch()", NumericValue, True)
        self._lower = lower

        is_type(upper, "upper", CodomainValue, True)
        is_type(upper.fetch(), "upper.fetch()", NumericValue, True)
        self._upper = upper

    @property
    def lower(self) -> NumericValue:
        """"""
        return self._lower.fetch()

    @property
    def upper(self) -> NumericValue:
        """"""
        return self._upper.fetch()

    def __call__(
        self, sampler: Callable[[NumericValue, NumericValue], NumericValue]
    ) -> CodomainValue:
        """
        Sampler function for the interval
        """
        codom = CodomainValue(
            v=sampler(self.lower, self.upper),
            mapping_name=str(sampler),
            set_id=self._name,
        )
        return codom


class Codomain(TypedMutableSet):
    """"""

    def __init__(self, name: str, iterable):
        """"""
        super().__init__(iterable, CodomainValue, name=name)


class Range(Codomain):
    """"""

    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)


class RangeSubset(Range):
    """"""

    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)


class OrderedCodomain(TypedOrderedSequence):
    """"""

    def __init__(self, name: str, iterable):
        """"""
        super().__init__(iterable, CodomainValue, name=name)


class FiniteCodomain(FiniteTypedSet):
    """"""

    def __init__(self, name: str, iterable):
        super().__init__(iterable, CodomainValue, name=name)


class OrderedFiniteCodomain(OrderedFiniteTypedSequence):
    """"""

    def __init__(self, name: str, iterable):
        super().__init__(iterable, CodomainValue, name=name)
