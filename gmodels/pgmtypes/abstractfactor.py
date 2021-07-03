"""!
Abstract Factor object that should serve as an interface to third parties
"""
from gmodels.gtypes.abstractobj import AbstractNode, AbstractEdge
from gmodels.gtypes.abstractobj import AbstractGraphObj

from gmodels.pgmtypes.codomaintype import NumericValue

from abc import abstractmethod
from typing import Callable, Set, List, FrozenSet, Tuple


class AbstractFactor(AbstractGraphObj):
    ""

    @abstractmethod
    def scope_vars(self, f: Callable[[Set[AbstractNode]], Set[AbstractNode]]):
        ""
        raise NotImplementedError

    @abstractmethod
    def vars_domain(
        self,
        rvar_filter: Callable[[AbstractNode], bool] = lambda x: True,
        value_filter: Callable[[NumericValue], bool] = lambda x: True,
        value_transform: Callable[[NumericValue], NumericValue] = lambda x: x,
    ) -> List[FrozenSet[Tuple[str, NumericValue]]]:
        ""
        raise NotImplementedError

    @abstractmethod
    def partition_value(self, vd: List[FrozenSet[Tuple[str, NumericValue]]]):
        ""
        raise NotImplementedError

    @abstractmethod
    def phi(self, scope_product: Set[Tuple[str, float]]):
        ""
        raise NotImplementedError

    @abstractmethod
    def phi_normal(self, scope_product: Set[Tuple[str, float]]):
        ""
        raise NotImplementedError
