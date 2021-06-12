"""
Abstract Node of a graph
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, NewType, Callable, Set
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


class AbstractEdge(ABC):
    "abstract edge object"

    @abstractmethod
    def type(self) -> EdgeType:
        raise NotImplementedError


AbstractNode = NewType("AbstractNode", AbstractGraphObj)


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
    def is_neighbour_of(self, n1: AbstractNode, n2: AbstractNode) -> bool:
        raise NotImplementedError

    @abstractmethod
    def edges_of(self, n: AbstractNode) -> Set[AbstractEdge]:
        raise NotImplementedError
