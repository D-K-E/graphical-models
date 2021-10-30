"""!
\file graph.py

\defgroup graphgroup Graph and Related Objects

Contains a general graph object. Most of the functionality is based on
Diestel 2017.

"""
import math
from typing import Callable, Dict, FrozenSet, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pygmodels.ganalysis.graphanalyzer import (
    BaseGraphAnalyzer,
    BaseGraphBoolAnalyzer,
    BaseGraphNumericAnalyzer,
)
from pygmodels.graphops.bgraphops import BaseGraphEdgeOps, BaseGraphOps
from pygmodels.graphops.graphops import BaseGraphAlgOps, BaseGraphSetOps
from pygmodels.graphops.graphsearcher import BaseGraphSearcher
from pygmodels.gtype.basegraph import BaseGraph
from pygmodels.gtype.edge import Edge, EdgeType
from pygmodels.gtype.graphobj import GraphObject
from pygmodels.gtype.node import Node


class Graph(BaseGraph):
    """!
    Simple finite graph
    \f$ G = (V, E) \f$ where \f$ V \f$ is the vertex set and \f$ E \f$ is the edge set.
    """

    def __init__(
        self,
        gid: str,
        data={},
        nodes: Set[Node] = None,
        edges: Set[Edge] = None,
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
        super().__init__(gid=gid, nodes=nodes, edges=edges, data=data)
        #
        self._props = None
        is_trivial = BaseGraphBoolAnalyzer.is_trivial(self)
        if is_trivial:
            msg = "This library is not compatible with computations with trivial graph"
            msg += "\nNodes: "
            msg += str([n.id() for n in self.V])
            msg += "\nEdges: " + str([e.id() for e in self.E])
            raise ValueError(msg)

    @property
    def graph_props(self):
        """!
        Several graph properties computed with dfs passage
        """
        if self._props is None:
            self._props = BaseGraphSearcher.depth_first_search(
                self,
                edge_generator=lambda node: BaseGraphEdgeOps.edges_of(
                    self, node
                ),
                check_cycle=True,
            )
        return self._props

    @classmethod
    def from_abstract_graph(cls, g_):
        """"""
        g = BaseGraph.from_abstract_graph(g_)
        return cls.from_base_graph(g)

    @classmethod
    def from_base_graph(cls, bgraph: BaseGraph):
        "Obtain finite graph from base graph"
        nodes = set(bgraph.V)
        edges = set(bgraph.E)
        data = bgraph.data()
        gid = bgraph.id()
        return Graph(gid=gid, nodes=nodes, edges=edges, data=data)

    @classmethod
    def from_edgeset(cls, edges: Set[Edge]):
        g = BaseGraph.from_edgeset(edges)
        return cls.from_base_graph(g)

    @classmethod
    def from_edge_node_set(cls, edges: Set[Edge], nodes: Set[Node]):
        g = BaseGraph.from_edge_node_set(edges=edges, nodes=nodes)
        return cls.from_base_graph(g)

    def to_base_graph(self):
        """!
        Transform Graph object to BaseGraph object
        """
        return BaseGraph(
            gid=self.id(),
            nodes=set(self.V.values()),
            edges=set(self.E.values()),
            data=self.data(),
        )

    def is_homomorphism(
        self,
        phi_map: Callable[[Node], Node] = lambda x: x,
        psi_map: Callable[[Edge], Edge] = lambda x: x,
    ) -> bool:
        """!
        \brief Check if a function is a homomorphism on the given graph.

        \warning Absolutely untested function that tries to follow the definition
        given in Diestel 2017, p. 3. Basically if a function transforms
        vertex set of graph but conserve adjacency properties of the graph,
        it is a homomorphism.

        """
        edges = self.edges()
        adjacency_of_vertices = set()
        nedges = set()
        nnodes = set()
        for e in edges:
            estart = e.start()
            eend = e.end()
            adjacency_of_vertices.add((estart, eend))
            nnodes.add(phi_map(estart))
            nnodes.add(phi_map(eend))
            nedges.add(psi_map(e))

        g = Graph.from_edge_node_set(edges=nedges, nodes=nnodes)
        for e in g.edges():
            estart = e.start()
            eend = e.end()
            if (estart, eend) not in adjacency_of_vertices:
                return False
        return True

    def __add__(
        self, a: Union[Set[Edge], Set[Node], Node, Edge, GraphObject]
    ) -> GraphObject:
        """!
        \brief overloads + sign for doing algebraic operations with graph
        objects.
        """
        return self.from_base_graph(BaseGraphAlgOps.add(self, a))

    def __sub__(
        self, a: Union[Set[Edge], Set[Node], Node, Edge, BaseGraph]
    ) -> BaseGraph:
        """!
        \brief overloads - sign for doing algebraic operations with graph
        objects.
        """
        bgraph = BaseGraphAlgOps.subtract(self, a)

        return self.from_base_graph(bgraph)
