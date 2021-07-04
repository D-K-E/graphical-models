"""!
Abstract objects, interfaces, for implementing Probabilistic graphical models
"""


from gmodels.gtypes.abstractobj import AbstractGraph
from gmodels.gtypes.abstractobj import AbstractNode, AbstractEdge
from gmodels.gtypes.abstractobj import AbstractGraphObj

from abc import abstractmethod
from typing import Callable, Set, List, FrozenSet, Tuple, Dict

from gmodels.pgmtypes.codomaintype import NumericValue, Outcome


class AbstractRandomVariable(AbstractNode):
    """!
    Abstract random variable
    """

    @abstractmethod
    def p(self, out: Outcome) -> NumericValue:
        """!
        Measure the probability of the given outcome
        """
        raise NotImplementedError


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


class AbstractPGM(AbstractGraph):
    """!
    Abstract probabilistic graphical models
    """

    @property
    @abstractmethod
    def V(self) -> Dict[str, AbstractRandomVariable]:
        """!
        Acces to node set of PGM
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def E(self) -> Dict[str, AbstractEdge]:
        """!
        Acces to edge set set of PGM
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def F(self) -> Dict[str, AbstractFactor]:
        """!
        Acces to factor set of PGM
        """
        raise NotImplementedError
