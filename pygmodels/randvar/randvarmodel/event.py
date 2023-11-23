"""
\brief event as defined in Biagini, Campanino, 2016, p. 5
"""

from pygmodels.randvar.randvarmodel.discrete import DiscreteRandomNumber
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcomes
from pygmodels.value.valuetype.codomain import CodomainValue
from pygmodels.value.valuetype.value import NumericValue
from pygmodels.utils import mk_id
from typing import Optional


class Event(DiscreteRandomNumber):
    """"""

    def __init__(self, *args, outcomes: Optional[PossibleOutcomes] = None, **kwargs):
        """"""
        super().__init__(*args, outcomes=outcomes, **kwargs)
        if self._outcomes is not None:
            for out in self.outcomes:
                v = out.value
                v_1 = v == 0
                v_2 = v == 1
                if not (v_1 or v_2):
                    raise ValueError("an event may have 0 or 1 as possible outcome")

    @classmethod
    def from_discrete_random_number(cls, d: DiscreteRandomNumber):
        """"""
        result = Event(
            randvar_id=d._id,
            randvar_name=d._name,
            outcomes=d._outcomes,
            data=d._data,
            evidence=d._evidence,
        )
        return result

    def to_discrete_random_number(self):
        """"""
        return DiscreteRandomNumber(
            randvar_id=self._id,
            randvar_name=self._name,
            outcomes=self._outcomes,
            data=self._data,
            evidence=self._evidence,
        )

    def __add__(self, other) -> DiscreteRandomNumber:
        "Biagini, Campanino, 2016, p. 4"
        s = self.to_discrete_random_number()
        o = other.to_discrete_random_number()
        e = s + o
        return self.from_discrete_random_number(e)

    def __sub__(self, other) -> DiscreteRandomNumber:
        "Biagini, Campanino, 2016, p. 4"
        s = self.to_discrete_random_number()
        o = other.to_discrete_random_number()
        e = s - o
        return self.from_discrete_random_number(e)

    def __mul__(self, other) -> DiscreteRandomNumber:
        "Biagini, Campanino, 2016, p. 4"
        s = self.to_discrete_random_number()
        o = other.to_discrete_random_number()
        e = s * o
        return self.from_discrete_random_number(e)

    def __truediv__(self, other) -> DiscreteRandomNumber:
        "Biagini, Campanino, 2016, p. 4"
        s = self.to_discrete_random_number()
        o = other.to_discrete_random_number()
        e = s / o
        return self.from_discrete_random_number(e)
