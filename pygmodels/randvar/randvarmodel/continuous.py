"""
\brief event as defined in Biagini, Campanino, 2016, p. 5
"""

from pygmodels.randvar.randvartype.baserandvar2 import BaseRandomNumber
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcomes
from pygmodels.value.valuetype.codomain import CodomainValue
from pygmodels.value.valuetype.codomain import Interval
from pygmodels.value.valuetype.value import NumericValue
from pygmodels.utils import mk_id
from typing import Optional, Callable, List


class ContinuousRandomNumber(BaseRandomNumber):
    """"""

    def __init__(self, *args, outcomes: Optional[Interval] = None, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        is_optional_type(outcomes, "outcomes", Interval, True)
        self._outcomes = outcomes

    @property
    def upper_bound(self) -> float:
        """"""
        f = self.outcomes.upper.value
        return f

    @property
    def lower_bound(self) -> float:
        """"""
        f = self.outcomes.lower.value
        return f

    @property
    def outcomes(self) -> Interval:
        """ """
        if self._outcomes is None:
            raise ValueError("outcomes is none")
        if self._evidence is not None:
            possible_out: PossibleOutcome = self._evidence.value
            numeric_value: NumericValue = possible_out.fetch()
            return Interval(lower=numeric_value, upper=numeric_value)
        return self._outcomes

    def __and__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"

        def min_f(e: Interval, f: Interval):
            """"""
            ef_lower = min(e.lower, f.lower)
            ef_upper = min(e.upper, f.upper)

        return self.__myop__(other=other, func=min_f, func_name="and")

    def __or__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"

        def max_f(e: Interval, f: Interval):
            """"""
            ef_lower = max(e.lower, f.lower)
            ef_upper = max(e.upper, f.upper)

        return self.__myop__(other=other, func=max_f, func_name="or")

    def __invert__(self) -> BaseRandomNumber:
        """
        Biagini, Campanino, 2016, p. 4
        """
        name = "~" + self.name

        def invert():
            for out in [self.outcomes.lower, self.outcomes.upper]:
                comp = 1 - out
                cval = CodomainValue(
                    v=comp,
                    set_id=self.id(),
                    mapping_name="~",
                    domain_name=self.name,
                )
                yield cval

        inverted = list(invert())
        new_interval = Interval(name=name, lower=inverted[0], upper=inverted[1])
        return ContinuousRandomNumber(
            randvar_id=mk_id(), randvar_name=name, outcomes=new_interval
        )

    def __myop__(
        self,
        other,
        func: Callable[[Interval, Interval], Interval] = lambda e, f: e + f,
        func_name: str = "+",
    ):
        "Biagini, Campanino, 2016, p. 4"
        is_type(other, "other", ContinuousRandomNumber, True)
        is_type(func, "func", FunctionType, True)
        is_type(func_name, "func_name", str, True)
        #
        name = "(" + (", ".join([other.name, self.name])) + ")"
        raise NotImplementedError
