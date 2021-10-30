"""!
\file graphanalyzer.py Graph Analyzer for BaseGraph subclasses
"""

import math
from typing import Callable, Dict, FrozenSet, List, Optional, Set, Tuple, Union

from pygmodels.graphops.bgraphops import (
    BaseGraphBoolOps,
    BaseGraphEdgeOps,
    BaseGraphNodeOps,
    BaseGraphOps,
)
from pygmodels.graphops.graphsearcher import BaseGraphSearcher
from pygmodels.gtype.abstractobj import (
    AbstractEdge,
    AbstractGraph,
    AbstractNode,
    EdgeType,
)
from pygmodels.gtype.basegraph import BaseGraph
from pygmodels.gtype.gsearchresult import (
    BaseGraphBFSResult,
    BaseGraphDFSResult,
)


class BaseGraphBoolAnalyzer:
    """!
    Answers boolean questions about base graph objects
    """

    @staticmethod
    def has_self_loop(g: AbstractGraph) -> bool:
        """!
        \brief Check if graph has a self loop.
        We check whether the incident vertices of an edge is same.

        \code{.py}
        n1 = Node("n1", {})
        n2 = Node("n2", {})
        e1 = Edge(
            "e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED
        )
        e2 = Edge(
            "e1", start_node=n1, end_node=n1, edge_type=EdgeType.UNDIRECTED
        )
        g = Graph("graph", nodes=set([n1, n2]), edges=set([e1, e2]))
        g.has_self_loop()
        # True
        \endcode
        """
        for edge in g.E:
            if edge.start() == edge.end():
                return True
        return False

    @staticmethod
    def is_node_independent_of(
        g: AbstractGraph, n1: AbstractNode, n2: AbstractNode
    ) -> bool:
        """!
        \brief check if two nodes are independent
        We consider two nodes independent if they are not the same, and they
        are not neighbours.

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
        >>> graph_2.is_node_independent_of(n1, n3)
        >>> True

        \endcode
        """
        if n1 == n2:
            return False
        return (
            True
            if BaseGraphBoolOps.is_neighbour_of(g, n1, n2) is False
            else False
        )

    @staticmethod
    def is_stable(g: AbstractGraph, ns: FrozenSet[AbstractNode]) -> bool:
        """!
        \brief check if given node set is stable

        We ensure that no nodes in the given node set is a neighbour of one
        another as per the definition of Diestel 2017, p. 3.

        \throws ValueError if argument node set is not a subset of vertices of
        the graph
        \code{.py}

        >>> n1 = Node("n1", {})
        >>> n2 = Node("n2", {})
        >>> n3 = Node("n3", {})
        >>> n4 = Node("n4", {})
        >>> n5 = Node("n5", {})
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
        >>>   nodes=set([n1, n2, n3, n4, n5]),
        >>>   edges=set([e1, e2, e3]),
        >>> )
        >>> graph_2.is_stable(set([n1, n3, n5]))
        >>> True

        \endcode
        """
        if ns.issubset(g.V) is False:
            raise ValueError("node set is not contained in graph")
        node_list = list(ns)
        while node_list:
            n1 = node_list.pop()
            for n2 in node_list:
                if BaseGraphBoolOps.is_neighbour_of(g, n1=n1, n2=n2):
                    return False
        return True

    @staticmethod
    def is_trivial(g: AbstractGraph) -> bool:
        """!
        \brief check if graph is trivial.
        This triviality condition is taken from
        Diestel 2017, p. 2
        """
        return BaseGraphNumericAnalyzer.order(g) < 2

    @staticmethod
    def has_cycles(g: AbstractGraph) -> bool:
        """!
        \brief Check if graph instance contains cycles.
        This interpretation is from Diestel 2017, p. 8. The
        proof is provided in the given page.
        """
        md = BaseGraphNumericAnalyzer.min_degree(g)
        if md >= 2:
            return True
        return False

    @staticmethod
    def is_disjoint(g1: AbstractGraph, g2: AbstractGraph) -> bool:
        "check if g2 is disjoint to g1"
        ns = BaseGraphOps.nodes(g1)
        ns_ = g2.vertex_intersection(ns)
        return len(ns_) == 0

    @staticmethod
    def is_proper_subgraph(g1: AbstractGraph, g2: AbstractGraph) -> bool:
        "check if g2 is subgraph of g1"
        ns = BaseGraphOps.nodes(g2)
        es = BaseGraphOps.edges(g2)
        contains_nodes = BaseGraphOps.contains(g1, ns)
        contains_edges = BaseGraphOps.contains(g1, es)
        return contains_edges and contains_nodes

    @staticmethod
    def is_subgraph(g1: AbstractGraph, g2: AbstractGraph) -> bool:
        "check if g2 is subgraph of g1"
        # check vertex set includes
        # check edge set includes
        if g1 == g2:
            return True
        return BaseGraphAnalyzer.is_proper_subgraph(g1, g2)

    @staticmethod
    def is_induced_subgraph(g1: AbstractGraph, g2: AbstractGraph) -> bool:
        """
        check if g2 is induced subgraph of g1
        induced subgraph:
        g2 \sub g1 ^ xy \in Edge[g1] with x,y Vertex[g2]
        """
        is_subgraph = BaseGraphAnalyzer.is_subgraph(g1, g2)
        if not is_subgraph:
            return False
        g2_vertices = BaseGraphOps.nodes(g2)
        g1_edges = BaseGraphOps.edges(g1)
        for g1_edge in g1_edges:
            has_node_id1 = False
            has_node_id2 = False
            edge_node_ids = g1_edge.node_ids()
            edge_node_id1 = edge_node_ids[0]
            edge_node_id2 = edge_node_ids[1]
            for g2_vertex in g2_vertices:
                vertex_id = g2_vertex.id()
                if vertex_id == edge_node_id1:
                    has_node_id1 = True
                if vertex_id == edge_node_id2:
                    has_node_id2 = True
            #
            if not has_node_id1 and not has_node_id2:
                return False
        return True

    @staticmethod
    def is_spanning_subgraph(g1: AbstractGraph, g2: AbstractGraph) -> bool:
        "check if g2 is spanning subgraph of g1"
        if not BaseGraphAnalyzer.is_subgraph(g1, g2):
            return False
        return BaseGraphOps.nodes(g1) == BaseGraphOps.nodes(g2)

    @staticmethod
    def is_connected(
        g: AbstractGraph,
        result: Optional[BaseGraphDFSResult] = None,
        edge_generator: Optional[Callable] = None,
        check_cycle: Optional[bool] = None,
    ) -> bool:
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
        if not isinstance(result, BaseGraphDFSResult):
            result = BaseGraphAnalyzer.dfs_props(
                g, edge_generator=edge_generator, check_cycle=check_cycle
            )

        return BaseGraphNumericAnalyzer.nb_components(g, result=result) == 1


class BaseGraphNumericAnalyzer:
    """!
    Analyze base graph for numeric properties
    """

    @staticmethod
    def order(g: AbstractGraph) -> int:
        """!
        \brief obtain the number of vertices in the graph.

        It corresponds to \f$ |G| \f$.
        This interpretation of order is taken from Diestel 2017, p. 2.
        """
        return len(g.V)

    @staticmethod
    def comp_degree(
        g: AbstractGraph, fn: Callable[[int, int], bool], comp_val: int
    ) -> int:
        """!
        \brief generic comparison function for degree related operations

        It is used in the context of finding maximum or minimum degree of the
        graph instance.
        """
        compare_v = comp_val
        gdata = BaseGraphOps.to_edgelist(g)
        for nid in g.V:
            nb_edges = len(gdata[nid.id()])
            if fn(nb_edges, compare_v):
                compare_v = nb_edges
        return compare_v

    @staticmethod
    def max_degree(g: AbstractGraph) -> int:
        """!
        \brief obtain maximum degree of the graph instance
        """
        v = BaseGraphNumericAnalyzer.comp_degree(
            g, fn=lambda nb_edges, compare: nb_edges > compare, comp_val=0
        )
        return v

    @staticmethod
    def min_degree(g: AbstractGraph) -> int:
        """!
        \brief obtain minimum degree of graph instance
        """
        return int(
            BaseGraphNumericAnalyzer.comp_degree(
                g,
                fn=lambda nb_edges, compare: nb_edges < compare,
                comp_val=math.inf,
            )
        )

    @staticmethod
    def average_degree(g: AbstractGraph) -> float:
        """!
        \brief obtain the average degree of graph instance

        The average degree is calculated using the formula:
        \f[ d(G) = \frac{1}{V[G]} \sum_{v \in V[G]} d(v) \f]

        It can be found in Diestel 2017, p. 5
        """
        gdata = BaseGraphOps.to_edgelist(g)
        return sum([len(gdata[v.id()]) for v in g.V]) / len(g.V)

    @staticmethod
    def edge_vertex_ratio(g: AbstractGraph) -> float:
        """!
        \brief obtain edge vertex ratio of graph instance
        Corresponds to \f[\epsilon(G)\f].
        The formula comes from Diestel 2017, p. 5.
        """
        return len(g.E) / len(g.V)

    @staticmethod
    def ev_ratio_from_average_degree(
        g: AbstractGraph, average_degree: float
    ) -> float:
        """!
        \brief obtain edge vertex ratio from average degree

        Applies the following formula:
        \f[ |E[G]| = \frac{1}{2} \sum_{v \in V[G]} d(v) = 1/2 * d(G) * |V[G]|
        \f]
        It comes from Diestel 2017, p. 5
        """
        return average_degree / 2

    @staticmethod
    def ev_ratio(g: AbstractGraph) -> float:
        """!
        \brief shorthand for ev_ratio_from_average_degree()
        """
        adegree = BaseGraphNumericAnalyzer.average_degree(g)
        return BaseGraphNumericAnalyzer.ev_ratio_from_average_degree(
            g, adegree
        )

    @staticmethod
    def shortest_path_length(g: AbstractGraph) -> int:
        """!
        \brief Give the shortest possible path length for graph instance

        This interpretation is taken from Diestel 2017, p. 8. The proof
        is also given in the corresponding page.
        """
        return BaseGraphAnalyzer.min_degree(g)

    @staticmethod
    def shortest_cycle_length(g: AbstractGraph) -> int:
        """!
        \brief Give the shortest possible cycle length for graph instance
        The interpretation comes from Diestel 2017, p. 8.
        """
        if BaseGraphAnalyzer.has_cycles(g):
            return BaseGraphAnalyzer.min_degree(g) + 1
        else:
            return 0

    @staticmethod
    def nb_neighbours_of(g: AbstractGraph, n: AbstractNode) -> int:
        """!
        \brief obtain number of neighbours of a given node.

        \param n node whose neighbour set we are interested in.

        \see Graph.neighbours_of

        Number of nodes in the neighbour set of n.

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
        >>> graph_2.nb_neighbours_of(n2)
        >>> 2

        \endcode
        """
        return len(BaseGraphNodeOps.neighbours_of(g, n))

    @staticmethod
    def nb_edges(g: AbstractGraph) -> int:
        """!
        \brief obtain number of edges in the graph
        It corresponds to \f$ ||G|| \f$.
        This interpretation is taken from Diestel 2017, p. 2.
        """
        return len(g.E)

    @staticmethod
    def nb_components(
        g: AbstractGraph,
        result: Optional[BaseGraphDFSResult] = None,
        edge_generator: Optional[Callable] = None,
        check_cycle: Optional[bool] = None,
    ) -> int:
        """!
        \brief the number of connected components in the given graph.

        This number makes more sense in the case of undirected graphs as our
        algorithm is adapted for that case. It is computed as we are traversing
        the graph in dfs_forest()

        """
        if not isinstance(result, BaseGraphDFSResult):
            result = BaseGraphAnalyzer.dfs_props(
                g, edge_generator=edge_generator, check_cycle=check_cycle
            )
        return result.nb_component

    @staticmethod
    def is_tree(
        g: AbstractGraph,
        result: Optional[BaseGraphDFSResult] = None,
        edge_generator: Optional[Callable] = None,
        check_cycle: Optional[bool] = None,
    ) -> bool:
        """!
        \brief check if graph instance is a tree.

        This interpretation comes from Diestel 2017, p. 14 - 15.
        """
        if not isinstance(result, BaseGraphDFSResult):
            result = BaseGraphAnalyzer.dfs_props(
                g, edge_generator=edge_generator, check_cycle=check_cycle
            )
        nb_c = BaseGraphNumericAnalyzer.nb_components(g, result=result)
        nb_vs = len(g.V)
        nb_es = len(g.E)
        return nb_c == 1 and nb_vs - 1 == nb_es


class BaseGraphNodeAnalyzer:
    """!
    Analyze graphs for properties that are measured with nodes
    """

    @staticmethod
    def max_degree_vs(g: AbstractGraph) -> Set[AbstractNode]:
        """!
        \brief obtain vertex set of whose degrees are equal to maximum degree.
        """
        md = BaseGraphNumericAnalyzer.max_degree(g)
        gdata = BaseGraphOps.to_edgelist(g)
        nodes = set([v for v in g.V if len(gdata[v.id()]) == md])
        return nodes

    @staticmethod
    def min_degree_vs(g: AbstractGraph) -> Set[AbstractNode]:
        """!
        \brief obtain set of vertices whose degree equal to minimum degree of
        graph instance
        """
        md = BaseGraphNumericAnalyzer.min_degree(g)
        gdata = BaseGraphOps.to_edgelist(g)
        nodes = set([v for v in g.V if len(gdata[v.id()]) == md])
        return nodes

    @staticmethod
    def get_component_nodes(
        root_node_id: str,
        g: AbstractGraph,
        result: Optional[BaseGraphDFSResult] = None,
        edge_generator: Optional[Callable] = None,
        check_cycle: Optional[bool] = None,
    ):
        """
        \brief Get component nodes of a graph

        Given a root node id for a component, obtain its node set.
        """
        if not isinstance(result, BaseGraphDFSResult):
            result = BaseGraphAnalyzer.dfs_props(
                g, edge_generator=edge_generator, check_cycle=check_cycle
            )
        V = {v.id(): v for v in g.V}
        v = V[root_node_id]
        Ts = result.components
        T = Ts[root_node_id]
        T.add(v.id())
        return set([V[v] for v in T])

    @staticmethod
    def get_components_as_node_sets(
        g: AbstractGraph,
        result: Optional[BaseGraphDFSResult] = None,
        edge_generator: Optional[Callable] = None,
        check_cycle: Optional[bool] = None,
    ) -> Set[FrozenSet[AbstractNode]]:
        """!
        \brief obtain component as a set of node sets.

        The node set members of the returning set are of type frozenset due to
        set being an unhashable type in python.
        """
        if not isinstance(result, BaseGraphDFSResult):
            result = BaseGraphAnalyzer.dfs_props(
                g, edge_generator=edge_generator, check_cycle=check_cycle
            )

        if BaseGraphNumericAnalyzer.nb_components(g, result=result) == 1:
            return set([frozenset(g.V)])

        # Extract component roots
        component_roots = [k for k in result.forest.keys()]
        return set(
            [
                frozenset(
                    BaseGraphNodeAnalyzer.get_component_nodes(
                        k, g=g, result=result
                    )
                )
                for k in component_roots
            ]
        )

    @staticmethod
    def find_articulation_points(
        g: AbstractGraph,
        graph_maker: Callable[[AbstractNode], AbstractGraph],
        result: Optional[BaseGraphDFSResult] = None,
        edge_generator: Optional[Callable] = None,
        check_cycle: Optional[bool] = None,
    ) -> Set[AbstractNode]:
        """!
        \brief find articulation points of graph.

        Find the articulation points of a graph. An articulation point, also
        called cut vertex is defined as the vertex that separates two other
        vertices of the same component.

        The algorithm we implement here is the naive version see, Erciyes 2018,
        p. 228. For the definition of the cut vertex, see Diestel 2017, p. 11
        """
        if not isinstance(result, BaseGraphDFSResult):
            result = BaseGraphAnalyzer.dfs_props(
                g, edge_generator=edge_generator, check_cycle=check_cycle
            )

        nb_component = BaseGraphNumericAnalyzer.nb_components(g, result=result)
        points: Set[AbstractNode] = set()
        for node in g.V:
            graph = graph_maker(node)
            nc = BaseGraphNumericAnalyzer.nb_components(graph)
            if nc > nb_component:
                points.add(node)
        return points


class BaseGraphEdgeAnalyzer:
    """!
    Base graph analysis methods that output edge or a set of edges
    """

    @staticmethod
    def find_bridges(
        g: AbstractGraph,
        graph_maker: Callable[[AbstractEdge], AbstractGraph],
        result: Optional[BaseGraphDFSResult] = None,
        edge_generator: Optional[Callable] = None,
        check_cycle: Optional[bool] = None,
    ) -> Set[AbstractEdge]:
        """!
        \brief find bridges of a given graph.

        A bridge is defined as the edge that separates its ends in the same
        component.
        The algorithm we implement here is the naive version provided by Erciyes 2018,
        p. 228. For the definition of the bridge, see Diestel 2017, p. 11
        """
        if not isinstance(result, BaseGraphDFSResult):
            result = BaseGraphAnalyzer.dfs_props(
                g, edge_generator=edge_generator, check_cycle=check_cycle
            )
        nb_component = BaseGraphNumericAnalyzer.nb_components(
            g=g, result=result
        )
        bridges = set()
        for e in g.E:
            made_g = graph_maker(e)
            nc = BaseGraphNumericAnalyzer.nb_components(g=made_g)
            if nc > nb_component:
                bridges.add(e)
        return bridges


class BaseGraphAnalyzer:
    """!
    Analyze base graphs
    """

    @staticmethod
    def get_component(
        root_node_id: str,
        g: AbstractGraph,
        result: Optional[BaseGraphDFSResult] = None,
        edge_generator: Optional[Callable] = None,
        check_cycle: Optional[bool] = None,
    ) -> BaseGraph:
        """!
        \brief get a component graph from graph instance

        As subgraphs are also graphs, components are in the strict sense a
        graph.
        """
        if not isinstance(result, BaseGraphDFSResult):
            result = BaseGraphAnalyzer.dfs_props(
                g, edge_generator=edge_generator, check_cycle=check_cycle
            )

        vertices = BaseGraphNodeAnalyzer.get_component_nodes(
            root_node_id, g=g, result=result
        )

        gdata = BaseGraphOps.to_edgelist(g)
        edges = [gdata[v.id()] for v in vertices]
        E = {e.id(): e for e in g.E}
        es: Set[AbstractEdge] = set()
        for elst in edges:
            for e in elst:
                es.add(E[e])

        return BaseGraph.from_edge_node_set(nodes=vertices, edges=es)

    @staticmethod
    def get_components(
        g: AbstractGraph,
        result: Optional[BaseGraphDFSResult] = None,
        edge_generator: Optional[Callable] = None,
        check_cycle: Optional[bool] = None,
    ) -> Set[BaseGraph]:
        """!
        \brief Get components of graph

        Each component is provided as a graph
        """
        if not isinstance(result, BaseGraphDFSResult):
            result = BaseGraphAnalyzer.dfs_props(
                g, edge_generator=edge_generator, check_cycle=check_cycle
            )

        if BaseGraphNumericAnalyzer.nb_components(g, result=result) == 1:
            return set([g])

        # Extract component roots
        component_roots = [k for k in result.forest.keys()]
        return set(
            [
                BaseGraphAnalyzer.get_component(
                    root_node_id=root, g=g, result=result
                )
                for root in component_roots
            ]
        )

    @staticmethod
    def to_adjmat(g: AbstractGraph, vtype=int) -> Dict[Tuple[str, str], int]:
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
        for v in g.V:
            for k in g.V:
                gmat[(v.id(), k.id())] = vtype(0)
        for edge in g.E:
            tpl1 = (edge.start().id(), edge.end().id())
            tpl2 = (edge.end().id(), edge.start().id())
            if tpl1 in gmat:
                gmat[tpl1] = vtype(1)
            if edge.type() == EdgeType.UNDIRECTED:
                if tpl2 in gmat:
                    gmat[tpl2] = vtype(1)
        return gmat

    @staticmethod
    def transitive_closure_matrix(
        g: AbstractGraph,
    ) -> Dict[Tuple[str, str], bool]:
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
        if BaseGraphBoolAnalyzer.has_self_loop(g):
            raise ValueError("Graph has a self loop")
        #
        T = BaseGraphAnalyzer.to_adjmat(g=g, vtype=bool)
        #
        n = list(g.V)
        for k in n.copy():
            for i in n.copy():
                for j in n.copy():
                    t_ij = T[(i.id(), j.id())]
                    t_ik = T[(i.id(), k.id())]
                    t_ki = T[(i.id(), k.id())]
                    T[(i.id(), j.id())] = t_ij or (t_ik and t_ki)
        T = {(k, i): v for (k, i), v in T.items() if k != i}
        return T

    @staticmethod
    def transitive_closure(g: AbstractGraph):
        """!
        Transitive closure is defined by Nuutila 1995, p. 15 as the following:

        The transitive closure of graph G = (V, E) is a graph G' = (V, E') such that
        E' contains an edge (v, w) iff G contains a non-null path v -> w.

        Notice that the edge is directed, so we are dealing with only directed
        graphs.

        The successor set of a vertex v is the set Succ(v) = {w | (v, w) \in E'
        }, i.e., the set of all vertices that can be reached from vertex v via
        non-null paths.  The predecessor set of a vertex v is the set Pred(v) =
        {u | (u, v) \in E' }, i.e., the set of all vertices that v is reachable
        from via non-null paths. The vertices adjacent from vertex v are the
        immediate successors of v and the vertices adjacent to v are the
        immediate predecessors of v.
        """
        pass

    @staticmethod
    def dfs_props(
        g: AbstractGraph,
        edge_generator: Optional[Callable] = None,
        check_cycle: Optional[bool] = None,
    ) -> BaseGraphDFSResult:
        """"""

        def default_edge_gen(node):
            return BaseGraphEdgeOps.edges_of(g, node)

        if edge_generator is None:
            edge_generator = default_edge_gen
        if check_cycle is None or not isinstance(check_cycle, bool):
            check_cycle = True
        return BaseGraphSearcher.depth_first_search(
            g, edge_generator=edge_generator, check_cycle=check_cycle
        )
