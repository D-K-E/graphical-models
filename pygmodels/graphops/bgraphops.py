"""!
\file bgraphops.py BaseGraph operations implemented for BaseGraph and its subclasses
"""

import math
from typing import Callable, Dict, FrozenSet, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pygmodels.gtype.abstractobj import (
    AbstractDiGraph,
    AbstractEdge,
    AbstractGraph,
    AbstractNode,
    AbstractUndiGraph,
    EdgeType,
)


class BaseGraphBoolOps:
    """"""

    @staticmethod
    def is_in(g: AbstractGraph, ne: Union[AbstractNode, AbstractEdge]) -> bool:
        """!
        \brief check if given edge or node is in graph

        We check if given graph object is in the graph.
        \throws TypeError if the argument is not a node or an edge
        """
        if isinstance(ne, AbstractNode):
            return ne.id() in {v.id() for v in g.V}
        elif isinstance(ne, AbstractEdge):
            return ne.id() in {e.id() for e in g.E}
        else:
            raise TypeError("Given argument should be either edge or node")

    @staticmethod
    def is_adjacent_of(
        g: AbstractGraph, e1: AbstractEdge, e2: AbstractEdge
    ) -> bool:
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
        if not BaseGraphBoolOps.is_in(g, e1):
            raise ValueError("edge not in Graph")

        if not BaseGraphBoolOps.is_in(g, e2):
            raise ValueError("edge not in Graph")

        n1_ids = e1.node_ids()
        n2_ids = e2.node_ids()
        return len(n1_ids.intersection(n2_ids)) > 0

    @staticmethod
    def is_node_incident(
        g: AbstractGraph, n: AbstractNode, e: AbstractEdge
    ) -> bool:
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
        if not BaseGraphBoolOps.is_in(g, e):
            raise ValueError("edge not in Graph")

        if not BaseGraphBoolOps.is_in(g, n):
            raise ValueError("node not in Graph")

        return e.is_endvertice(n)

    @staticmethod
    def is_related_to(
        g: AbstractGraph,
        n1: AbstractNode,
        n2: AbstractNode,
        condition: Callable[[AbstractNode, AbstractNode, AbstractEdge], bool],
        es: FrozenSet[AbstractEdge] = None,
    ) -> bool:
        """!
        \brief Generic function for applying proximity conditions on a node pair

        \param n1 first node subject to proximity condition
        \param n2 second node subject to proximity condition
        \param condition proximity condition in the form of a callable.
        \param es edge set. We query the proximity condition in this set if it
        is specified

        We check whether a proximity condition is valid for given two nodes.
        """
        if es is None:
            es = frozenset(g.E)
        for e in es:
            if condition(n1, n2, e) is True:
                return True
        return False

    @staticmethod
    def is_neighbour_of(
        g: AbstractGraph, n1: AbstractNode, n2: AbstractNode
    ) -> bool:
        """!
        \brief check if two nodes are neighbours
        We define the condition of neighborhood as having a common edge, not
        being the same

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
        >>> graph_2.is_neighbour_of(n2, n3)
        >>> True
        >>> graph_2.is_neighbour_of(n2, n2)
        >>> False

        \endcode
        """
        if not BaseGraphBoolOps.is_in(g, n1):
            raise ValueError("node not in graph")

        if not BaseGraphBoolOps.is_in(g, n2):
            raise ValueError("node not in graph")

        def cond(
            n_1: AbstractNode, n_2: AbstractNode, e: AbstractEdge
        ) -> bool:
            """!
            \brief neighborhood condition
            """
            estart = e.start()
            eend = e.end()
            c1 = estart == n_1 and eend == n_2
            c2 = estart == n_2 and eend == n_1
            return c1 or c2

        gdata = BaseGraphOps.to_edgelist(g)

        n1_edge_ids = set(gdata[n1.id()])
        n2_edge_ids = set(gdata[n2.id()])
        edge_ids = n1_edge_ids.intersection(n2_edge_ids)
        # filter self loops
        edges = set([e for e in g.E if e.id() in edge_ids])
        return BaseGraphBoolOps.is_related_to(
            g, n1=n1, n2=n2, condition=cond, es=edges
        )


class BaseGraphEdgeOps:
    """
    \brief Operations that output edge or set of edges involving base graphs
    """

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

        if not BaseGraphBoolOps.is_in(g, n):
            raise ValueError("node not in Graph")
        gdata = BaseGraphOps.to_edgelist(g)
        edge_ids = gdata[n.id()]
        E = {e.id(): e for e in g.E}
        return set([E[eid] for eid in edge_ids])

    @staticmethod
    def outgoing_edges_of(
        g: AbstractGraph, n: AbstractNode
    ) -> FrozenSet[AbstractEdge]:
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
        if not BaseGraphBoolOps.is_in(g, n):
            raise ValueError("node not in Graph")

        eset = set()
        E = {e.id(): e for e in g.E}
        gdata = BaseGraphOps.to_edgelist(g)
        for eid in gdata[n.id()]:
            e = E[eid]
            if e.is_start(n):
                eset.add(e)
        return frozenset(eset)

    @staticmethod
    def incoming_edges_of(
        g: AbstractGraph, n: AbstractNode
    ) -> FrozenSet[AbstractEdge]:
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
        if not BaseGraphBoolOps.is_in(g, n):
            raise ValueError("node not in Graph")

        eset = set()
        gdata = BaseGraphOps.to_edgelist(g)
        E = {e.id(): e for e in g.E}
        for eid in gdata[n.id()]:
            e = E[eid]
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
        if not BaseGraphBoolOps.is_in(g, n):
            raise ValueError("node not in graph")

        return {e for e in g.E if e.is_end(n)}

    @staticmethod
    def edges(g: AbstractGraph) -> FrozenSet[AbstractEdge]:
        """!
        \brief obtain edge set of the graph
        """
        return frozenset([n for n in g.E])

    @staticmethod
    def edge_by_id(g: AbstractGraph, edge_id: str) -> AbstractEdge:
        """!
        \brief obtain edge by using its identifier
        \throws ValueError if the edge id is not in graph
        """
        E = {e.id(): e for e in g.E}
        if edge_id not in E:
            raise ValueError("edge id not in graph")
        return E[edge_id]

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
        if not BaseGraphBoolOps.is_in(g, start) or not BaseGraphBoolOps.is_in(
            g, end
        ):
            raise ValueError("one of the nodes is not present in graph")
        n1id = start.id()
        n2id = end.id()
        gdata = BaseGraphOps.to_edgelist(g)
        first_eset = set(gdata[n1id])
        second_eset = set(gdata[n2id])
        common_edge_ids = first_eset.intersection(second_eset)
        if len(common_edge_ids) == 0:
            raise ValueError("No common edges between given nodes")
        return set([e for e in g.E if e.id() in common_edge_ids])


class BaseGraphNodeOps:
    """
    \brief Operations that output a node or a set of nodes involving graphs
    """

    @staticmethod
    def get_nodes(
        ns: Optional[Set[AbstractNode]],
        es: Optional[Set[AbstractEdge]],
    ) -> FrozenSet[AbstractNode]:
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
        return frozenset(nodes)

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
        return frozenset([n for n in g.V])

    @staticmethod
    def nodes(g: AbstractGraph) -> FrozenSet[AbstractNode]:
        """!
        \brief obtain vertex set of the graph
        """
        return BaseGraphOps.vertices(g)

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
        if not BaseGraphBoolOps.is_in(g, n1):
            raise ValueError("node is not in graph")
        neighbours = set()
        for n2 in g.V:
            if BaseGraphBoolOps.is_neighbour_of(g, n1=n1, n2=n2) is True:
                neighbours.add(n2)
        return neighbours

    @staticmethod
    def vertex_by_id(g: AbstractGraph, node_id: str) -> AbstractNode:
        """!
        \brief obtain vertex by using its identifier
        \throws ValueError if the node is not in graph
        """
        V = {v.id(): v for v in g.V}
        if node_id not in V:
            raise ValueError("node id not in graph")
        return V[node_id]

    @staticmethod
    def vertices_of(
        g: AbstractGraph, e: AbstractEdge
    ) -> Tuple[AbstractNode, AbstractNode]:
        """!
        \brief obtain all vertices associated with an edge.

        \throws ValueError if edge is not inside the graph
        """
        if BaseGraphBoolOps.is_in(g, e):
            return (e.start(), e.end())
        else:
            raise ValueError("edge not in graph")


class BaseGraphOps:
    """!
    \brief Basic operations defined for all (directed/undirected) graphs
    """

    @staticmethod
    def to_edgelist(g: AbstractGraph) -> Dict[str, str]:
        """!
        \brief Create edge list representation of graph

        For each node we register the edges.
        """
        _nodes = BaseGraphNodeOps.get_nodes(ns=set(g.V), es=set(g.E))
        gdata = {}
        for vertex in _nodes:
            gdata[vertex.id()] = []
        #
        for edge in g.E:
            for node_id in edge.node_ids():
                elist = gdata.get(node_id, None)
                if elist is None:
                    gdata[node_id] = []
                else:
                    gdata[node_id].append(edge.id())
        return gdata

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
    def get_subgraph_by_vertices(
        g: AbstractGraph,
        vs: Set[AbstractNode],
        edge_policy: Callable[
            [AbstractEdge, Set[AbstractNode]], bool
        ] = lambda x, ys: set([x.start(), x.end()]).issubset(ys)
        is True,
    ) -> Tuple[Set[AbstractNode], Set[AbstractEdge]]:
        """!
        Get the subgraph using vertices.

        \param vs set of vertices for the subgraph
        \param edge_policy determines which edges should be conserved. By
        default we conserve edges whose incident nodes are a subset of vs
        """
        if not all(BaseGraphBoolOps.is_in(g, v) for v in vs):
            raise ValueError("Given nodes are not contained in graph")
        es: Set[AbstractEdge] = set()
        for e in g.E:
            if edge_policy(e, vs) is True:
                es.add(e)
        return (vs, es)
