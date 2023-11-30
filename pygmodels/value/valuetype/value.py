"""!
\file value.py Represents the value of functions in the case of PGMs
"""

from typing import Callable, FrozenSet, List, Optional, Set, Tuple, Union

from pygmodels.value.valuetype.abstractvalue import AbstractSetValue
from pygmodels.value.valuetype.abstractvalue import AbstractValue
from pygmodels.value.valuetype.abstractvalue import Countable
from pygmodels.value.valuetype.abstractvalue import TypedSequence
from pygmodels.value.valuetype.abstractvalue import Interval
from pygmodels.value.valuetype.abstractvalue import IntervalConf
from pygmodels.utils import is_type, is_optional_type
from pygmodels.utils import is_all_type
from types import FunctionType
from xml.etree import ElementTree as ET
import math


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

    @staticmethod
    def __cond_check__(s, o):
        """"""
        cond1 = s.value == math.inf
        cond2 = s.value == (-math.inf)
        cond3 = o.value == (math.inf)
        cond4 = o.value == (-math.inf)
        return cond1, cond2, cond3, cond4

    @staticmethod
    def __add_cond__(s, o):
        """"""
        s_inf, s_minf, o_inf, o_minf = NumericValue.__cond_check__(s=s, o=o)
        if s_inf and o_minf:
            raise ValueError(f"{s.value} + {o.value} is undefined")
        if s_minf and o_inf:
            raise ValueError(f"{s.value} + {o.value} is undefined")
        if s_inf and o_inf:
            return (NumericValue(math.inf), True)
        if s_minf and o_minf:
            return (NumericValue(-math.inf), True)
        return (None, False)

    @staticmethod
    def __sub_cond__(s, o):
        """"""
        s_inf, s_minf, o_inf, o_minf = NumericValue.__cond_check__(s=s, o=o)
        if s_inf and o_minf:
            return (NumericValue(math.inf), True)
        if s_minf and o_inf:
            return (NumericValue(-math.inf), True)
        if s_inf and o_inf:
            raise ValueError(f"{s.value} - {o.value} is undefined")
        if s_minf and o_minf:
            raise ValueError(f"{s.value} - {o.value} is undefined")
        return (None, False)

    @staticmethod
    def __mul_cond__(s, o):
        """"""
        s_inf, s_minf, o_inf, o_minf = NumericValue.__cond_check__(s=s, o=o)
        if s_inf and o_minf:
            return (NumericValue(-math.inf), True)
        if s_minf and o_inf:
            return (NumericValue(-math.inf), True)
        if s_inf and o_inf:
            return (NumericValue(math.inf), True)
        if s_minf and o_minf:
            return (NumericValue(math.inf), True)
        if s.value == 0 and (o_inf or o_minf):
            return (NumericValue(0), True)
        if o.value == 0 and (s_minf or s_inf):
            return (NumericValue(0), True)
        return (None, False)

    @staticmethod
    def __truediv_cond__(s, o):
        """"""
        s_inf, s_minf, o_inf, o_minf = NumericValue.__cond_check__(s=s, o=o)
        if s_inf and o_minf:
            raise ValueError(f"{s.value} / {o.value} is undefined")
        if s_minf and o_inf:
            raise ValueError(f"{s.value} / {o.value} is undefined")
        if s_inf and o_inf:
            raise ValueError(f"{s.value} / {o.value} is undefined")
        if s_minf and o_minf:
            raise ValueError(f"{s.value} / {o.value} is undefined")
        return (None, False)

    @staticmethod
    def __pow_cond__(s, o):
        """"""
        s_inf, s_minf, o_inf, o_minf = NumericValue.__cond_check__(s=s, o=o)
        if s_inf and o_inf:
            return (NumericValue(math.inf), True)
        if s_inf and o_minf:
            raise ValueError(f"{s.value} ** {o.value} is undefined")
        if s_minf and o_inf:
            raise ValueError(f"{s.value} ** {o.value} is undefined")
        if s_minf and o_minf:
            raise ValueError(f"{s.value} ** {o.value} is undefined")
        return (None, False)

    @staticmethod
    def __add_op__(s, o):
        """
        infinity aware summation from: Shao 2010, p. 3
        """
        val, is_cond = NumericValue.__add_cond__(s=s, o=o)
        if is_cond:
            return val
        return NumericValue(s.value + o.value)

    @staticmethod
    def __sub_op__(s, o):
        """
        infinity aware subtraction from: Shao 2010, p. 3
        """
        val, is_cond = NumericValue.__sub_cond__(s=s, o=o)
        if is_cond:
            return val
        return NumericValue(s.value - o.value)

    @staticmethod
    def __mul_op__(s, o):
        """
        infinity aware subtraction from: Shao 2010, p. 3
        """
        val, is_cond = NumericValue.__mul_cond__(s=s, o=o)
        if is_cond:
            return val
        return NumericValue(s.value * o.value)

    def __add__(self, other):
        """
        infinity aware summation from: Shao 2010, p. 3
        """
        return self.__myop__(func=NumericValue.__add_op__, other=other)

    def __radd__(self, other):
        """"""

        def radd_op(s, o):
            """"""
            val, is_cond = NumericValue.__add_op__(s=o, o=s)
            if is_cond:
                return val
            return NumericValue(o.value + s.value)

        return self.__myop__(func=radd_op, other=other)

    def __sub__(self, other):
        """
        infinity aware summation from: Shao 2010, p. 3
        """
        return self.__myop__(func=NumericValue.__sub_op__, other=other)

    def __rsub__(self, other):
        """"""

        def rsub_op(s, o):
            """"""
            val, is_cond = NumericValue.__sub_cond__(s=o, o=s)
            if is_cond:
                return val
            return NumericValue(o.value - s.value)

        return self.__myop__(func=rsub_op, other=other)

    def __mul__(self, other):
        """
        infinity aware multiplication
        """
        return self.__myop__(func=NumericValue.__mul_op__, other=other)

    def __rmul__(self, other):
        """
        infinity aware multiplication
        """

        def mul_op(s, o):
            val, is_cond = NumericValue.__mul_cond__(s=o, o=s)
            if is_cond:
                return val
            return NumericValue(o.value * s.value)

        return self.__myop__(func=mul_op, other=other)

    def __truediv__(self, other):
        """"""

        def truediv_op(s, o):
            """"""
            val, is_cond = NumericValue.__truediv_cond__(s=s, o=o)
            return NumericValue(s.value / o.value)

        return self.__myop__(func=truediv_op, other=other)

    def __floordiv__(self, other):
        """"""

        def floordiv_op(s, o):
            """"""
            val, is_cond = NumericValue.__truediv_cond__(s=s, o=o)
            return NumericValue(s.value // o.value)

        return self.__myop__(func=floordiv_op, other=other)

    def __mod__(self, other):
        """"""

        def mod_op(s, o):
            """"""
            s_inf, s_minf, o_inf, o_minf = NumericValue.__cond_check__(s=s, o=o)
            if s_inf or s_minf or o_inf or o_minf:
                raise ValueError(
                    f"% operation is not supported with infinities {s.value}"
                    + f" and {o.value}"
                )
            return NumericValue(s.value % o.value)

        return self.__myop__(func=mod_op, other=other)

    def __pow__(self, other):
        """"""

        def pow_op(s, o):
            """"""
            val, is_cond = NumericValue.__pow_cond__(s=s, o=o)
            if is_cond:
                return val
            return NumericValue(pow(s.value, o.value))

        return self.__myop__(func=pow_op, other=other)

    def __rtruediv__(self, other):
        """"""

        def rtruediv_op(s, o):
            """"""
            val, is_cond = NumericValue.__truediv_cond__(s=o, o=s)
            return NumericValue(o.value / s.value)

        return self.__myop__(func=rtruediv_op, other=other)

    def __rfloordiv__(self, other):
        """"""

        def rfloordiv_op(s, o):
            """"""
            val, is_cond = NumericValue.__truediv_cond__(s=o, o=s)
            return NumericValue(o.value // s.value)

        return self.__myop__(func=rfloordiv_op, other=other)

    def __rmod__(self, other):
        """"""

        def rmod_op(s, o):
            """"""
            s_inf, s_minf, o_inf, o_minf = NumericValue.__cond_check__(s=s, o=o)
            if s_inf or s_minf or o_inf or o_minf:
                raise ValueError(
                    f"% operation is not supported with infinities {s.value}"
                    + f" and {o.value}"
                )
            return NumericValue(o.value % s.value)

        return self.__myop__(func=rmod_op, other=other)

    def __rpow__(self, other):
        """"""

        def rpow_op(s, o):
            """"""
            val, is_cond = NumericValue.__pow_cond__(s=o, o=s)
            if is_cond:
                return val
            return NumericValue(pow(o.value, s.value))

        return self.__myop__(func=rpow_op, other=other)

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


class ContainerValue(Value, TypedSequence):
    """"""

    def __init__(self, v: Union[tuple, frozenset], name="container", member_type=Value):
        """"""
        types = (tuple, frozenset)
        is_type(v, "v", types, True)
        super().__init__(iterable=v, name=name, member_type=member_type)

    @property
    def value(self) -> Union[tuple, frozenset]:
        return self._iter

    def __str__(self) -> str:
        """"""
        m = ET.Element(self.__name__)
        m.set("name", self._name)
        for v in self.value:
            vv = ET.SubElement(m, "value")
            vv.set("type", self._member_type.__name__)
            vv.text = str(v)
        ET.indent(m)
        return ET.tostring(m, encoding="unicode")

    def count(self):
        """"""
        return len(self)

    def length(self):
        """"""
        return len(self)


class NTupleValue(ContainerValue):
    """"""

    def __init__(self, v: tuple):
        is_type(v, "v", tuple, True)
        super().__init__(v=v, name="ntuple", member_type=NumericValue)

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


class SubsetValue(ContainerValue):
    """ """

    def __init__(self, v: FrozenSet[SetValue], name: str = "subset"):
        """"""
        is_type(v, "v", frozenset, True)
        is_all_type([a.fetch() for a in v], "v member", NumericValue, True)
        super().__init__(v=v, name=name, member_type=SetValue)

    def __myop__(self, func, other, is_set=False) -> Union[bool, ContainerValue]:
        """"""
        vset = self.value
        if isinstance(other, SubsetValue):
            oset = other.value
        else:
            oset = other
        if not is_set:
            return func(vset, oset)
        else:
            return SubsetValue(func(vset, oset))

    def __le__(self, other) -> bool:
        """"""
        self.__myop__(other=other, func=lambda s, o: s <= o, is_set=False)

    def __lt__(self, other) -> bool:
        """"""
        self.__myop__(other=other, func=lambda s, o: s < o, is_set=False)

    def __gt__(self, other) -> bool:
        """"""
        self.__myop__(other=other, func=lambda s, o: s > o, is_set=False)

    def __ge__(self, other) -> bool:
        """"""
        self.__myop__(other=other, func=lambda s, o: s >= o, is_set=False)

    def __eq__(self, other) -> bool:
        return self.__myop__(func=lambda s, o: s == o, other=other, is_set=False)

    def __ne__(self, other) -> bool:
        return self.__myop__(func=lambda s, o: s != o, other=other, is_set=False)

    def __and__(self, other) -> ContainerValue:
        return self.__myop__(func=lambda s, o: s & o, other=other, is_set=True)

    def __or__(self, other) -> ContainerValue:
        return self.__myop__(func=lambda s, o: s | o, other=other, is_set=True)

    def __xor__(self, other) -> ContainerValue:
        return self.__myop__(func=lambda s, o: s ^ o, other=other, is_set=True)

    def __sub__(self, other) -> ContainerValue:
        return self.__myop__(func=lambda s, o: s - o, other=other, is_set=True)

    def __hash__(self):
        """"""
        return hash(self.value)


class IntervalR(Interval):
    """
    An interval defined on real line
    """

    def __init__(
        self,
        lower: AbstractValue,
        upper: AbstractValue,
        open_on: Optional[IntervalConf] = None,
        name: Optional[str] = None,
    ):
        up_fn = None
        low_fn = None
        s = ""
        if open_on is None:
            s += "[" + str(lower) + ", " + str(upper) + "]"
            up_fn = lambda x: x <= self.upper
            low_fn = lambda x: x >= self.lower
        elif open_on == IntervalConf.Lower:
            s += "(" + str(lower) + ", " + str(upper) + "]"
            up_fn = lambda x: x <= self.upper
            low_fn = lambda x: x > self.lower

        elif open_on == IntervalConf.Upper:
            s += "[" + str(lower) + ", " + str(upper) + ")"
            up_fn = lambda x: x < self.upper
            low_fn = lambda x: x >= self.lower
        elif open_on == IntervalConf.Both:
            s += "(" + str(lower) + ", " + str(upper) + ")"
            up_fn = lambda x: x < self.upper
            low_fn = lambda x: x > self.lower
        if name:
            s = name
        is_type(lower, "lower", NumericValue, True)
        is_type(upper, "upper", NumericValue, True)
        super().__init__(name=s, lower=lower, upper=upper, open_on=open_on)
        self._compare_lower = low_fn
        self._compare_upper = up_fn

    def __contains__(self, i: NumericValue):
        """"""
        return self._compare_lower(i) and self._compare_upper(i)

    def length(self):
        """
        Lebesque measure as per: Epps, 2014, p. 19
        Originally defined for (a, b] type intervals but the derivation in
        p. 19-20 show that results are equivalent for (a, b) as well.
        """
        return self.upper - self.lower

    def count(self):
        """"""
        return float("inf")

    def __decide_conf__(self, other, min_l, max_l):
        """"""
        if min_l == other.lower:
            lower_open = (
                True
                if (
                    (other._open_on == IntervalConf.Lower)
                    or (other.is_closed() == False)
                )
                else False
            )
        else:
            lower_open = (
                True
                if (
                    (self._open_on == IntervalConf.Lower) or (self.is_closed() == False)
                )
                else False
            )
        if max_l == other.upper:
            upper_open = (
                True
                if (
                    (other._open_on == IntervalConf.Upper)
                    or (other.is_closed() == False)
                )
                else False
            )
        else:
            upper_open = (
                True
                if (
                    (self._open_on == IntervalConf.Upper) or (self.is_closed() == False)
                )
                else False
            )
        #
        if lower_open and upper_open:
            conf = IntervalConf.Both
        elif lower_open:
            conf = IntervalConf.Lower
        elif upper_open:
            conf = IntervalConf.Upper
        else:
            conf = None
        return conf

    def __or__(self, other):
        """"""
        if isinstance(other, IntervalR):
            raise TypeError("other must have type IntervalR")
        #
        if (other.lower > self.upper) or (other.upper < self.lower):
            raise ValueError("there is no overlap between intervals can't apply union")
        min_l = min(other.lower, self.lower)
        max_l = max(other.upper, self.upper)
        conf = self.__decide_conf__(other=other, min_l=min_l, max_l=max_l)
        return IntervalR(lower=min_l, upper=max_l, name=None, open_on=conf)

    def __and__(self, other):
        """"""
        if isinstance(other, IntervalR):
            raise TypeError("other must have type IntervalR")
        #
        if (other.lower > self.upper) or (other.upper < self.lower):
            raise ValueError(
                "there is no overlap between intervals can't apply intersection"
            )
        min_l = max(other.lower, self.lower)
        max_l = min(other.upper, self.upper)
        conf = self.__decide_conf__(other=other, min_l=min_l, max_l=max_l)
        return IntervalR(lower=min_l, upper=max_l, name=None, open_on=conf)
