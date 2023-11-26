"""!
\file abstractvalue.py Value of a set
"""

from abc import ABC, abstractmethod
from typing import Any, Union, Callable, NewType, Optional
from collections.abc import MutableSet, MutableSequence, Sequence
from collections.abc import Iterator
from pygmodels.utils import is_all_type, is_type
from collections.abc import Set as CSet
from types import GeneratorType
from enum import Enum, auto


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

    def __hash__(self):
        """"""
        return hash(str(self))


class NamedContainer:
    """"""

    def __init__(self, name: str):
        """"""
        is_type(name, "name", str, True)
        self._name = name


class Countable(NamedContainer, Iterator):
    """"""

    def __init__(self, iterable, member_type, name: str):
        """"""
        super().__init__(name=name)
        self.member_type = member_type
        if isinstance(iterable, GeneratorType):
            self.elements = iterable
            self.it = self.elements
        else:
            is_all_type(iterable, "iterable", self.member_type, True)
            self.elements = iterable
            self.it = iter(self.elements)
        #
        self._filter = set()

    def __fetch__(self):
        """"""
        if isinstance(self.elements, GeneratorType):
            val = next(self.it, None)
            if val is None:
                self._filter = set()
                return None, True
            else:
                if val not in self._filter:
                    self._filter.add(val)
                    return val, False
                return None, False
        else:
            val = next(self.it, None)
            if val is None:
                self.it = iter(self.elements)
                return None, True
            else:
                return val, False

    def __next__(self):
        """"""
        val, is_end = self.__fetch__()
        if is_end:
            raise StopIteration
        if val:
            return val
        # iterate until the next one
        while (val is None) or (is_end == False):
            val, is_end = self.__fetch__()
            if is_end:
                raise StopIteration
            if val:
                return val


class IntervalConf(Enum):
    Lower = auto()
    Upper = auto()
    Both = auto()


class Interval(NamedContainer):
    """"""

    def __init__(
        self,
        name: str,
        lower: AbstractValue,
        upper: AbstractValue,
        open_on: Optional[IntervalConf] = None,
    ):
        """"""
        super().__init__(name=name)
        is_type(lower, "lower", AbstractValue, True)
        if not lower.is_numeric():
            raise TypeError("lower bound of interval must be a numeric value")
        self._lower = lower

        is_type(upper, "upper", AbstractValue, True)

        if not upper.is_numeric():
            raise TypeError("upper bound of interval must be a numeric value")
        self._upper = upper

        is_optional_type(open_on, "open_on", IntervalConf, True)
        self._open_on = open_on

    @property
    def lower(self) -> AbstractValue:
        """"""
        return self._lower.fetch()

    @property
    def upper(self) -> AbstractValue:
        """"""
        return self._upper.fetch()

    def is_closed(self) -> bool:
        "check if interval is closed"
        return self._open_on is None

    def is_half_closed(self) -> bool:
        "check if interval is closed from one end"
        if self._open_on is None:
            return False
        if self._open_on == IntervalConf.Both:
            return False
        return True


class TypedMutableSet(NamedContainer, MutableSet):
    """"""

    def __init__(self, iterable, member_type, name: str):
        """"""
        super().__init__(name=name)
        is_all_type(iterable, "iterable", member_type, True)
        lst = set()
        for value in iterable:
            lst.add(value)
        self.elements = lst
        self.member_type = member_type

    @classmethod
    def from_countable(self, cs: Countable):
        """"""
        return TypedMutableSet(iterable=set(cs.elements), member_type=self.member_type)

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


class TypedOrderedSequence(NamedContainer, MutableSequence):
    """"""

    def __init__(self, iterable, member_type, name: str):
        """"""
        super().__init__(name=name)
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


class FiniteTypedSet(NamedContainer, CSet):
    """"""

    def __init__(self, iterable, member_type, name: str):
        """"""
        super().__init__(name=name)
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


class OrderedFiniteTypedSequence(NamedContainer, Sequence):
    """"""

    def __init__(self, iterable, member_type, name: str):
        """"""
        super().__init__(name=name)
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
