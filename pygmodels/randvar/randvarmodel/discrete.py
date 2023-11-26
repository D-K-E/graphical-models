"""
\brief discrete random number as defined in Biagini, Campanino, 2016, p. 27
"""

from pygmodels.randvar.randvartype.baserandvar2 import BaseRandomNumber
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcomes
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcome
from pygmodels.value.valuetype.codomain import CodomainValue
from pygmodels.value.valuetype.value import NumericValue
from pygmodels.utils import mk_id, is_type, is_optional_type
from typing import Optional, Callable, List
from types import FunctionType
from xml.etree import ElementTree as ET
from itertools import product


class DiscreteRandomNumber(BaseRandomNumber):
    """"""

    def __init__(self, *args, outcomes: Optional[PossibleOutcomes] = None, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        is_optional_type(outcomes, "outcomes", PossibleOutcomes, True)
        self._outcomes = outcomes

    @property
    def upper_bound(self) -> float:
        """"""
        if self._evidence is not None:
            return self._evidence.value().value
        f = max([out.value for out in self.outcomes])
        return f

    @property
    def lower_bound(self) -> float:
        """"""
        if self._evidence is not None:
            return self._evidence.value().value
        f = min([out.value for out in self.outcomes])
        return f

    @property
    def outcomes(self) -> PossibleOutcomes:
        """
        Biagini, Campanino, 2016, p. 5
        """
        if self._outcomes is None:
            raise ValueError("outcomes is none")
        if self._evidence is not None:
            return PossibleOutcomes(
                iterable=set([self._evidence.value]), name=f"{self.id}_outcome"
            )
        return self._outcomes

    def __and__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"

        def min_f(e, f):
            if (e < f).value:
                return e
            return f

        return self.__myop__(other=other, func=min_f, func_name="&")

    def __or__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"

        def max_f(e, f):
            if (e > f).value:
                return e
            else:
                return f

        return self.__myop__(other=other, func=max_f, func_name="|")

    def __invert__(self) -> BaseRandomNumber:
        """
        Biagini, Campanino, 2016, p. 4
        """
        domain_name = self.__mk_domain_name__()
        opname = "~"
        name = "(" + opname + " " + domain_name + ")"
        randvar_id = mk_id()

        def invert():
            """"""
            for out in self:
                comp = 1 - out.fetch()
                cval = PossibleOutcome(
                    v=comp,
                    randvar_id=randvar_id,
                    domain_name=domain_name,
                )
                yield cval

        set_name = "outcome"
        oname = "(" + set_name + " #" + name + ")"
        new_outcomes = PossibleOutcomes(iterable=invert(), name=oname)
        return DiscreteRandomNumber(
            randvar_id=mk_id(), randvar_name=name, outcomes=new_outcomes
        )

    def __mk_domain_name__(self):
        """"""
        if self._name is None:
            dom_o = "#(id " + self.id + ")"
        else:
            dom_o = "#(" + self.name + " (id " + self.id + ")" + ")"
        return dom_o

    def __myop__(
        self,
        other,
        func: Callable[[NumericValue, NumericValue], NumericValue] = lambda e, f: e + f,
        func_name: str = "+",
    ):
        "Biagini, Campanino, 2016, p. 4"
        is_type(other, "other", DiscreteRandomNumber, True)
        is_type(func, "func", FunctionType, True)
        is_type(func_name, "func_name", str, True)
        #
        opname = func_name

        domain_name = " ".join([self.__mk_domain_name__(), other.__mk_domain_name__()])
        name = "(" + opname + " " + domain_name + ")"
        set_name = "outcome"
        randvar_id = mk_id()

        def get_outcomes():
            """"""
            for (e_val, f_val) in product(self, other):
                f = f_val.fetch()
                e: NumericValue = e_val.fetch()
                ef_max = func(e, f)
                rval = PossibleOutcome(
                    v=ef_max,
                    randvar_id=randvar_id,
                    domain_name=domain_name,
                )
                yield rval

        oname = "(" + set_name + " #" + name + ")"
        op_result = DiscreteRandomNumber(
            randvar_id=randvar_id,
            randvar_name=name,
            outcomes=PossibleOutcomes(iterable=get_outcomes(), name=oname),
        )
        return op_result

    def __add__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"

        def add_f(e, f):
            """"""
            ef = e + f
            return ef

        return self.__myop__(other=other, func=add_f, func_name="+")

    def __sub__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"

        def sub_f(e, f):
            """"""
            ef = e - f
            return ef

        return self.__myop__(other=other, func=sub_f, func_name="-")

    def __mul__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"

        def mul_f(e, f):
            """"""
            ef = e * f
            return ef

        return self.__myop__(other=other, func=mul_f, func_name="*")

    def __truediv__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"

        def div_f(e, f):
            """"""
            ef = e / f
            return ef

        return self.__myop__(other=other, func=div_f, func_name="/")

    def __iter__(self):
        return iter(self.outcomes)

    def __contains__(self, other: PossibleOutcome) -> bool:
        """"""
        is_type(other, "other", PossibleOutcome, True)
        return x.mapped_by == self.id

    def __str__(self):
        """"""
        s = ET.Element("DiscreteRandomNumber")
        s.set("id", self.id)
        if self._name is not None:
            s.set("name", self._name)
        if self._data is not None:
            d = ET.SubElement(s, "Data")
            for k, v in self.data.items():
                kd = ET.SubElement(d, str(k))
                kd.text = str(v)
        for o in self.outcomes:
            s.append(ET.fromstring(str(o)))
        ET.indent(s)
        return ET.tostring(s, encoding="unicode")
