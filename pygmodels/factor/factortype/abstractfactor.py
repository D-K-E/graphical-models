# abstract factor type
"""!
\file abstractfactor.py Contains abstract class for the factor
"""
from abc import ABC, abstractmethod
from typing import Callable, FrozenSet, List, Set, Tuple

from pygmodels.graph.graphtype.abstractobj import AbstractGraphObj
from pygmodels.randvar.randvartype.abstractrandvar import (
    AbstractRandomVariable,
)
from pygmodels.value.valuetype.value import OrderedFiniteVSet
from pygmodels.value.valuetype.abstractvalue import TypedMutableSet
from pygmodels.value.valuetype.abstractvalue import TypedOrderedSequence
from pygmodels.value.valuetype.abstractvalue import FiniteTypedSet
from pygmodels.value.valuetype.abstractvalue import OrderedFiniteTypedSequence


class FactorScope(TypedMutableSet):
    """"""

    def __init__(self, iterable):
        super().__init__(iterable, AbstractRandomVariable)


OrderedSubset = OrderedFiniteVSet
FactorDomainValue = FrozenSet[OrderedSubset]
DomainSubset = DomainSliceSet
FactorDomain = List[DomainSubset]
FactorCartesianProduct = FactorDomain


class AbstractFactor(AbstractGraphObj):
    """"""

    @abstractmethod
    def scope_vars(self, filter_fn: Callable[[FactorScope], Set[FactorScope]]):
        """"""
        raise NotImplementedError

    @abstractmethod
    def partition_value(self, vd: FactorDomain) -> float:
        """"""
        raise NotImplementedError

    def Z(self, vd: FactorDomain) -> float:
        return self.partition_value(vd=vd)

    @abstractmethod
    def __call__(self, scope_product: DomainSliceSet):
        """"""
        raise NotImplementedError
