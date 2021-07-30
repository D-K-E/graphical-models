"""!
\file bgraphops.py BaseGraph operations implemented for BaseGraph and its subclasses
"""

from typing import Set, Optional, Callable, List, Tuple, Union, Dict, FrozenSet
from pygmodels.gtype.abstractobj import AbstractGraph, AbstractUndiGraph
from pygmodels.gtype.abstractobj import AbstractGraph, AbstractDiGraph
from pygmodels.gtype.abstractobj import AbstractNode, AbstractEdge

from uuid import uuid4
import math


class BaseGraphOps:
    """!
    \brief Basic operations defined for all (directed/undirected) graphs
    """

    @staticmethod
    def get_nodes(
        ns: Optional[Set[AbstractNode]], es: Optional[Set[AbstractEdge]],
    ) -> Dict[str, AbstractNode]:
        """!
        \brief Obtain all nodes in a single set.

        \param ns set of nodes
        \param es set of edges

        We assume that node set and edge set might contain different nodes,
        that is \f$ V[G] = V[ns] \cup V[es] \f$
        We combine nodes given in both sets to create a final set of nodes
        for the graph
        """
        nodes = set()
        if ns is None:
            return
        for n in ns:
            nodes.add(n)
        if es is not None:
            for e in es:
                estart = e.start()
                eend = e.end()
                nodes.add(estart)
                nodes.add(eend)
        #
        return {n.id(): n for n in nodes}

    @staticmethod
    def to_edgelist(g: AbstractGraph) -> Dict[str, str]:
        """!
        \brief Create edge list representation of graph

        For each node we register the edges.
        """
        _nodes = BaseGraphOps.get_nodes(ns=set(g.V.values()), es=set(g.E.values()))
        gdata = {}
        for vertex in _nodes.values():
            gdata[vertex.id()] = []
        #
        for edge in g.E.values():
            for node_id in edge.node_ids():
                elist = gdata.get(node_id, None)
                if elist is None:
                    gdata[node_id] = []
                else:
                    gdata[node_id].append(edge.id())
        return gdata

    @staticmethod
    def vertices(g: AbstractGraph) -> FrozenSet[AbstractNode]:
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
        return frozenset([n for n in g.V.values()])

    @staticmethod
    def nodes(g: AbstractGraph) -> FrozenSet[AbstractNode]:
        """!
        \brief obtain vertex set of the graph
        """
        return BaseGraphOps.vertices(g)

    @staticmethod
    def edges(g: AbstractGraph) -> FrozenSet[AbstractEdge]:
        """!
        \brief obtain edge set of the graph
        """
        return frozenset([n for n in g.E.values()])

    @staticmethod
    def neighbours_of(g: AbstractGraph, n1: AbstractEdge) -> Set[AbstractNode]:
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
        if not BaseGraphOps.is_in(g, n1):
            raise ValueError("node is not in graph")
        neighbours = set()
        for n2 in BaseGraphOps.nodes(g):
            if g.is_neighbour_of(n1=n1, n2=n2) is True:
                neighbours.add(n2)
        return neighbours

    @staticmethod
    def is_in(g: AbstractGraph, ne: Union[AbstractNode, AbstractEdge]) -> bool:
        """!
        \brief check if given edge or node is in graph

        We check if given graph object is in the graph.
        \throws TypeError if the argument is not a node or an edge
        """
        if isinstance(ne, AbstractNode):
            return ne.id() in g.V
        elif isinstance(ne, AbstractEdge):
            return ne.id() in g.E
        else:
            raise TypeError("Given argument should be either edge or node")

    @staticmethod
    def edges_of(g: AbstractGraph, n: AbstractNode) -> Set[AbstractEdge]:
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

        if not BaseGraphOps.is_in(g, n):
            raise ValueError("node not in Graph")
        gdata = BaseGraphOps.to_edgelist(g)
        edge_ids = gdata[n.id()]
        return set([g.E[eid] for eid in edge_ids])

    @staticmethod
    def outgoing_edges_of(g: AbstractGraph, n: AbstractNode) -> FrozenSet[AbstractEdge]:
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
        if not BaseGraphOps.is_in(g, n):
            raise ValueError("node not in Graph")

        eset = set()
        gdata = BaseGraphOps.to_edgelist(g)
        for eid in gdata[n.id()]:
            e = g.E[eid]
            if e.is_start(n):
                eset.add(e)
        return frozenset(eset)

    @staticmethod
    def incoming_edges_of(g: AbstractGraph, n: AbstractNode) -> FrozenSet[AbstractEdge]:
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
        if not BaseGraphOps.is_in(g, n):
            raise ValueError("node not in Graph")

        eset = set()
        gdata = BaseGraphOps.to_edgelist(g)
        for eid in gdata[n.id()]:
            e = g.E[eid]
            if e.is_end(n):
                eset.add(e)
        return frozenset(eset)

    @staticmethod
    def edges_by_end(g: AbstractGraph, n: AbstractNode) -> Set[AbstractEdge]:
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
        for e_id in g.E:
            edge = g.E[e_id]
            if edge.is_end(n):
                es.add(edge)
        return es

    @staticmethod
    def vertex_by_id(g: AbstractGraph, node_id: str) -> AbstractNode:
        """!
        \brief obtain vertex by using its identifier
        \throws ValueError if the node is not in graph
        """
        if node_id not in g.V:
            raise ValueError("node id not in graph")
        return g.V[node_id]

    @staticmethod
    def edge_by_id(g: AbstractGraph, edge_id: str) -> AbstractEdge:
        """!
        \brief obtain edge by using its identifier
        \throws ValueError if the edge id is not in graph
        """
        if edge_id not in g.E:
            raise ValueError("edge id not in graph")
        return g.E[edge_id]

    @staticmethod
    def edge_by_vertices(
        g: AbstractGraph, start: AbstractNode, end: AbstractNode
    ) -> Set[AbstractEdge]:
        """!
        \brief obtain edge set by using its vertices.

        We take all edges that consist of given two nodes

        \throws ValueError if any of argument nodes are not inside the graph.
        \throws ValueError if there are no edges that consist of argument nodes.
        """
        if not BaseGraphOps.is_in(g, start) or not BaseGraphOps.is_in(g, end):
            raise ValueError("one of the nodes is not present in graph")
        n1id = start.id()
        n2id = end.id()
        gdata = BaseGraphOps.to_edgelist(g)
        first_eset = set(gdata[n1id])
        second_eset = set(gdata[n2id])
        common_edge_ids = first_eset.intersection(second_eset)
        if len(common_edge_ids) == 0:
            raise ValueError("No common edges between given nodes")
        return set([g.E[e] for e in common_edge_ids])

    @staticmethod
    def vertices_of(
        g: AbstractGraph, e: AbstractEdge
    ) -> Tuple[AbstractNode, AbstractNode]:
        """!
        \brief obtain all vertices associated with an edge.

        \throws ValueError if edge is not inside the graph
        """
        if BaseGraphOps.is_in(g, e):
            return (e.start(), e.end())
        else:
            raise ValueError("edge not in graph")
