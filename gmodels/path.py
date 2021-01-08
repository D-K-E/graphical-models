"""!
Path in a given graph
"""
from typing import Set, Optional, Callable, List, Tuple, Dict, Union
from gmodels.edge import Edge, EdgeType
from gmodels.node import Node
from gmodels.graph import Graph
from uuid import uuid4
import math


class Path(Graph):
    """!
    path object as defined in Diestel 2017, p. 6
    """

    def __init__(
        self, gid: str, data={}, nodes: List[Node] = None, edges: List[Edge] = None
    ):
        ""
        super().__init__(gid=gid, data=data, nodes=set(nodes), edges=set(edges))
        self._node_list = nodes
        self._edge_list = edges

    def length(self) -> int:
        if self._edge_list is None:
            return 0
        return len(self._edge_list)

    def node_list(self) -> List[Node]:
        "get vertice list"
        if self._node_list is None or len(self._node_list) == 0:
            raise ValueError("there are no vertices in the path")
        return self._node_list

    def endvertices(self) -> Tuple[Node, Node]:
        ""
        vs = self.node_list()
        if len(vs) == 1:
            return (vs[0], vs[0])
        return (vs[0], vs[-1])


class Cycle(Path):
    """!
    Cycle as defined in Diestel p. 8
    """

    def __init__(
        self, gid: str, data={}, nodes: List[Node] = None, edges: List[Edge] = None
    ):
        ""
        super().__init__(gid, data, nodes, edges)
        vs = self.vertices()
        if vs[0] != vs[-1]:
            raise ValueError("The first and last vertice of a cycle must be same")
