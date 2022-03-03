"""!
\file value.py Represents the value of functions in the case of PGMs
"""

from typing import Callable, FrozenSet, List, Optional, Set, Tuple, Union

from pygmodels.value.abstractvalue import AbstractSetValue

NumericValue = float
DiscreteValue = str
BinaryValue = bool

Value = Union[
    NumericValue, DiscreteValue, BinaryValue, set, list, dict, tuple, Callable
]


class SetValue(AbstractSetValue):
    "Value contained by a set"

    def __init__(self, v: Optional[Value], set_id: Optional[str] = None):
        if v is None:
            val = None
        elif isinstance(v, Value):
            val = v
        else:
            raise TypeError("the associated value must have type Value")
        self.v = val
        self._set = set_id

    @property
    def belongs_to(self) -> str:
        """"""
        if self._set is None:
            raise ValueError("Value not associated to any set")
        return self._set

    @property
    def value(self) -> Value:
        if self.v is None:
            raise ValueError("Value is not associated to any data")
        return self.v


VSet = Set[SetValue]
OrderedVSet = List[SetValue]

FiniteVSet = FrozenSet[SetValue]
OrderedFiniteVSet = Tuple[SetValue]
