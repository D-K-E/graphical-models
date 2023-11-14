"""!
\file value.py Represents the value of functions in the case of PGMs
"""

from typing import Callable, FrozenSet, List, Optional, Set, Tuple, Union

from pygmodels.value.valuetype.abstractvalue import AbstractSetValue
from pygmodels.value.valuetype.abstractvalue import AbstractValue
from pygmodels.utils import is_type, is_optional_type
from pygmodels.utils import is_all_type
from types import FunctionType


class Value(AbstractValue):
    """"""

    def is_numeric(self) -> bool:
        """"""
        return isinstance(self.value, (float, int, bool))

    def is_string(self) -> bool:
        """"""
        return isinstance(self.value, str)

    def is_container(self) -> bool:
        """"""
        types = (tuple, frozenset)
        return isinstance(self.value, types)

    def is_callable(self) -> bool:
        """"""
        return callable(self.value)


class NumericValue(Value):
    """!"""

    def __init__(self, v: Union[float, int, bool]):
        is_type(v, "v", (float, int, bool), True)
        self._v = v

    @property
    def value(self) -> Union[float, int, bool]:
        return self._v

    def __add__(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(self.value + other.value)
        else:
            return NumericValue(self.value + other)

    def __sub__(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(self.value - other.value)
        else:
            return NumericValue(self.value - other)

    def __rsub__(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(other.value - self.value)
        else:
            return NumericValue(other - self.value)

    def __mul__(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(self.value * other.value)
        else:
            return NumericValue(self.value * other)

    def __truediv__(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(self.value / other.value)
        else:
            return NumericValue(self.value / other)

    def __floordiv__(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(self.value // other.value)
        else:
            return NumericValue(self.value // other)

    def __mod__(self, other):
        """"""
        if isinstance(other, NumericValue):
            return NumericValue(self.value % other.value)
        else:
            return NumericValue(self.value % other)

    def __pow__(self, other):
        """"""
        if isinstance(other, NumericValue):
            return NumericValue(pow(self.value, other.value))
        else:
            return NumericValue(pow(self.value, other))

    def __rtruediv__(self, other):
        """"""
        if isinstance(other, NumericValue):
            return NumericValue(other.value / self.value)
        else:
            return NumericValue(other / self.value)

    def __rfloordiv__(self, other):
        """"""
        if isinstance(other, NumericValue):
            return NumericValue(other.value // self.value)
        else:
            return NumericValue(other // self.value)

    def __rmod__(self, other):
        """"""
        if isinstance(other, NumericValue):
            return NumericValue(other.value % self.value)
        else:
            return NumericValue(other % self.value)

    def __rpow__(self, other):
        """"""
        if isinstance(other, NumericValue):
            return NumericValue(pow(other.value, self.value))
        else:
            return NumericValue(pow(other, self.value))

    def __lt__(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(self.value < other.value)
        else:
            return NumericValue(self.value < other)

    def __le__(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(self.value <= other.value)
        else:
            return NumericValue(self.value <= other)

    def __gt__(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(self.value > other.value)
        else:
            return NumericValue(self.value > other)

    def __ge__(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(self.value >= other.value)
        else:
            return NumericValue(self.value >= other)

    def __eq__(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(self.value == other.value)
        else:
            return NumericValue(self.value == other)

    def __ne__(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(self.value != other.value)
        else:
            return NumericValue(self.value != other)


class StringValue(Value):
    """!"""

    def __init__(self, v: str):
        is_type(v, "v", str, True)
        self._v = v

    @property
    def value(self):
        return self._v


class ContainerValue(Value):
    """"""

    def __init__(self, v: Union[tuple, frozenset]):
        types = (tuple, frozenset)
        is_type(v, "v", types, True)
        is_all_type(v, "v", Value, True)
        self._v = v

    @property
    def value(self):
        return self._v


class CallableValue(Value):
    def __init__(self, v: FunctionType):
        is_type(v, "v", FunctionType, True)
        self._v = v

    @property
    def value(self):
        return self._v


class SetValue(Value, AbstractSetValue):
    "Value contained by a set"

    def __init__(self, v: Optional[Value] = None, set_id: Optional[str] = None):
        is_optional_type(v, "v", Value, True)
        self._v = v

        is_optional_type(set_id, "set_id", str, True)
        self._set = set_id

    @property
    def belongs_to(self) -> str:
        """"""
        if self._set is None:
            raise ValueError("Value not associated to any set")
        return self._set

    @property
    def value(self) -> object:
        """inner python object attached to value"""
        return self.fetch().value

    def fetch(self) -> Value:
        """"""
        if self._v is None:
            raise ValueError("Value is not associated to any data")
        return self._v
