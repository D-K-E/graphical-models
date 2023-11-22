"""
Abstract Node of a graph
"""
from abc import ABC, abstractmethod
from collections import namedtuple
from copy import deepcopy
from enum import Enum
from typing import (
    Callable,
    Dict,
    FrozenSet,
    List,
    NewType,
    Optional,
    Set,
    Tuple,
    Union,
)

from pygmodels.utils import is_type


class AbstractInfo(ABC):
    """"""

    @property
    @abstractmethod
    def id(self) -> str:
        raise NotImplementedError


class AbstractGraphObj(AbstractInfo):
    "Abstract graph object"

    @property
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
    """"""


class AbstractEdge(AbstractGraphObj):
    "abstract edge object"

    @property
    @abstractmethod
    def type(self) -> EdgeType:
        raise NotImplementedError

    @abstractmethod
    def is_start(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_end(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_endvertice(self, n: Union[AbstractNode, str]) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_other(self, n: Union[AbstractNode, str]) -> AbstractNode:
        """!
        \todo Type checking is not done
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def node_ids(self) -> FrozenSet[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def start(self) -> AbstractNode:
        raise NotImplementedError

    @property
    @abstractmethod
    def end(self) -> AbstractNode:
        raise NotImplementedError


class AbstractSearchResult(AbstractGraphObj):
    """"""

    @property
    @abstractmethod
    def search_name(self) -> str:
        "Search method name"
        raise NotImplementedError


class AbstractGraph(AbstractGraphObj):
    """!
    \brief Abstract Graph interface
    """

    @property
    @abstractmethod
    def V(self) -> FrozenSet[AbstractNode]:
        raise NotImplementedError

    @property
    @abstractmethod
    def E(self) -> FrozenSet[AbstractEdge]:
        raise NotImplementedError


class AbstractTree(AbstractGraph):
    """"""

    @property
    @abstractmethod
    def root(self) -> AbstractNode:
        raise NotImplementedError


class AbstractPath(AbstractGraph):
    """"""

    @abstractmethod
    def length(self) -> int:
        """"""
        raise NotImplementedError

    @abstractmethod
    def endvertices(self) -> Tuple[AbstractNode, AbstractNode]:
        """"""
        raise NotImplementedError


class AbstractFixedEdgeGraph(AbstractGraph):
    """"""

    def check_edge_type(self, etype: EdgeType) -> bool:
        """"""
        return all(e.type == etype for e in self.E)


class AbstractUndiGraph(AbstractFixedEdgeGraph):
    """"""


class AbstractDiGraph(AbstractFixedEdgeGraph):
    """"""
