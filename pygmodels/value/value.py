"""!
\file value.py Represents the value of functions in the case of PGMs
"""

from typing import Callable, FrozenSet, List, Optional, Set, Tuple, Union

from pygmodels.value.abstractvalue import AbstractSetValue
from pygmodels.value.abstractvalue import AbstractValue
from pygmodels.utils import is_type


class Value(AbstractValue):
    ""

    def is_numeric(self) -> bool:
        ""
        return isinstance(self.value, (float, int, bool))

    def is_string(self) -> bool:
        ""
        return isinstance(self.value, str)

    def is_container(self) -> bool:
        ""
        return isinstance(self.value, (tuple, list, dict))

    def is_callable(self) -> bool:
        ""
        return callable(self.value)


class NumericValue(Value):
    """!
    """

    def __init__(self, v: Union[float, int, bool]):
        is_type(
            v, originType=(float, int, bool), shouldRaiseError=True, val_name="v",
        )
        self.value = v


class SetValue(Value, AbstractSetValue):
    "Value contained by a set"

    def __init__(self, v: Optional[Value] = None, set_id: Optional[str] = None):
        if v is not None:
            types = (bool, int, float, str, dict, list, tuple, Callable, frozenset, set)
            if not isinstance(v, types):
                msg = "Type of the value must be one of *{0}* but it is {1}"
                raise TypeError(msg.format(list(map(str, types)), str(type(v))))
        self.v = v
        is_type(
            set_id, originType=str, shouldRaiseError=True, val_name="set_id",
        )

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
