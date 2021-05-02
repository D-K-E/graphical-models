"""
Abstract Node of a graph
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
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

    @classmethod
    def _copy(cls, f):
        return deepcopy(f)

    def copy(self):
        return AbstractGraphObj._copy(self)


class EdgeType(Enum):
    DIRECTED = 1
    UNDIRECTED = 2


class NodePosition(Enum):
    START = 1
    END = 2


class AbstractEdge(ABC):
    "abstract edge object"

    @abstractmethod
    def type(self) -> EdgeType:
        raise NotImplementedError
