"""
Abstract Node of a graph
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, NewType, Callable, Set
from typing import Union, FrozenSet
from enum import Enum
from collections import namedtuple
from copy import deepcopy


class AbstractInfo(ABC):
    @abstractmethod
    def id(self) -> str:
        raise NotImplementedError


class AbstractGraphObj(AbstractInfo):
    "Abstract graph object"

    @abstractmethod
    def data(self) -> Dict:
        raise NotImplementedError

    @abstractmethod
    def copy(self):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, n) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError


class EdgeType(Enum):
    DIRECTED = 1
    UNDIRECTED = 2


class AbstractNode(AbstractGraphObj):
    ""


class AbstractEdge(ABC):
    "abstract edge object"

    @abstractmethod
    def type(self) -> EdgeType:
        raise NotImplementedError

    @abstractmethod
    def is_start(self):
        raise NotImplementedError

    @abstractmethod
    def is_end(self):
        raise NotImplementedError

    @abstractmethod
    def is_endvertice(self, n: Union[AbstractNode, str]) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_other(self, n: Union[AbstractNode, str]) -> AbstractNode:
        raise NotImplementedError

    @abstractmethod
    def node_ids(self) -> FrozenSet[str]:
        raise NotImplementedError

    @abstractmethod
    def start(self) -> AbstractNode:
        raise NotImplementedError

    @abstractmethod
    def end(self) -> AbstractNode:
        raise NotImplementedError


class AbstractGraph(AbstractGraphObj):
    """!
    \brief Abstract Graph interface
    """

    @property
    @abstractmethod
    def V(self) -> Dict[str, AbstractNode]:
        raise NotImplementedError

    @property
    @abstractmethod
    def E(self) -> Dict[str, AbstractEdge]:
        raise NotImplementedError

    @abstractmethod
    def is_trivial(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def order(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def is_related_to(
        self,
        n1: AbstractNode,
        n2: AbstractNode,
        condition: Callable[[AbstractNode, AbstractNode, AbstractEdge], bool],
        es: FrozenSet[AbstractEdge] = None,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_neighbour_of(self, n1: AbstractNode, n2: AbstractNode) -> bool:
        raise NotImplementedError
