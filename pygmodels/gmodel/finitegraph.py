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
        self.mk_nodes(ns=nodes, es=edges)
        self.mk_gdata()

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
        return FiniteGraph(gid=gid, nodes=nodes, edges=edges, data=data)

    @classmethod
    def from_edgeset(cls, edges: Set[Edge]):
        g = BaseGraph.from_edgeset(edges)
        return cls.from_base_graph(g)

    @classmethod
    def from_edge_node_set(cls, edges: Set[Edge], nodes: Set[Node]):
        g = BaseGraph.from_edge_node_set(edges=edges, nodes=nodes)
        return cls.from_base_graph(g)

    def mk_nodes(self, ns: Optional[Set[Node]], es: Optional[Set[Edge]]):
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
        self._nodes = {n.id(): n for n in nodes}

    def mk_gdata(self):
        """!
        \brief Create edge list representation of graph

        For each node we register the edges.
        """
        if self._nodes is not None:
            for vertex in self._nodes.values():
                self.gdata[vertex.id()] = []
            #
            for edge in self._edges.values():
                for node_id in edge.node_ids():
                    elist = self.gdata.get(node_id, None)
                    if elist is None:
                        self.gdata[node_id] = []
                    else:
                        self.gdata[node_id].append(edge.id())

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

    def edges(self) -> FrozenSet[Edge]:
        """!
        \brief obtain edge set of the graph
        """
        return frozenset([n for n in self.E.values()])

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

    def is_in(self, ne: Union[Node, Edge]) -> bool:
        """!
        \brief check if given edge or node is in graph

        We check if given graph object is in the graph.
        \throws TypeError if the argument is not a node or an edge
        """
        if isinstance(ne, Node):
            return ne.id() in self.V
        elif isinstance(ne, Edge):
            return ne.id() in self.E
        else:
            raise TypeError("Given argument should be either edge or node")

    def nb_edges(self) -> int:
        """!
        \brief obtain number of edges in the graph
        It corresponds to \f$ ||G|| \f$.
        This interpretation is taken from Diestel 2017, p. 2.
        """
        return len(self.E)

    def vertex_by_id(self, node_id: str) -> Node:
        """!
        \brief obtain vertex by using its identifier
        \throws ValueError if the node is not in graph
        """
        if node_id not in self.V:
            raise ValueError("node id not in graph")
        return self.V[node_id]

    def edge_by_id(self, edge_id: str) -> Edge:
        """!
        \brief obtain edge by using its identifier
        \throws ValueError if the edge id is not in graph
        """
        if edge_id not in self.E:
            raise ValueError("edge id not in graph")
        return self.E[edge_id]

    def edge_by_vertices(self, start: Node, end: Node) -> Set[Edge]:
        """!
        \brief obtain edge set by using its vertices.

        We take all edges that consist of given two nodes

        \throws ValueError if any of argument nodes are not inside the graph.
        \throws ValueError if there are no edges that consist of argument nodes.
        """
        if not self.is_in(start) or not self.is_in(end):
            raise ValueError("one of the nodes is not present in graph")
        n1id = start.id()
        n2id = end.id()
        first_eset = set(self.gdata[n1id])
        second_eset = set(self.gdata[n2id])
        common_edge_ids = first_eset.intersection(second_eset)
        if len(common_edge_ids) == 0:
            raise ValueError("No common edges between given nodes")
        return set([self.E[e] for e in common_edge_ids])

    def vertices_of(self, e: Edge) -> Tuple[Node, Node]:
        """!
        \brief obtain all vertices associated with an edge.

        \throws ValueError if edge is not inside the graph
        """
        if self.is_in(e):
            return (e.start(), e.end())
        else:
            raise ValueError("edge not in graph")

    def set_op(
        self,
        obj: Union[Set[Node], Set[Edge], BaseGraph],
        op: Callable[[Union[Set[Node], Set[Edge]]], Union[Set[Node], Set[Edge], bool]],
    ) -> Optional[Union[Set[Node], Set[Edge], bool]]:
        """!
        \brief generic set operation for graph

        \param obj the hooked object to operation. We deduce its corresponding
        argument from its type.
        \param op operation that is going to be applied to obj and its
        corresponding object.

        The idea is to give a single interface for generic set operation
        functions. For example if object is a set of nodes we provide
        the target for the operation as the nodes of this graph, if it is an
        edge we provide a set of edges of this graph
        """
        if isinstance(obj, (set, frozenset)):
            lst = list(obj)
            if isinstance(lst[0], Node):
                return op(self.nodes())
            else:
                return op(self.edges())
        elif not isinstance(obj, BaseGraph):
            raise TypeError("object should be either node/edge set or base graph")
        return None

    def intersection(
        self, aset: Union[Set[Node], Set[Edge], BaseGraph]
    ) -> Union[Set[Node], Set[Edge], BaseGraph]:
        """!
        \brief obtain intersection of either node or edge set
        """
        v = self.set_op(obj=aset, op=lambda x: x.intersection(aset))
        if v is None:
            return self.graph_intersection(aset)
        return v

    def union(
        self, aset: Union[Set[Node], Set[Edge], BaseGraph]
    ) -> Union[Set[Node], Set[Edge], BaseGraph]:
        """!
        \brief obtain union of either node or edge set
        """
        v = self.set_op(obj=aset, op=lambda x: x.union(aset))
        if v is None:
            return self.graph_union(aset)
        return v

    def difference(
        self, aset: Union[Set[Node], Set[Edge], BaseGraph]
    ) -> Union[Set[Node], Set[Edge], BaseGraph]:
        """!
        \brief obtain set difference of either node or edge set
        """
        v = self.set_op(obj=aset, op=lambda x: x.difference(aset))
        if v is None:
            return self.graph_difference(aset)
        return v

    def symmetric_difference(
        self, aset: Union[Set[Node], Set[Edge], BaseGraph]
    ) -> Union[Set[Node], Set[Edge], BaseGraph]:
        """!
        \brief obtain symmetric set difference of either node or edge set.
        """
        v = self.set_op(obj=aset, op=lambda x: x.symmetric_difference(aset))
        if v is None:
            return self.graph_symmetric_difference(aset)
        return v

    def contains(self, a: Union[Set[Edge], Set[Node], BaseGraph]) -> bool:
        """!
        \brief check if argument set of nodes or edges is contained by graph
        """
        v = self.set_op(obj=a, op=lambda x: a.issubset(x) is True)
        if v is None:
            return self.contains(a.nodes()) and self.contains(a.edges())
        return v

    def graph_intersection(self, gs):
        """!
        \brief intersection operation adapted for graph.

        Intersection of graph with another is the graph resulting from
        intersection sets of their nodes and their edges.
        """
        ns: Set[Node] = gs.nodes()
        es: Set[Edge] = gs.edges()
        es_ = self.intersection(es)
        ns_ = self.intersection(ns)
        return FiniteGraph(gid=str(uuid4()), nodes=ns_, edges=es_)

    def graph_union(self, gs):
        """!
        \brief union operation adapted for graph.

        Union of graph with another is the graph resulting from
        union sets of their nodes and their edges.
        """
        ns: Set[Node] = gs.nodes()
        es: Set[Edge] = gs.edges()
        es_ = self.union(es)
        ns_ = self.union(ns)
        return FiniteGraph(gid=str(uuid4()), nodes=ns_, edges=es_)

    def graph_difference(self, gs):
        """!
        \brief set difference operation adapted for graph.

        Difference of graph with another is the graph resulting from
        set difference sets of their nodes and their edges.
        """

        ns: Set[Node] = gs.nodes()
        es: Set[Edge] = gs.edges()
        es_ = self.difference(es)
        # ensure that edges do not contain
        # a node that is in gs
        ess = set()
        for e in es_:
            ids = e.node_ids()
            if all([i not in gs.V for i in ids]):
                ess.add(e)
        ns_ = self.difference(ns)
        return FiniteGraph(gid=str(uuid4()), nodes=ns_, edges=ess)

    def graph_symmetric_difference(self, gs):
        """!
        \brief symmetric set difference operation adapted for graph.
        """
        ns: Set[Node] = gs.nodes()
        es: Set[Edge] = gs.edges()
        es_ = self.symmetric_difference(es)
        ns_ = self.symmetric_difference(ns)
        return FiniteGraph(gid=str(uuid4()), nodes=ns_, edges=es_)

    def _subtract_node(self, n: Node) -> Tuple[Set[Node], Set[Edge]]:
        """!
        \brief subtract a given node from graph

        Output a node and edge set which do not contain the node.

        \todo This function look extra correct and elegant but it is quite
        inefficient with respect to look ups.
        """
        if not isinstance(n, Node):
            raise TypeError("argument is not an instance of node")
        n_id = n.id()
        nnodes: Set[Node] = set([self.V[v] for v in self.V if v != n_id])
        nedges: Set[Edge] = set(
            [self.E[e] for e in self.E if n_id not in self.E[e].node_ids()]
        )
        return (nnodes, nedges)

    def subtract_node_from_self(self, n: Node):
        """!
        \brief subtract given node from the graph instance
        """
        nodes, edges = self._subtract_node(n)
        self._nodes = {n.id(): n for n in nodes}
        self._edges = {e.id(): e for e in edges}

    def subtract_node(self, n: Node):
        """!
        \brief create a new graph by subtracting the argument node.
        """
        nodes, edges = self._subtract_node(n)
        data = self.data()
        return FiniteGraph(gid=str(uuid4()), data=data, nodes=nodes, edges=edges)

    def subtract_nodes_from_self(self, ns: Set[Node]):
        """!
        \brief subtract the set of nodes from graph instance
        """
        for n in ns:
            self.subtract_node_from_self(n)

    def subtract_nodes(self, ns: Set[Node]):
        """!
        \brief create a new graph by subtracting given set of nodes from graph instance
        """
        nslst = list(ns)
        if len(nslst) == 1:
            return self.subtract_node(nslst.pop())
        nn = nslst.pop()
        g = self.subtract_node(nn)
        g.subtract_nodes_from_self(nslst)
        return g

    def _subtract_edge(self, e: Edge) -> Set[Edge]:
        """!
        \brief subtract an edge from graph's edge set

        By default we do not remove the nodes associated with the edge.
        """
        if not isinstance(e, Edge):
            raise TypeError("argument is not an instance of edge")
        edges = self.edges()
        nedges: Set[Edge] = set()
        for edge in edges:
            if e != edge:
                nedges.add(edge)
        return nedges

    def subtract_edge_from_self(self, e: Edge):
        """!
        \brief subtract edge from edge set of graph instance
        """
        edges = self._subtract_edge(e)
        self._edges = {e.id(): e for e in edges}

    def subtract_edge(self, e: Edge) -> BaseGraph:
        """!
        \brief create a new graph by subtracting edge from edge set of graph instance
        \see subtract_node() as well
        """
        edges = self._subtract_edge(e)
        return FiniteGraph(
            gid=str(uuid4()), data=self.data(), nodes=self.nodes(), edges=edges
        )

    def subtract_edge_with_nodes(self, e) -> BaseGraph:
        """!
        \brief subtract edge and remove its nodes as well.
        """
        edges = self._subtract_edge(e)
        enode1, enode2 = e.start(), e.end()
        nodes = self.nodes()
        nodes = nodes.difference(set([enode1, enode2]))
        return FiniteGraph(gid=str(uuid4()), nodes=nodes, edges=edges)

    def subtract(self, a: Union[Node, Edge]):
        """!
        \brief Generic subtraction operation
        """
        if isinstance(a, Node):
            return self.subtract_node(a)
        elif isinstance(a, Edge):
            return self.subtract_edge(a)
        else:
            raise TypeError("Argument must be node or edge: " + str(type(a)))

    def subtract_edges_from_self(self, es: Set[Edge]):
        """!
        \brief subtract edge set from graph instance
        """
        for e in es:
            self.subtract_edge_from_self(e)

    def subtract_edges(self, es: Set[Edge]):
        """!
        \brief create a new graph by subtracting edge set from graph instance
        """
        nslst = list(es)
        if len(nslst) == 1:
            return self.subtract_edge(nslst.pop())
        nn = nslst.pop()
        g = self.subtract_edge(nn)
        g.subtract_edges_from_self(nslst)
        return g

    def added_edge_between_if_none(self, n1: Node, n2: Node) -> bool:
        """!
        Add edges between nodes if there are no edges in between
        """
        try:
            es = self.edge_by_vertices(n1, n2)
        except ValueError:
            e = Edge(edge_id=str(uuid4()), data={}, start_node=n1, end_node=n2)
            self.add_edge_to_self(e)
            return True
        return False

    def add_edge_to_self(self, e: Edge):
        """!
        """
        edges = set(self.edges())
        edges.add(e)
        self._edges = {e.id(): e for e in edges}

    def add_edge(self, e: Edge):
        ""
        edges = set(self.edges())
        edges.add(e)
        return FiniteGraph(
            gid=str(uuid4()), data=self.data(), nodes=self.nodes(), edges=edges
        )

    def add_edges_to_self(self, es: Set[Edge]):
        ""
        for e in es:
            self.add_edges_to_self(e)

    def add_edges(self, es: Set[Edge]):
        ""
        for e in es:
            self = self.add_edge(e)

    def comp_degree(self, fn: Callable[[int, int], bool], comp_val: int) -> int:
        """!
        \brief generic comparison function for degree related operations

        It is used in the context of finding maximum or minimum degree of the
        graph instance.
        """
        compare_v = comp_val
        for nid in self.V:
            nb_edges = len(self.gdata[nid])
            if fn(nb_edges, compare_v):
                compare_v = nb_edges
        return compare_v

    def max_degree(self) -> int:
        """!
        \brief obtain maximum degree of the graph instance
        """
        v = self.comp_degree(
            fn=lambda nb_edges, compare: nb_edges > compare, comp_val=0
        )
        return v

    def max_degree_vs(self) -> Set[Node]:
        """!
        \brief obtain vertex set of whose degrees are equal to maximum degree.
        """
        md = self.max_degree()
        nodes = set()
        for nid in self.V:
            if len(self.gdata[nid]) == md:
                nodes.add(self.V[nid])
        return nodes

    def min_degree(self) -> int:
        """!
        \brief obtain minimum degree of graph instance
        """
        return int(
            self.comp_degree(
                fn=lambda nb_edges, compare: nb_edges < compare, comp_val=math.inf
            )
        )

    def min_degree_vs(self) -> Set[Node]:
        """!
        \brief obtain set of vertices whose degree equal to minimum degree of
        graph instance
        """
        md = self.min_degree()
        nodes = set()
        for nid in self.V:
            if len(self.gdata[nid]) == md:
                nodes.add(self.V[nid])
        return nodes

    def average_degree(self) -> float:
        """!
        \brief obtain the average degree of graph instance

        The average degree is calculated using the formula:
        \f[ d(G) = \frac{1}{V[G]} \sum_{v \in V[G]} d(v) \f]

        It can be found in Diestel 2017, p. 5
        """
        return sum([len(self.gdata[nid]) for nid in self.V]) / len(self.V)

    def edge_vertex_ratio(self) -> float:
        """!
        \brief obtain edge vertex ratio of graph instance
        Corresponds to \f[\epsilon(G)\f]. 
        The formula comes from Diestel 2017, p. 5.
        """
        return len(self.E) / len(self.V)

    def ev_ratio_from_average_degree(self, average_degree: float):
        """!
        \brief obtain edge vertex ratio from average degree

        Applies the following formula:
        \f[ |E[G]| = \frac{1}{2} \sum_{v \in V[G]} d(v) = 1/2 * d(G) * |V[G]|
        \f]
        It comes from Diestel 2017, p. 5
        """
        return average_degree / 2

    def ev_ratio(self):
        """!
        \brief shorthand for ev_ratio_from_average_degree()
        """
        return self.ev_ratio_from_average_degree(self.average_degree())

    def has_cycles(self) -> bool:
        """!
        \brief Check if graph instance contains cycles.
        This interpretation is from Diestel 2017, p. 8. The
        proof is provided in the given page.
        """
        md = self.min_degree()
        if md >= 2:
            return True
        return False

    def shortest_path_length(self) -> int:
        """!
        \brief Give the shortest possible path length for graph instance
        
        This interpretation is taken from Diestel 2017, p. 8. The proof
        is also given in the corresponding page.
        """
        return self.min_degree()

    def shortest_cycle_length(self) -> int:
        """!
        \brief Give the shortest possible cycle length for graph instance
        The interpretation comes from Diestel 2017, p. 8.
        """
        if self.has_cycles():
            return self.min_degree() + 1
        else:
            return 0
