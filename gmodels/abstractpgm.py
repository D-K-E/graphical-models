"""!
Abstract objects, interfaces, for implementing Probabilistic graphical models
"""
from gmodels.gtypes.abstractobj import AbstractNode, AbstractEdge


class AbstractFactor(AbstractGraphObj):
    ""

    @abstractmethod
    def scope_vars(self, f: Callable[[Set[AbstractNode]], Set[AbstractNode]]):
        ""
        raise NotImplementedError

    @abstractmethod
    def factor_domain(
        self,
        rvar_filter: Callable[[AbstractNode], bool],
        value_filter: Callable[[float], bool],
        value_transform: Callable[[float], float],
    ):
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
