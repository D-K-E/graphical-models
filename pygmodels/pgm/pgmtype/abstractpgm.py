"""!
Abstract objects, interfaces, for implementing Probabilistic graphical models
"""


from abc import abstractmethod
from typing import Callable, Dict, FrozenSet, List, Set, Tuple

from pygmodels.factor.factortype.abstractfactor import AbstractFactor
from pygmodels.graphtype.abstractobj import (
    AbstractEdge,
    AbstractGraph,
    AbstractGraphObj,
    AbstractNode,
)
from pygmodels.randvar.randvartype.abstractrandvar import (
    AbstractRandomVariable,
)
from pygmodels.value.codomain import Outcome
from pygmodels.value.value import NumericValue


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
