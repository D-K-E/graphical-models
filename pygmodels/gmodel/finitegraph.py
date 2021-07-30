"""!
\file finitegraph.py

\defgroup graphgroup Finite Graph and Related Objects

Contains a general graph object. Most of the functionality is based on 
Diestel 2017.

"""
from typing import Set, Optional, Callable, List, Tuple, Union, Dict, FrozenSet
from pygmodels.gtype.basegraph import BaseGraph
from pygmodels.gtype.edge import Edge, EdgeType
from pygmodels.gtype.node import Node
from pygmodels.graphf.bgraphops import BaseGraphOps
from uuid import uuid4
import math


class FiniteGraph(BaseGraph):
    def __init__(
        self, gid: str, data={}, nodes: Set[Node] = None, edges: Set[Edge] = None
    ):
        """!
        \brief Graph Constructor

        \param gid unique graph id. In most cases we generate a random id with
        uuid4

        \param data is any data associated with the graph.

        \param nodes a node/vertex set.
        \param edges an edge set.

        \throws ValueError If the graph is trivial, we raise a value error, as
        most algorithms don't work with trivial graphs.

        We construct the graph from given node and edge set. For quick look up
        we store them in hash tables. The gdata member also stores an edge list
        representation, in order to facilitate some of the basic look up
        functionality concerning neighbours of vertices.

        \code{.py}

        >>> a = Node("a", {})  # b
        >>> b = Node("b", {})  # c
        >>> f = Node("f", {})  # d
        >>> e = Node("e", {})  # e
        >>> ab = Edge(
        >>>    "ab", start_node=a, end_node=b, edge_type=EdgeType.UNDIRECTED
        >>> )
        >>> be = Edge(
        >>>    "be", start_node=b, end_node=e, edge_type=EdgeType.UNDIRECTED
        >>> )
        >>> graph = Graph(
        >>>     "graph",
        >>>     data={"my": "graph", "data": "is", "very": "awesome"},
        >>>     nodes=set([a, b, e, f]),
        >>>     edges=set([ab, be]),
        >>> )

        \endcode
        """
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges)
        self._nodes = BaseGraphOps.get_nodes(
            ns=set(self.V.values()), es=set(self.E.values())
        )
        self.gdata = BaseGraphOps.to_edgelist(self)
