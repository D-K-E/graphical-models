"""
"""

from pygmodels.randvar.randvarmodel.event import Event
from pygmodels.randvar.randvartype.baseexpectation import BaseExpectation
from pygmodels.value.valuetype.value import NumericValue
from pygmodels.utils import is_optional_type
from typing import Union, Optional, Callable, Tuple
from types import FunctionType


class EventExpectation(BaseExpectation):
    """"""

    def __init__(
        self,
        expectation_id: str,
        randvar: Optional[Event] = None,
        data: Optional[dict] = None,
    ):
        """"""
        is_optional_type(randvar, "randvar", Event, True)
        super().__init__(expectation_id=expectation_id, randvar=randvar, data=data)

    def __call__(self, x: Optional[PossibleOutcome] = None) -> float:
        """
        from Biagini, Campanino, 2016, p. 10

        1. the probability of an event E is a number between 0 and 1, 0 ≤ P(E) ≤ 1;
        2. E ≡ 0 \f$\to\f$ P(E) = 0;
        3. E ≡ 1 \f$\to\f$ P(E) = 1.
        """
        if x is None:
            probability = 0.0
            for out in self.randvar.outcomes:
                if out.value == 0:
                    probability += 0
                elif out.value == 1:
                    probability += 1
                else:
                    raise ValueError("event outcome may either be 0 or 1")
            return probability
        elif x in self:
            if x.value == 0:
                return 0.0
            elif x.value == 1:
                return 1.0
            else:
                raise ValueError("event outcome may either be 0 or 1")
