"""!
\file finitegraph.py

\defgroup graphgroup Finite Graph and Related Objects

Contains a general graph object. Most of the functionality is based on 
Diestel 2017.

"""
from typing import Set, Optional, Callable, List, Tuple, Union, Dict, FrozenSet
from gmodels.gtypes.basegraph import BaseGraph
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.gtypes.node import Node
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

    @classmethod
    def from_base_graph(cls, bgraph: BaseGraph):
        "Obtain finite graph from base graph"
        nodes = set(bgraph.V.values())
        edges = set(bgraph.E.values())
        data = bgraph.data()
        gid = bgraph.id()
        return FiniteGraph(gid=gid, nodes=nodes, edges=edges, data=data)

    @classmethod
    def from_edgeset(cls, edges: Set[Edge]):
        g = BaseGraph.from_edgeset(edges)
        return cls.from_base_graph(g)

    @classmethod
    def from_edge_node_set(cls, edges: Set[Edge], nodes: Set[Node]):
        g = BaseGraph.from_edge_node_set(edges=edges, nodes=nodes)
        return cls.from_base_graph(g)

    def vertices(self) -> FrozenSet[Node]:
        """!
        \brief obtain vertex set of the given graph

        \code{.py}

        >>> n1 = Node("n1", {})
        >>> n2 = Node("n2", {})
        >>> e1 = Edge("e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED)
        >>> e2 = Edge("e2", start_node=n1, end_node=n1, edge_type=EdgeType.UNDIRECTED)
        >>> g = Graph("g", nodes=set([n1, n2]), edges=set([e1,e2]))
        >>> g.vertices()
        >>> # set([n1, n2])

        \endcode
        """
        return frozenset([n for n in self.V.values()])

    def nodes(self) -> FrozenSet[Node]:
        """!
        \brief obtain vertex set of the graph
        """
        return self.vertices()

    def edges(self) -> Set[Edge]:
        """!
        \brief obtain edge set of the graph
        """
        return set([n for n in self.E.values()])

    def has_self_loop(self) -> bool:
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
        for edge in self.edges():
            if edge.start() == edge.end():
                return True
        return False

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

    def is_node_independent_of(self, n1: Node, n2: Node) -> bool:
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
        return True if self.is_neighbour_of(n1, n2) is False else False

    def is_stable(self, ns: FrozenSet[Node]) -> bool:
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
        if ns.issubset(self.nodes()) is False:
            raise ValueError("node set is not contained in graph")
        node_list = list(ns)
        while node_list:
            n1 = node_list.pop()
            for n2 in node_list:
                if self.is_neighbour_of(n1=n1, n2=n2):
                    return False
        return True

    def neighbours_of(self, n1: Node) -> Set[Node]:
        """!
        \brief obtain neighbour set of a given node.

        \param n1 the node whose neighbour set we are searching for

        \throws ValueError if node is not inside the graph

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
        >>> neighbours = graph_2.neighbours_of(n2)
        >>> [n.id() for n in neighbours]
        >>> ["n1", "n3"]

        \endcode
        """
        if not self.is_in(n1):
            raise ValueError("node is not in graph")
        neighbours = set()
        for n2 in self.nodes():
            if self.is_neighbour_of(n1=n1, n2=n2) is True:
                neighbours.add(n2)
        return neighbours

    def nb_neighbours_of(self, n: Node) -> int:
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
        return len(self.neighbours_of(n))

    def edges_of(self, n: Node) -> Set[Edge]:
        """!
        \brief obtain the edge set of a given node.

        \param n node whose adjacent edges we are interested in

        \return edge set of node.

        \throw ValueError if node is not in graph we raise a value error

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
        >>> graph = Graph(
        >>>     "g1",
        >>>     data={"my": "graph", "data": "is", "very": "awesome"},
        >>>     nodes=set([n1, n2, n3, n4]),
        >>>     edges=set([e1, e2]),
        >>> )
        >>> edges = graph.edges_of(n2)
        >>> edges == set([e1, e2])
        >>> True

        \endcode
        """
        if not self.is_in(n):
            raise ValueError("node not in Graph")
        edge_ids = self.gdata[n.id()]
        return set([self.E[eid] for eid in edge_ids])

    def outgoing_edges_of(self, n: Node) -> FrozenSet[Edge]:
        """!
        \brief obtain the outgoing edge set of a given node.

        Outgoing edge set means all edges that start with the given node
        and end in another node. This information is mostly trivial for 
        undirected graphs but becomes important for distinguishing 
        parents from children in directed graphs.

        \param n node whose adjacent edges we are interested in

        \return edge set of node.

        \throw ValueError if node is not in graph we raise a value error
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
        >>> graph = Graph(
        >>>     "g1",
        >>>     data={"my": "graph", "data": "is", "very": "awesome"},
        >>>     nodes=set([n1, n2, n3, n4]),
        >>>     edges=set([e1, e2]),
        >>> )
        >>> edges = graph.outgoing_edges_of(n2)
        >>> edges == set([e2])
        >>> True

        \endcode
        """
        if not self.is_in(n):
            raise ValueError("node not in Graph")

        eset = set()
        for eid in self.gdata[n.id()]:
            e = self.E[eid]
            if e.is_start(n):
                eset.add(e)
        return frozenset(eset)

    def incoming_edges_of(self, n: Node) -> FrozenSet[Edge]:
        """!
        \brief obtain incoming edges of a given graph

        Incoming edges are defined as edges that end with the given node.
        We only check for the position and do not consider the type of the edge
        For its use case see \see outgoing_edges_of()
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
        >>> graph = Graph(
        >>>     "g1",
        >>>     data={"my": "graph", "data": "is", "very": "awesome"},
        >>>     nodes=set([n1, n2, n3, n4]),
        >>>     edges=set([e1, e2]),
        >>> )
        >>> edges = graph.incoming_edges_of(n2)
        >>> edges == set([e1])
        >>> True

        \endcode
        """
        if not self.is_in(n):
            raise ValueError("node not in Graph")

        eset = set()
        for eid in self.gdata[n.id()]:
            e = self.E[eid]
            if e.is_end(n):
                eset.add(e)
        return frozenset(eset)

    def edges_by_end(self, n: Node) -> Set[Edge]:
        """!
        \brief obtain edge set of node.

        This function should not be confused with incoming_edges_of() or
        outgoing_edges_of() functions.
        This function provides the edge set of the given node considering the
        type of the edge as well.

        If the edge is undirected, it is going to be included in the set if the
        node is an endvertex of it.  If the edge is directed, it is going to be
        included in the set if the node is at the end position of the vertex.

        \code{.py}
        >>> n1 = Node("n1", {})
        >>> n2 = Node("n2", {})
        >>> e1 = Edge("e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED)
        >>> e2 = Edge("e2", start_node=n1, end_node=n1, edge_type=EdgeType.UNDIRECTED)
        >>> g = Graph("g", nodes=set([n1, n2]), edges=set([e1,e2]))
        >>> g.edges_by_end(n2) == set([e1])
        >>> # True

        \endcode
        """
        es: Set[Edge] = set()
        for e_id in self.E:
            edge = self.E[e_id]
            if edge.is_end(n):
                es.add(edge)
        return es
