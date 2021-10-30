# abstract factor type
"""!
\file abstractfactor.py Contains abstract class for the factor
"""
from pygmodels.gtype.abstractobj import AbstractGraphObj
from pygmodels.randvar.rtype.abstractrandvar import AbstractRandomVariable
from pygmodels.value.value import NumericValue, OrderedFiniteVSet

from abc import ABC, abstractmethod
from typing import Callable, Tuple, Set, FrozenSet, List

FactorScope = Set[AbstractRandomVariable]
OrderedSubset = OrderedFiniteVSet
DomainSliceSet = FrozenSet[OrderedSubset]
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
    def partition_value(self, vd: FactorDomain):
        """"""
        raise NotImplementedError

    @abstractmethod
    def phi(self, scope_product: DomainSliceSet):
        """"""
        raise NotImplementedError
