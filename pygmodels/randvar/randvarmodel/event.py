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
