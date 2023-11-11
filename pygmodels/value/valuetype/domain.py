"""!
\file domain.py Represents the domain of a function. It can be anything.
"""

from typing import Any, FrozenSet, List, Optional, Set, Tuple
from typing import NewType

from pygmodels.value.valuetype.abstractvalue import AbstractSetValue
from pygmodels.value.valuetype.abstractvalue import TypedMutableSet
from pygmodels.value.valuetype.abstractvalue import TypedOrderedSequence
from pygmodels.value.valuetype.abstractvalue import FiniteTypedSet
from pygmodels.value.valuetype.abstractvalue import OrderedFiniteTypedSequence
from pygmodels.value.valuetype.value import SetValue
from pygmodels.value.valuetype.value import Value
from pygmodels.utils import is_all_type, is_type


class DomainValue(SetValue):
    """"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Domain(TypedMutableSet):
    """"""

    def __init__(self, iterable):
        super().__init__(iterable, DomainValue)


class DomainSample(Domain):
    """"""

    def __init__(self, *args):
        """"""
        super().__init__(*args)


class Sample(DomainSample):
    """"""

    def __init__(self, *args):
        """"""
        super().__init__(*args)


class OrderedDomain(TypedOrderedSequence):
    """"""

    def __init__(self, iterable):
        super().__init__(iterable, DomainValue)


class FiniteDomain(FiniteTypedSet):
    """"""

    def __init__(self, iterable):
        super().__init__(iterable, DomainValue)


class OrderedFiniteDomain(OrderedFiniteTypedSequence):
    """"""

    def __init__(self, iterable):
        super().__init__(iterable, DomainValue)
