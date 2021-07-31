"""!
\file graphanalyzer.py Graph Analyzer for BaseGraph subclasses
"""

import math
from typing import Callable, Dict, FrozenSet, List, Optional, Set, Tuple, Union

from pygmodels.graphf.bgraphops import BaseGraphOps
from pygmodels.gtype.abstractobj import (
    AbstractEdge,
    AbstractGraph,
    AbstractNode,
)


class BaseGraphAnalyzer:
    """!
    Analyze base graphs
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
        for edge in BaseGraphOps.edges(g):
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
        return True if g.is_neighbour_of(n1, n2) is False else False

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
        if ns.issubset(BaseGraphOps.nodes(g)) is False:
            raise ValueError("node set is not contained in graph")
        node_list = list(ns)
        while node_list:
            n1 = node_list.pop()
            for n2 in node_list:
                if g.is_neighbour_of(n1=n1, n2=n2):
                    return False
        return True

    @staticmethod
    def is_trivial(g: AbstractGraph) -> bool:
        """!
        \brief check if graph is trivial.
        This triviality condition is taken from
        Diestel 2017, p. 2
        """
        return BaseGraphAnalyzer.order(g) < 2

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
            nb_edges = len(gdata[nid])
            if fn(nb_edges, compare_v):
                compare_v = nb_edges
        return compare_v

    @staticmethod
    def max_degree(g: AbstractGraph) -> int:
        """!
        \brief obtain maximum degree of the graph instance
        """
        v = BaseGraphAnalyzer.comp_degree(
            g, fn=lambda nb_edges, compare: nb_edges > compare, comp_val=0
        )
        return v

    @staticmethod
    def max_degree_vs(g: AbstractGraph) -> Set[AbstractNode]:
        """!
        \brief obtain vertex set of whose degrees are equal to maximum degree.
        """
        md = BaseGraphAnalyzer.max_degree(g)
        gdata = BaseGraphOps.to_edgelist(g)
        nodes = set()
        for nid in g.V:
            if len(gdata[nid]) == md:
                nodes.add(g.V[nid])
        return nodes

    @staticmethod
    def min_degree(g: AbstractGraph) -> int:
        """!
        \brief obtain minimum degree of graph instance
        """
        return int(
            BaseGraphAnalyzer.comp_degree(
                g,
                fn=lambda nb_edges, compare: nb_edges < compare,
                comp_val=math.inf,
            )
        )

    @staticmethod
    def min_degree_vs(g: AbstractGraph) -> Set[AbstractNode]:
        """!
        \brief obtain set of vertices whose degree equal to minimum degree of
        graph instance
        """
        md = BaseGraphAnalyzer.min_degree(g)
        gdata = BaseGraphOps.to_edgelist(g)
        nodes = set()
        for nid in g.V:
            if len(gdata[nid]) == md:
                nodes.add(g.V[nid])
        return nodes

    @staticmethod
    def average_degree(g: AbstractGraph) -> float:
        """!
        \brief obtain the average degree of graph instance

        The average degree is calculated using the formula:
        \f[ d(G) = \frac{1}{V[G]} \sum_{v \in V[G]} d(v) \f]

        It can be found in Diestel 2017, p. 5
        """
        gdata = BaseGraphOps.to_edgelist(g)
        return sum([len(gdata[nid]) for nid in g.V]) / len(g.V)

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
        adegree = BaseGraphAnalyzer.average_degree(g)
        return BaseGraphAnalyzer.ev_ratio_from_average_degree(g, adegree)

    @staticmethod
    def has_cycles(g: AbstractGraph) -> bool:
        """!
        \brief Check if graph instance contains cycles.
        This interpretation is from Diestel 2017, p. 8. The
        proof is provided in the given page.
        """
        md = BaseGraphAnalyzer.min_degree(g)
        if md >= 2:
            return True
        return False

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
        return len(BaseGraphOps.neighbours_of(g, n))

    @staticmethod
    def nb_edges(g: AbstractGraph) -> int:
        """!
        \brief obtain number of edges in the graph
        It corresponds to \f$ ||G|| \f$.
        This interpretation is taken from Diestel 2017, p. 2.
        """
        return len(g.E)

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
    def is_tree(g: AbstractGraph) -> bool:
        raise NotImplementedError

    @staticmethod
    def find_articulation_points(
        g: AbstractGraph, graph_maker=Callable[[AbstractNode], AbstractGraph]
    ):
        """"""
        raise NotImplementedError

    @staticmethod
    def find_bridges(
        g: AbstractGraph, graph_maker=Callable[[AbstractNode], AbstractGraph]
    ):
        """"""
        pass
