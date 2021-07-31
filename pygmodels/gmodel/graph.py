"""!
\file graph.py

\defgroup graphgroup Graph and Related Objects

Contains a general graph object. Most of the functionality is based on 
Diestel 2017.

"""
from typing import Set, Optional, Callable, List, Tuple, Union, Dict, FrozenSet
from pygmodels.gtype.graphobj import GraphObject
from pygmodels.graphf.graphops import BaseGraphSetOps, BaseGraphAlgOps
from pygmodels.graphf.bgraphops import BaseGraphOps
from pygmodels.graphf.graphanalyzer import BaseGraphAnalyzer
from pygmodels.gmodel.finitegraph import FiniteGraph
from pygmodels.gtype.basegraph import BaseGraph
from pygmodels.gtype.edge import Edge, EdgeType
from pygmodels.gtype.node import Node
from pygmodels.graphf.graphtraverser import BaseGraphTraverser
from uuid import uuid4
import math


class Graph(BaseGraph):
    """!
    Simple finite graph
    \f$ G = (V, E) \f$ where \f$ V \f$ is the vertex set and \f$ E \f$ is the edge set.
    """

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
        super().__init__(gid=gid, nodes=nodes, edges=edges, data=data)
        #
        self.props = BaseGraphTraverser.visit_graph_dfs(
            self,
            edge_generator=lambda x: BaseGraphOps.edges_of(self, x),
            check_cycle=True,
        )

    @classmethod
    def from_abstract_graph(cls, g_):
        ""
        g = BaseGraph.from_abstract_graph(g_)
        return cls.from_base_graph(g)

    @classmethod
    def from_base_graph(cls, bgraph: BaseGraph):
        "Obtain finite graph from base graph"
        nodes = set(bgraph.V.values())
        edges = set(bgraph.E.values())
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

        #
        self._nodes = {n.id(): n for n in nodes}

    @classmethod
    def is_adjacent_of(cls, e1: Edge, e2: Edge) -> bool:
        """!
        \brief Check if two edges are adjacent

        \param e1 an edge
        \param e2 an edge

        \code{.py}

        >>> n1 = Node("n1", {})
        >>> n2 = Node("n2", {})
        >>> n3 = Node("n3", {})
        >>> n4 = Node("n4", {})
        >>> e1 = Edge(
        >>>     "e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED
        >>> )
        >>> e2 = Edge(
        >>>     "e2", start_node=n2, end_node=n3, edge_type=EdgeType.UNDIRECTED
        >>> )
        >>> e3 = Edge(
        >>>     "e3", start_node=n3, end_node=n4, edge_type=EdgeType.UNDIRECTED
        >>> )
        >>> graph_2 = Graph(
        >>>   "g2",
        >>>   data={"my": "graph", "data": "is", "very": "awesome"},
        >>>   nodes=set([n1, n2, n3, n4]),
        >>>   edges=set([e1, e2, e3]),
        >>> )
        >>> graph_2.is_adjacent_of(e2, e3)
        >>> True

        \endcode
        """
        n1_ids = e1.node_ids()
        n2_ids = e2.node_ids()
        return len(n1_ids.intersection(n2_ids)) > 0

    @classmethod
    def is_node_incident(cls, n: Node, e: Edge) -> bool:
        """!
        \brief Check if a node is incident of an edge

        \param n node We check if this node is an endvertex of the edge.
        \param e The queried edge.

        \code{.py}

        >>> n1 = Node("n1", {})
        >>> n2 = Node("n2", {})
        >>> e1 = Edge("e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED)
        >>> e2 = Edge("e2", start_node=n1, end_node=n1, edge_type=EdgeType.UNDIRECTED)
        >>> Graph.is_node_incident(n1, e1)
        >>> # True
        >>> Graph.is_node_incident(n2, e2)
        >>> # False

        \endcode
        """
        return e.is_endvertice(n)

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
        gdata = BaseGraphOps.to_edgelist(self)
        for v in self.V:
            for k in self.V:
                common = set(gdata[v]).intersection(set(gdata[k]))
                gmat[(v, k)] = vtype(0)
        for edge in BaseGraphOps.edges(self):
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
        if BaseGraphAnalyzer.has_self_loop(self):
            raise ValueError("Graph has a self loop")
        #
        n = len(self.gdata)
        T = self.to_adjmat(vtype=bool)
        for k in self.V.copy():
            for i in self.V.copy():
                for j in self.V.copy():
                    t_ij = T[(i, j)]
                    t_ik = T[(i, k)]
                    t_ki = T[(i, k)]
                    T[(i, j)] = t_ij or (t_ik and t_ki)
        T = {(k, i): v for (k, i), v in T.items() if k != i}
        return T

    def is_connected(self) -> bool:
        """!
        \brief Check if graph is connected
        If a graph has a single component, then we assume that it is connected
        graph

        \code{.py}

        >>> n1 = Node("n1", {})
        >>> n2 = Node("n2", {})
        >>> n3 = Node("n3", {})
        >>> n4 = Node("n4", {})
        >>> e1 = Edge(
        >>>     "e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED
        >>> )
        >>> e2 = Edge(
        >>>     "e2", start_node=n2, end_node=n3, edge_type=EdgeType.UNDIRECTED
        >>> )
        >>> e3 = Edge(
        >>>     "e3", start_node=n3, end_node=n4, edge_type=EdgeType.UNDIRECTED
        >>> )
        >>> graph_2 = Graph(
        >>>   "g2",
        >>>   data={"my": "graph", "data": "is", "very": "awesome"},
        >>>   nodes=set([n1, n2, n3, n4]),
        >>>   edges=set([e1, e2, e3]),
        >>> )
        >>> graph_2.is_connected()
        >>> True

        \endcode
        """
        return self.nb_components() == 1

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

    def nb_components(self) -> int:
        """!
        \brief the number of connected components in the given graph.

        This number makes more sense in the case of undirected graphs as our
        algorithm is adapted for that case. It is computed as we are traversing
        the graph in dfs_forest()
        """
        return self.props["nb-component"]

    def is_tree(self) -> bool:
        """!
        \brief check if graph instance is a tree.

        This interpretation comes from Diestel 2017, p. 14 - 15.
        """
        nb_c = self.nb_components()
        nb_vs = len(self.nodes())
        nb_es = len(self.edges())
        return nb_c == 1 and nb_vs - 1 == nb_es

    def get_component_nodes(self, root_node_id: str) -> Set[Node]:
        """!
        \brief Get component nodes of a graph

        Given a root node id for a component, obtain its node set.
        """
        v = self.V[root_node_id]
        Ts = self.props["components"]
        T = Ts[root_node_id]
        T.add(v.id())
        return set([self.V[v] for v in T])

    def get_component(self, root_node_id: str) -> GraphObject:
        """!
        \brief get a component graph from graph instance

        As subgraphs are also graphs, components are in the strict sense a
        graph.
        """
        vertices = self.get_component_nodes(root_node_id)
        edges = [self.gdata[v.id()] for v in vertices]
        es: Set[Edge] = set()
        for elst in edges:
            for e in elst:
                es.add(self.E[e])

        return Graph(gid=str(uuid4()), nodes=vertices, edges=es)

    def get_components(self):
        """!
        \brief Get components of graph

        Each component is provided as a graph
        """
        if self.nb_components() == 1:
            return set([self])

        # Extract component roots
        component_roots = [k for k in self.props["dfs-forest"].keys()]
        return set([self.get_component(root_node_id=root) for root in component_roots])

    def get_components_as_node_sets(self) -> Set[FrozenSet[Node]]:
        """!
        \brief obtain component as a set of node sets.

        The node set members of the returning set are of type frozenset due to
        set being an unhashable type in python.
        """
        if self.nb_components() == 1:
            return set([frozenset(self.nodes())])

        # Extract component roots
        component_roots = [k for k in self.props["dfs-forest"].keys()]
        return set([frozenset(self.get_component_nodes(k)) for k in component_roots])

    def find_articulation_points(
        self, graph_maker: Callable[[Node], GraphObject]
    ) -> Set[Node]:
        """!
        \brief find articulation points of graph.

        Find the articulation points of a graph. An articulation point, also
        called cut vertex is defined as the vertex that separates two other
        vertices of the same component.

        The algorithm we implement here is the naive version see, Erciyes 2018,
        p. 228. For the definition of the cut vertex, see Diestel 2017, p. 11
        """
        nb_component = self.nb_components()
        points: Set[Node] = set()
        for node in BaseGraphOps.nodes(self):
            graph = graph_maker(node)
            if graph.nb_components() > nb_component:
                points.add(node)
        return points

    def find_bridges(self, graph_maker: Callable[[Edge], GraphObject]) -> Set[Edge]:
        """!
        \brief find bridges of a given graph.

        A bridge is defined as the edge that separates its ends in the same
        component.
        The algorithm we implement here is the naive version provided by Erciyes 2018,
        p. 228. For the definition of the bridge, see Diestel 2017, p. 11
        """
        nb_component = self.nb_components()
        bridges: Set[Edge] = set()
        for edge in BaseGraphOps.edges(self):
            graph = self.from_base_graph(BaseGraphAlgOps.subtract(self, edge))
            if graph.nb_components() > nb_component:
                bridges.add(edge)
        return bridges

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
        for e in BaseGraphOps.edges(self):
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
