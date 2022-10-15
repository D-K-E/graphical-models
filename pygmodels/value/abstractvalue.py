"""!
\file abstractvalue.py Value of a set
"""

from abc import ABC, abstractmethod
from typing import Any, Union, Callable

BinaryValue = bool
NumericValue = Union[float, int, BinaryValue]

Value = Union[NumericValue, str, frozenset, set, list, dict, tuple, Callable]


class AbstractValue(ABC):
    """
    A Value
    """

    @abstractmethod
    def is_numeric(self) -> bool:
        ""
        raise NotImplementedError

    @abstractmethod
    def is_string(self) -> bool:
        ""
        raise NotImplementedError

    @abstractmethod
    def is_container(self) -> bool:
        ""
        raise NotImplementedError

    @abstractmethod
    def is_callable(self) -> bool:
        ""
        raise NotImplementedError

    @property
    @abstractmethod
    def value(self) -> Value:
        "Returns the value associated with the set value"
        raise NotImplementedError


class AbstractSetValue(AbstractValue):
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
        m = "SetValue[ " + str(self.value)
        m += " belongs to set " + str(self.belongs_to)
        m += " ]"
        return m

    def __hash__(self):
        """"""
        return hash(str(self))
