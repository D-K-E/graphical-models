"""!
\file value.py Represents the value of functions in the case of PGMs
"""

from typing import Callable, FrozenSet, List, Optional, Set, Tuple, Union

from pygmodels.value.valuetype.abstractvalue import AbstractSetValue
from pygmodels.value.valuetype.abstractvalue import AbstractValue
from pygmodels.utils import is_type, is_optional_type
from pygmodels.utils import is_all_type
from types import FunctionType
from xml.etree import ElementTree as ET


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

    def __myop__(self, func, other) -> Union[Value, bool]:
        """"""
        is_type(other, "other", (NumericValue, float, int, bool))
        if not isinstance(other, NumericValue):
            other = NumericValue(v=other)
        #
        return func(self, other)

    def __add__(self, other):
        return self.__myop__(
            func=lambda s, o: NumericValue(s.value + o.value), other=other
        )

    def __sub__(self, other):
        return self.__myop__(
            func=lambda s, o: NumericValue(s.value - o.value), other=other
        )

    def __rsub__(self, other):
        return self.__myop__(
            func=lambda s, o: NumericValue(o.value - s.value), other=other
        )

    def __mul__(self, other):
        return self.__myop__(
            func=lambda s, o: NumericValue(s.value * o.value), other=other
        )

    def __truediv__(self, other):
        return self.__myop__(
            func=lambda s, o: NumericValue(s.value / o.value), other=other
        )

    def __floordiv__(self, other):
        return self.__myop__(
            func=lambda s, o: NumericValue(s.value // o.value), other=other
        )

    def __mod__(self, other):
        """"""
        return self.__myop__(
            func=lambda s, o: NumericValue(s.value % o.value), other=other
        )

    def __pow__(self, other):
        """"""
        return self.__myop__(
            func=lambda s, o: NumericValue(pow(s.value, o.value)), other=other
        )

    def __rtruediv__(self, other):
        """"""
        return self.__myop__(
            func=lambda s, o: NumericValue(o.value / s.value), other=other
        )

    def __rfloordiv__(self, other):
        """"""
        return self.__myop__(
            func=lambda s, o: NumericValue(o.value // s.value), other=other
        )

    def __rmod__(self, other):
        """"""
        return self.__myop__(
            func=lambda s, o: NumericValue(o.value % s.value), other=other
        )

    def __rpow__(self, other):
        """"""
        return self.__myop__(
            func=lambda s, o: NumericValue(pow(o.value, s.value)), other=other
        )

    def __lt__(self, other):
        return self.__myop__(func=lambda s, o: s.value < o.value, other=other)

    def __le__(self, other):
        return self.__myop__(func=lambda s, o: s.value <= o.value, other=other)

    def __gt__(self, other):
        return self.__myop__(func=lambda s, o: s.value > o.value, other=other)

    def __ge__(self, other):
        return self.__myop__(func=lambda s, o: s.value >= o.value, other=other)

    def __eq__(self, other):
        return self.__myop__(func=lambda s, o: s.value == o.value, other=other)

    def __ne__(self, other):
        return self.__myop__(func=lambda s, o: s.value != o.value, other=other)


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

    def __contains__(self, c: Value):
        """"""
        return c in self.value

    def __getitem__(self, index: int):
        return self.value[index]


class NTupleValue(ContainerValue):
    """"""

    def __init__(self, v: tuple):
        is_type(v, "v", tuple, True)
        is_all_type(v, "v", NumericValue, True)
        self._v = v

    def __len__(self):
        "number of dimensions of the n-tuple"
        return len(self.value)

    def is_numeric(self) -> bool:
        return True

    def __myop__(self, func: FunctionType, other: Union[ContainerValue, int, float]):
        """"""
        is_type(other, "other", (NTupleValue, int, float), True)
        if isinstance(other, NTupleValue):
            cond1 = len(other) == len(self)
            cond2 = len(other) == 1
            cond3 = cond1 or cond2
            if not cond3:
                raise ValueError(
                    f"dimension mismatch between {len(self)}" + f" and {len(other)}"
                )
        else:
            other = NTupleValue(tuple([NumericValue(other)]))
        dims = list(range(len(self)))
        if len(other) == 1:
            # broadcast
            other = NTupleValue(tuple([other[0] for _ in dims]))
        vs = [func(self[i], other[i]) for i in dims]
        return NTupleValue(tuple(vs))

    def __add__(self, other):
        """"""
        return self.__myop__(func=lambda s, o: s + o, other=other)

    def __sub__(self, other):
        return self.__myop__(func=lambda s, o: s - o, other=other)

    def __rsub__(self, other):
        return self.__myop__(func=lambda s, o: o - s, other=other)

    def __mul__(self, other):
        return self.__myop__(func=lambda s, o: s * o, other=other)

    def __truediv__(self, other):
        return self.__myop__(func=lambda s, o: s / o, other=other)

    def __floordiv__(self, other):
        return self.__myop__(func=lambda s, o: s // o, other=other)

    def __rtruediv__(self, other):
        """"""
        return self.__myop__(func=lambda s, o: o / s, other=other)

    def __rfloordiv__(self, other):
        """"""
        return self.__myop__(func=lambda s, o: o // s, other=other)


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

    def __str__(self) -> str:
        """"""
        m = ET.Element("SetValue")
        m.set("set", self.belongs_to)
        m.text = str(self.value)
        ET.indent(m)
        return ET.tostring(m, encoding="unicode")
