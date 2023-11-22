"""
\brief event as defined in Biagini, Campanino, 2016, p. 5
"""

from pygmodels.randvar.randvarmodel.discrete import DiscreteRandomNumber
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcomes
from pygmodels.value.valuetype.codomain import CodomainValue
from pygmodels.value.valuetype.value import NumericValue
from pygmodels.utils import mk_id


class Event(DiscreteRandomNumber):
    """"""

    def __init__(self, *args, outcomes: Optional[PossibleOutcomes] = None, **kwargs):
        """"""
        super().__init__(*args, outcomes, **kwargs)
        if self._outcomes is not None:
            for out in self.outcomes:
                v = out.value
                if (v != 0) or (v != 1):
                    raise ValueError("an event may have 0 or 1 as possible outcome")

    def __or__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 5"

        def or_f(e, f):
            e_prod_f = e * f
            e_plus_f = e + f
            return e_plus_f - e_prod_f

        return self.__myop__(other=other, func=or_f, func_name="or")

    def __sub__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 5"

        def diff_f(e, f):
            e_prod_f = e * f
            return e - e_prod_f

        return self.__myop__(other=other, func=diff_f, func_name="difference")

    def __xor__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 5"
        e_f = self - other
        f_e = other - self
        return e_f or f_e
