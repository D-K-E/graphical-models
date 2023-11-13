"""
\brief discreteops.py 
"""
from pygmodels.utils import is_type
from pygmodels.value.codomain import CodomainValue
from pygmodels.value.valuetype.value import NumericValue
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcomes
from pygmodels.randvar.randvarmodel.discrete import DiscreteRandomNumber
from types import FunctionType, LambdaType
from uuid import uuid4


class DiscreteRandomNumberOps:
    """"""

    @staticmethod
    def apply(
        r: DiscreteRandomNumber,
        other: DiscreteRandomNumber,
        f: Callable[[NumericValue, NumericValue], NumericValue] = lambda e, f: e + f,
    ):
        """"""
        is_type(r, "r", DiscreteRandomNumber, True)
        is_type(other, "other", DiscreteRandomNumber, True)
        name = "(" + (", ".join([other.name, r.name])) + ")"
