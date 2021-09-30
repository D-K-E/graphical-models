"""!
\file graph.py

\defgroup graphgroup Graph and Related Objects

Contains a general graph object. Most of the functionality is based on
Diestel 2017.

"""
import math
from typing import Callable, Dict, FrozenSet, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pygmodels.graphf.bgraphops import BaseGraphOps
from pygmodels.graphf.bgraphops import BaseGraphEdgeOps
from pygmodels.graphf.graphanalyzer import BaseGraphAnalyzer
from pygmodels.graphf.graphanalyzer import BaseGraphBoolAnalyzer
from pygmodels.graphf.graphanalyzer import BaseGraphNumericAnalyzer
from pygmodels.graphf.graphops import BaseGraphAlgOps, BaseGraphSetOps
from pygmodels.graphf.graphsearcher import BaseGraphSearcher
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
        self, gid: str, data={}, nodes: Set[Node] = None, edges: Set[Edge] = None,
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
                edge_generator=lambda node: BaseGraphEdgeOps.edges_of(self, node),
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

    def to_adjmat(self, vtype=int) -> Dict[Tuple[str, str], int]:
        """!
        \brief Transform adjacency list to adjacency matrix representation

        \param vtype the cast type for the entry of adjacency matrix.

        \return adjacency matrix whose keys are identifiers of nodes and values
        are flags whether there is an edge between them.

        \code{.py}

        >>> a = Node("a", {})  # b
        >>> b = Node("b", {})  # c
        >>> f = Node("f", {})  # d
        >>> e = Node("e", {})  # e
        >>> ae = Edge(
        >>>    "ae", start_node=a, end_node=e, edge_type=EdgeType.UNDIRECTED
        >>> )

        >>> af = Edge(
        >>>     "af", start_node=a, end_node=f, edge_type=EdgeType.UNDIRECTED
        >>> )

        >>> ef = Edge(
        >>>     "ef", start_node=e, end_node=f, edge_type=EdgeType.UNDIRECTED
        >>> )

        >>> ugraph1 = Graph(
        >>>     "graph",
        >>>     data={"my": "graph", "data": "is", "very": "awesome"},
        >>>   nodes=set([a, b, e, f]),
        >>>   edges=set([ae, af, ef]),
        >>> )
        >>> mat = ugraph1.to_adjmat(vtype=bool)
        >>> mat == {
        >>>     ("b", "b"): False,
        >>>     ("b", "e"): False,
        >>>     ("b", "f"): False,
        >>>     ("b", "a"): False,
        >>>     ("e", "b"): False,
        >>>     ("e", "e"): False,
        >>>     ("e", "f"): True,
        >>>     ("e", "a"): True,
        >>>     ("f", "b"): False,
        >>>     ("f", "e"): True,
        >>>     ("f", "f"): False,
        >>>     ("f", "a"): True,
        >>>     ("a", "b"): False,
        >>>     ("a", "e"): True,
        >>>     ("a", "f"): True,
        >>>     ("a", "a"): False
        >>> }
        >>> True

        \endcode
        """
        gmat = {}
        for v in self.V:
            for k in self.V:
                gmat[(v.id(), k.id())] = vtype(0)
        for edge in self.E:
            tpl1 = (edge.start().id(), edge.end().id())
            tpl2 = (edge.end().id(), edge.start().id())
            if tpl1 in gmat:
                gmat[tpl1] = vtype(1)
            if edge.type() == EdgeType.UNDIRECTED:
                if tpl2 in gmat:
                    gmat[tpl2] = vtype(1)
        return gmat

    def transitive_closure_matrix(self) -> Dict[Tuple[str, str], bool]:
        """!
        \brief Obtain transitive closure matrix of a given graph

        Transitive closure is defined by Joyner, et. al. as:

        - Consider a digraph \f$G = (V, E)\f$ of order \f$n = |V |\f$. The
          transitive closure of G is defined as the digraph \f$G^{∗} = (V,
          E^{∗}) \f$ having the same vertex set as G. However, the edge set
          \f$E^{∗}\f$ of \f$G^{∗}\f$ consists of all edges uv such that there
          is a u-v path in G and \f$uv \not \in E\f$. The transitive closure
          \f$G^{*}\f$ answers an important question about G: If u and v are two
          distinct vertices of G, are they connected by a path with length ≥ 1?

        Variant of the Floyd-Roy-Warshall algorithm taken from Joyner,
        Phillips, Nguyen, Algorithmic Graph Theory, 2013, p.134

        \throws ValueError we raise a value error if the graph has a self loop.

        \code{.py}

        >>> a = Node("a", {})  # b
        >>> b = Node("b", {})  # c
        >>> f = Node("f", {})  # d
        >>> e = Node("e", {})  # e
        >>> ae = Edge(
        >>>    "ae", start_node=a, end_node=e, edge_type=EdgeType.UNDIRECTED
        >>> )

        >>> af = Edge(
        >>>     "af", start_node=a, end_node=f, edge_type=EdgeType.UNDIRECTED
        >>> )

        >>> ef = Edge(
        >>>     "ef", start_node=e, end_node=f, edge_type=EdgeType.UNDIRECTED
        >>> )

        >>> ugraph1 = Graph(
        >>>     "graph",
        >>>     data={"my": "graph", "data": "is", "very": "awesome"},
        >>>   nodes=set([a, b, e, f]),
        >>>   edges=set([ae, af, ef]),
        >>> )
        >>> mat == {
        >>>     ("a", "b"): True,
        >>>     ("a", "e"): True,
        >>>     ("a", "f"): True,
        >>>     ("b", "a"): False,
        >>>     ("b", "e"): False,
        >>>     ("b", "f"): False,
        >>>     ("e", "a"): True,
        >>>     ("e", "b"): True,
        >>>     ("e", "f"): True,
        >>>     ("f", "a"): True,
        >>>     ("f", "b"): True,
        >>>     ("f", "e"): True
        >>>   }
        >>> True

        \endcode
        """
        if BaseGraphBoolAnalyzer.has_self_loop(self):
            raise ValueError("Graph has a self loop")
        #
        T = self.to_adjmat(vtype=bool)
        for k in self.V.copy():
            for i in self.V.copy():
                for j in self.V.copy():
                    t_ij = T[(i.id(), j.id())]
                    t_ik = T[(i.id(), k.id())]
                    t_ki = T[(i.id(), k.id())]
                    T[(i.id(), j.id())] = t_ij or (t_ik and t_ki)
        T = {(k, i): v for (k, i), v in T.items() if k != i}
        return T

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

    def get_subgraph_by_vertices(
        self,
        vs: Set[Node],
        edge_policy: Callable[[Edge, Set[Node]], bool] = lambda x, ys: set(
            [x.start(), x.end()]
        ).issubset(ys)
        is True,
    ) -> GraphObject:
        """!
        Get the subgraph using vertices.

        \param vs set of vertices for the subgraph
        \param edge_policy determines which edges should be conserved. By
        default we conserve edges whose incident nodes are a subset of vs
        """
        es: Set[Edge] = set()
        for e in self.E:
            if edge_policy(e, vs) is True:
                es.add(e)
        return Graph.from_edge_node_set(edges=es, nodes=vs)

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
