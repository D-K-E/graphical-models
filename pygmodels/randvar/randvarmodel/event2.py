"""
\brief event as defined in Fristedt 1997, p. 3 and Venkatesh 2013, p. 14
"""

from pygmodels.randvar.randvarmodel.discrete import DiscreteRandomNumber
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcomes
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcome
from pygmodels.value.valuetype.abstractvalue import Interval
from pygmodels.value.valuetype.value import NumericValue
from pygmodels.utils import mk_id
from typing import Optional, Set


class Event(PossibleOutcomes):
    """"""

    def __init__(self, iterable: Set[PossibleOutcome]):
        """"""
