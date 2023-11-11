"""!
\file abstractvalue.py Value of a set
"""

from abc import ABC, abstractmethod
from typing import Any, Union, Callable, NewType
from collections.abc import MutableSet, MutableSequence, Sequence
from pygmodels.utils import is_all_type, is_type
from collections.abc import Set as CSet


BinaryValue = bool
NumericValue = Union[float, int, BinaryValue]

PyValue = Union[NumericValue, str, frozenset, tuple, Callable]


class AbstractValue(ABC):
    """
    A Value
    """

    @abstractmethod
    def is_numeric(self) -> bool:
        """"""
        raise NotImplementedError

    @abstractmethod
    def is_string(self) -> bool:
        """"""
        raise NotImplementedError

    @abstractmethod
    def is_container(self) -> bool:
        """"""
        raise NotImplementedError

    @abstractmethod
    def is_callable(self) -> bool:
        """"""
        raise NotImplementedError

    @property
    @abstractmethod
    def value(self) -> PyValue:
        "Returns the value associated with the set value"
        raise NotImplementedError

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if not isinstance(other, AbstractValue):
            return False
        return self.value == other.value


class AbstractSetValue(AbstractValue):
    """"""

    @abstractmethod
    def belongs_to(self) -> str:
        "The name of the set that contains the value"
        raise NotImplementedError

    def __eq__(self, other):
        """"""
        if isinstance(other, AbstractSetValue):
            c1 = other.value == self.value
            c2 = other.belongs_to == self.belongs_to
            return c1 and c2
        return False

    def __str__(self):
        """"""
        m = "Value[ " + str(self.value)
        m += " belongs to set " + str(self.belongs_to)
        m += " ]"
        return m

    def __hash__(self):
        """"""
        return hash(str(self))


class TypedMutableSet(MutableSet):
    """"""

    def __init__(self, iterable, member_type):
        is_all_type(iterable, "iterable", member_type, True)
        lst = set()
        for value in iterable:
            lst.add(value)
        self.elements = lst
        self.member_type = member_type

    def __iter__(self):
        return iter(self.elements)

    def __contains__(self, value):
        """"""
        return value in self.elements

    def __len__(self):
        """"""
        return len(self.elements)

    def add(self, element):
        """"""
        is_type(element, "element", self.member_type, True)
        return self.elements.add(element)

    def discard(self, element):
        """"""
        return self.elements.discard(element)


class TypedOrderedSequence(MutableSequence):
    """"""

    def __init__(self, iterable, member_type):
        is_type(iterable, "iterable", list, True)
        is_all_type(iterable, "iterable", member_type, True)
        self.elements = iterable.copy()
        self.member_type = member_type

    def __iter__(self):
        return iter(self.elements)

    def __contains__(self, value):
        return value in self.elements

    def __len__(self):
        return len(self.elements)

    def __getitem__(self, i):
        return self.elements[i]

    def __delitem__(self, i):
        del self.elements[i]

    def __setitem__(self, i, other):
        is_type(other, "other", self.member_type, True)
        self.elements[i] = other
        return

    def insert(self, i, other):
        is_type(other, "other", self.member_type, True)
        return self.elements.insert(i, other)


class FiniteTypedSet(CSet):
    """"""

    def __init__(self, iterable, member_type):
        is_all_type(iterable, "iterable", member_type, True)
        lst = set()
        for value in iterable:
            lst.add(value)
        self.elements = frozenset(lst)

    def __iter__(self):
        return iter(self.elements)

    def __contains__(self, value):
        return value in self.elements

    def __len__(self):
        return len(self.elements)


class OrderedFiniteTypedSequence(Sequence):
    """"""

    def __init__(self, iterable, member_type):
        is_type(iterable, "iterable", tuple, True)
        is_all_type(iterable, "iterable", member_type, True)
        self.elements = tuple([f for f in iterable])

    def __iter__(self):
        return iter(self.elements)

    def __contains__(self, value):
        return value in self.elements

    def __len__(self):
        return len(self.elements)

    def __getitem__(self, i):
        return self.elements[i]
