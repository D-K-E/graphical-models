"""!
\file graph.py

\defgroup graphgroup Graph and Related Objects

Contains a general graph object. Most of the functionality is based on 
Diestel 2017.

"""
from typing import Set, Optional, Callable, List, Tuple, Union, Dict, FrozenSet
from gmodels.gtypes.graphobj import GraphObject
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.gtypes.node import Node
from uuid import uuid4
import math


class Graph(GraphObject):
    """!
    Simple finite graph
    \f[ G = (V, E) \f] where \f[ V \f] is the vertex set and \f[ E \f] is the edge set.
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

        We construct the graph from given node and edge set. For quick look up
        we store them in hash tables. The gdata member also stores an edge list
        representation, in order to facilitate some of the basic look up
        functionality concerning neighbours of vertices.
        """
        super().__init__(oid=gid, odata=data)
        self._nodes: Optional[Dict[str, Node]] = None
        if nodes is not None:
            self._nodes = {n.id(): n for n in nodes}
        self._edges: Optional[Dict[str, Edge]] = None
        if edges is not None:
            self._edges = {e.id(): e for e in edges}
        #
        self.gdata: Dict[str, List[str]] = {}
        if self._nodes is not None:
            self.is_empty = len(self._nodes) == 0
        else:
            self.is_empty = True

        if self.is_trivial():
            msg = "This library is not compatible with computations with trivial graph"
            msg += "\nNodes: "
            msg += str(self._nodes.keys())
            msg += "\nEdges: " + str(self._edges.keys())
            raise ValueError(msg)
        #
        self.mk_nodes(ns=nodes, es=edges)
        self.mk_gdata()
        self.props = self.visit_graph_dfs(
            edge_generator=self.edges_of, check_cycle=True
        )

    @classmethod
    def from_edgeset(cls, edges: Set[Edge]):
        """!
        \brief We construct the graph from given edge set using a random id.

        See \see Graph for more information
        """
        nodes: Set[Node] = set()
        for e in edges:
            nodes.add(e.start())
            nodes.add(e.end())
        return Graph(gid=str(uuid4()), nodes=nodes, edges=edges)

    @classmethod
    def from_edge_node_set(cls, edges: Set[Edge], nodes: Set[Node]):
        """!
        \brief We construct the graph from given node, and edge sets using a random id.
        \see Graph for more information
        """
        nodes = set(nodes)
        for e in edges:
            nodes.add(e.start())
            nodes.add(e.end())
        return Graph(gid=str(uuid4()), nodes=nodes, edges=edges)

    def mk_nodes(self, ns: Optional[Set[Node]], es: Optional[Set[Edge]]):
        """!
        \brief Obtain all nodes in a single set.

        \param ns set of nodes
        \param es set of edges

        We assume that node set and edge set might contain different nodes,
        that is \f[ V[G] = V[ns] \cup V[es] \f]
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

    def to_adjmat(self, vtype=int):
        """!
        \brief Transform adjacency list to adjacency matrix representation
        """
        gmat = {}
        for v in self.V:
            for k in self.V:
                common = set(self.gdata[v]).intersection(set(self.gdata[k]))
                gmat[(v, k)] = vtype(0)
        for edge in self.edges():
            tpl1 = (edge.start().id(), edge.end().id())
            tpl2 = (edge.end().id(), edge.start().id())
            if tpl1 in gmat:
                gmat[tpl1] = vtype(1)
            if edge.type() == EdgeType.UNDIRECTED:
                if tpl2 in gmat:
                    gmat[tpl2] = vtype(1)
        return gmat

    def has_self_loop(self) -> bool:
        """!
        \brief Check if graph has a self loop.
        We check whether the incident vertices of an edge is same.
        """
        for edge in self.edges():
            if edge.start() == edge.end():
                return True
        return False

    def transitive_closure_matrix(self) -> Dict[Tuple[str, str], bool]:
        """!
        \brief Obtain transitive closure matrix of a given graph

        We apply the algorithm from algorithmic graph theory Joyner, Phillips,
        Nguyen, 2013, p.134
        """
        if self.has_self_loop():
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

    def __eq__(self, n):
        """!
        \brief Check for equality

        This is not a strict check for equality of graphs. We simply check
        for ids. There is nothing mathematical about it. Should not be
        used in the context of graph algebra.
        """
        if isinstance(n, Graph):
            return self.id() == n.id()
        return False

    def __str__(self):
        """!
        \brief Obtain string representation of the graph.
        """
        return (
            self.id()
            + "--"
            + "::".join([str(n) for n in self._nodes])
            + "--"
            + "!!".join([str(n) for n in self._edges])
            + "--"
            + "::".join([str(k) + "-" + str(v) for k, v in self.data().items()])
        )

    def __hash__(self):
        """!
        \brief Create a hash value for the graph.

        Since the identifiers of graphs are randomly generated in most cases,
        hashing them by their string representation should not create a
        problem, because the string representation contains the identifier
        of the graph.
        """
        return hash(self.__str__())

    @property
    def V(self) -> Dict[str, Node]:
        """!
        \brief Obtain vertices of the graph

        \throws ValueError if node set is empty for the graph
        """
        if self._nodes is None:
            raise ValueError("Nodes are None for this graph")
        return self._nodes

    @property
    def E(self) -> Dict[str, Edge]:
        """!
        \brief obtain edges of the graph
        \throws ValueError if edge set is empty for the graph.
        """
        if self._edges is None:
            raise ValueError("Edges are None for this graph")
        return self._edges

    def is_connected(self) -> bool:
        """!
        \brief Check if graph is connected
        If a graph has a single component, then we assume that it is connected
        graph
        """
        return self.nb_components() == 1

    def is_adjacent_of(self, e1: Edge, e2: Edge) -> bool:
        """!
        \brief Check if two edges are adjacent
        """
        n1_ids = e1.node_ids()
        n2_ids = e2.node_ids()
        return len(n1_ids.intersection(n2_ids)) > 0

    def is_node_incident(self, n: Node, e: Edge) -> bool:
        """!
        \brief Check if a node is incident of an edge

        \param n node We check if this node is an endvertex of the edge.
        \param e The queried edge.
        """
        return e.is_endvertice(n)

    def is_related_to(
        self,
        n1: Node,
        n2: Node,
        condition: Callable[[Node, Node, Edge], bool],
        es: Set[Edge] = None,
    ):
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
            es = self.edges()
        for e in es:
            if condition(n1, n2, e) is True:
                return True
        return False

    def is_neighbour_of(self, n1: Node, n2: Node) -> bool:
        """!
        \brief check if two nodes are neighbours
        We define the condition of neighborhood as having a common edge.
        """

        def cond(n_1: Node, n_2: Node, e: Edge) -> bool:
            """!
            \brief neighborhood condition
            """
            estart = e.start()
            eend = e.end()
            c1 = estart == n_1 and eend == n_2
            c2 = estart == n_2 and eend == n_1
            return c1 or c2

        n1_edge_ids = set(self.gdata[n1.id()])
        n2_edge_ids = set(self.gdata[n2.id()])
        edge_ids = n1_edge_ids.intersection(n2_edge_ids)
        # filter self loops
        edges = set([self.E[e] for e in edge_ids])
        return self.is_related_to(n1=n1, n2=n2, condition=cond, es=edges)

    def is_node_independent_of(self, n1: Node, n2: Node) -> bool:
        """!
        \brief check if two nodes are independent
        We consider two nodes independent if they are not the same, and they
        are not neighbours.
        """
        if n1 == n2:
            return False
        return True if self.is_neighbour_of(n1, n2) is False else False

    def is_stable(self, ns: Set[Node]) -> bool:
        """!
        \brief check if given node set is stable

        We ensure that no nodes in the given node set is a neighbour of one
        another as per the definition of Diestel 2017, p. 3.

        \throws ValueError if argument node set is not a subset of vertices of
        the graph
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
        \throws ValueError if node is not inside the graph
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
        """
        return len(self.neighbours_of(n))

    def edges_of(self, n: Node) -> Set[Edge]:
        """!
        \brief obtain the edge set of a given node.
        """
        edge_ids = self.gdata[n.id()]
        return set([self.E[eid] for eid in edge_ids])

    def outgoing_edges_of(self, n: Node) -> Set[Edge]:
        """!
        \brief obtain the outgoing edge set of a given node.

        Outgoing edge set means all edges that start with the given node
        and end in another node. This information is mostly trivial for 
        undirected graphs but becomes important for distinguishing 
        parents from children in directed graphs.
        """
        return set([e for e in self.edges() if e.start() == n])

    def incoming_edges_of(self, n: Node) -> Set[Edge]:
        """!
        \brief obtain incoming edges of a given graph

        Incoming edges are defined as edges that end with the given node.
        We only check for the position and do not consider the type of the edge
        For its use case see \see outgoing_edges_of()
        """
        return set([e for e in self.edges() if e.end() == n])

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
        """
        return set([self.E[e] for e in self.E if self.E[e].is_end(n)])

    def vertices(self) -> Set[Node]:
        """!
        \brief obtain vertex set of the given graph
        """
        return set([n for n in self.V.values()])

    def nodes(self) -> Set[Node]:
        """!
        \brief obtain vertex set of the graph
        """
        return self.vertices()

    def edges(self) -> Set[Edge]:
        """!
        \brief obtain edge set of the graph
        """
        return set([n for n in self.E.values()])

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

    def order(self) -> int:
        """!
        \brief obtain the number of vertices in the graph.

        It corresponds to \f[ |G| \f].
        This interpretation of order is taken from Diestel 2017, p. 2.
        """
        return len(self.V)

    def nb_edges(self) -> int:
        """!
        \brief obtain number of edges in the graph
        It corresponds to \f[ ||G|| \f].
        This interpretation is taken from Diestel 2017, p. 2.
        """
        return len(self.E)

    def is_trivial(self) -> bool:
        """!
        \brief check if graph is trivial.
        This triviality condition is taken from
        Diestel 2017, p. 2
        """
        return self.order() < 2

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

    def edge_by_vertices(self, n1: Node, n2: Node) -> Set[Edge]:
        """!
        \brief obtain edge set by using its vertices.

        We take all edges that consist of given two nodes

        \throws ValueError if any of argument nodes are not inside the graph.
        \throws ValueError if there are no edges that consist of argument nodes.
        """
        if not self.is_in(n1) or not self.is_in(n2):
            raise ValueError("one of the nodes is not present in graph")
        n1id = n1.id()
        n2id = n2.id()
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

    def set_op(
        self,
        obj: Union[Set[Node], Set[Edge], GraphObject],
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
        if isinstance(obj, set):
            lst = list(obj)
            if isinstance(lst[0], Node):
                return op(self.nodes())
            else:
                return op(self.edges())
        elif not isinstance(obj, Graph):
            raise TypeError("object should be either node/edge set or graph")
        return None

    def intersection(
        self, aset: Union[Set[Node], Set[Edge], GraphObject]
    ) -> Union[Set[Node], Set[Edge], GraphObject]:
        """!
        \brief obtain intersection of either node or edge set
        """
        v = self.set_op(obj=aset, op=lambda x: x.intersection(aset))
        if v is None:
            return self.graph_intersection(aset)
        return v

    def union(
        self, aset: Union[Set[Node], Set[Edge], GraphObject]
    ) -> Union[Set[Node], Set[Edge], GraphObject]:
        """!
        \brief obtain union of either node or edge set
        """
        v = self.set_op(obj=aset, op=lambda x: x.union(aset))
        if v is None:
            return self.graph_union(aset)
        return v

    def difference(
        self, aset: Union[Set[Node], Set[Edge], GraphObject]
    ) -> Union[Set[Node], Set[Edge], GraphObject]:
        """!
        \brief obtain set difference of either node or edge set
        """
        v = self.set_op(obj=aset, op=lambda x: x.difference(aset))
        if v is None:
            return self.graph_difference(aset)
        return v

    def symmetric_difference(
        self, aset: Union[Set[Node], Set[Edge], GraphObject]
    ) -> Union[Set[Node], Set[Edge], GraphObject]:
        """!
        \brief obtain symmetric set difference of either node or edge set.
        """
        v = self.set_op(obj=aset, op=lambda x: x.symmetric_difference(aset))
        if v is None:
            return self.graph_symmetric_difference(aset)
        return v

    def contains(self, a: Union[Set[Edge], Set[Node], GraphObject]) -> bool:
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
        return Graph(gid=str(uuid4()), nodes=ns_, edges=es_)

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
        return Graph(gid=str(uuid4()), nodes=ns_, edges=es_)

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
        return Graph(gid=str(uuid4()), nodes=ns_, edges=ess)

    def graph_symmetric_difference(self, gs):
        """!
        \brief symmetric set difference operation adapted for graph.
        """
        ns: Set[Node] = gs.nodes()
        es: Set[Edge] = gs.edges()
        es_ = self.symmetric_difference(es)
        ns_ = self.symmetric_difference(ns)
        return Graph(gid=str(uuid4()), nodes=ns_, edges=es_)

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
        return Graph(gid=str(uuid4()), data=data, nodes=nodes, edges=edges)

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

    def subtract_edge(self, e: Edge) -> GraphObject:
        """!
        \brief create a new graph by subtracting edge from edge set of graph instance
        \see subtract_node() as well
        """
        edges = self._subtract_edge(e)
        return Graph(
            gid=str(uuid4()), data=self.data(), nodes=self.nodes(), edges=edges
        )

    def subtract_edge_with_nodes(self, e) -> GraphObject:
        """!
        \brief subtract edge and remove its nodes as well.
        """
        edges = self._subtract_edge(e)
        enode1, enode2 = e.start(), e.end()
        nodes = self.nodes()
        nodes = nodes.difference(set([enode1, enode2]))
        return Graph(gid=str(uuid4()), nodes=nodes, edges=edges)

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
        edges = self.edges()
        edges.add(e)
        self._edges = {e.id(): e for e in edges}

    def add_edge(self, e: Edge):
        ""
        edges = self.edges()
        edges.add(e)
        return Graph(
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

    def visit_graph_dfs(
        self, edge_generator: Callable[[Node], Set[Node]], check_cycle: bool = False,
    ):
        """!
        \brief interior visit function for depth first enumeration of graph
        instance.

        \see dfs_forest() method for more information on parameters.
        """
        time = 0
        marked: Dict[str, bool] = {n: False for n in self.V}
        preds: Dict[str, Dict[str, str]] = {}
        Ts: Dict[str, Set[str]] = {}
        d: Dict[str, int] = {n: math.inf for n in self.V}
        f: Dict[str, int] = {n: math.inf for n in self.V}
        cycles: Dict[str, List[Dict[str, Union[str, int]]]] = {n: [] for n in self.V}
        component_counter = 0
        #
        for u in self.V:
            if marked[u] is False:
                pred: Dict[str, Optional[str]] = {n: None for n in self.V}
                T: Set[str] = set()
                self.dfs_forest(
                    u=u,
                    pred=pred,
                    cycles=cycles,
                    marked=marked,
                    d=d,
                    T=T,
                    f=f,
                    time=time,
                    check_cycle=check_cycle,
                    edge_generator=edge_generator,
                )
                component_counter += 1
                for child, parent in pred.copy().items():
                    if child != u and child is None:
                        pred.pop(child)
                Ts[u] = T
                preds[u] = pred
        #
        res = {
            "dfs-forest": self.from_preds_to_edgeset(preds),
            "first-visit-times": d,
            "last-visit-times": f,
            "components": Ts,
            "cycle-info": cycles,
            "nb-component": component_counter,
        }
        return res

    def from_preds_to_edgeset(
        self, preds: Dict[str, Dict[str, str]]
    ) -> Dict[str, Set[Edge]]:
        """!
        \brief obtain the edge set implied by the predecessor array.
        """
        esets: Dict[str, Set[Edge]] = {}
        for u, forest in preds.copy().items():
            eset: Set[Edge] = set()
            for child, parent in forest.items():
                cnode = self.V[child]
                if parent is not None:
                    pnode = self.V[parent]
                    eset = eset.union(self.edge_by_vertices(n1=pnode, n2=cnode))
            esets[u] = eset
        return esets

    def dfs_forest(
        self,
        u: str,
        pred: Dict[str, str],
        marked: Dict[str, int],
        d: Dict[str, int],
        f: Dict[str, int],
        T: Set[str],
        cycles: Dict[str, List[Dict[str, Union[str, int]]]],
        time: int,
        edge_generator: Callable[[Node], Set[Edge]],
        check_cycle: bool = False,
    ) -> Optional[Tuple[str, str]]:
        """!
        adapted for cycle detection
        dfs recursive forest from Erciyes 2018, Guide Graph ..., p.152 alg. 6.7

        \param f storing last visit times per node
        \param d storing first visit times per node
        \param cycles storing cycle info
        \param marked storing if node is visited
        \param pred storing the parent of nodes
        \param g graph we are searching for
        \param u node id
        \param T set of pred nodes
        \param time global visit counter
        \param check_cycle fill cycles if it is detected
        \param edge_generator generate edges of a vertex with respect to graph type
        """
        marked[u] = True
        time += 1
        d[u] = time
        unode = self.V[u]
        for edge in edge_generator(unode):
            vnode = edge.get_other(unode)
            v = vnode.id()
            if marked[v] is False:
                pred[v] = u
                T.add(v)
                self.dfs_forest(
                    u=v,
                    pred=pred,
                    marked=marked,
                    d=d,
                    f=f,
                    T=T,
                    cycles=cycles,
                    time=time,
                    check_cycle=check_cycle,
                    edge_generator=edge_generator,
                )
        #
        time += 1
        f[u] = time
        if check_cycle:
            # v ancestor, u visiting node
            # edge between them is a back edge
            # see p. 151, and p. 159-160
            unode = self.V[u]
            for edge in edge_generator(unode):
                vnode = edge.get_other(unode)
                vid = vnode.id()
                if pred[u] != vid:
                    first_visit = d.get(vid)
                    last_visit = f.get(vid)
                    cond = d[vid] < f[u]
                    if cond:
                        cycle_info = {
                            "ancestor": vid,
                            "before": u,
                            "ancestor-first-time-visit": d[vid],
                            "current-final-time-visit": f[u],
                        }
                        cycles[u].append(cycle_info)
        #
        return None

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

    def find_shortest_paths(
        self, n1: Node, edge_generator: Callable[[Node], Set[Edge]]
    ) -> Dict[str, Union[dict, set]]:
        """!
        \brief find shortest path from given node to all other nodes

        Applies the Breadth first search algorithm from Even and Guy Even 2012, p. 12

        \throws ValueError if given node is not found in graph instance
        """
        if not self.is_in(n1):
            raise ValueError("argument node is not in graph")
        nid = n1.id()
        Q = [nid]
        l_vs = {v: math.inf for v in self.V}
        l_vs[nid] = 0
        T = set([nid])
        P: Dict[str, Dict[str, str]] = {}
        P[nid] = {}
        while Q:
            u = Q.pop(0)
            unode = self.V[u]
            for edge in edge_generator(unode):
                vnode = edge.get_other(unode)
                vid = vnode.id()
                if vid not in T:
                    T.add(vid)
                    l_vs[vid] = int(l_vs[u] + 1)
                    P[nid][u] = vid
                    Q.append(vid)
        #
        T = set([self.V[t] for t in T])
        path_props = {"bfs-tree": P, "path-set": T, "top-sort": l_vs}
        return path_props

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
        for node in self.nodes():
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
        for edge in self.edges():
            graph = self.subtract(edge)
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
        for e in self.edges():
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
        if isinstance(a, Node):
            nodes = self.union(set([a]))
            return Graph(gid=str(uuid4()), data={}, nodes=nodes, edges=self.edges())
        elif isinstance(a, Edge):
            es = self.union(set([a]))
            return Graph(gid=str(uuid4()), data={}, nodes=self.nodes(), edges=es)
        else:
            return self.union(a)

    def __sub__(
        self, a: Union[Set[Edge], Set[Node], Node, Edge, GraphObject]
    ) -> GraphObject:
        """!
        \brief overloads - sign for doing algebraic operations with graph
        objects.
        """
        if isinstance(a, Node):
            nodes = self.difference(set([a]))
            return Graph(gid=str(uuid4()), data={}, nodes=nodes, edges=self.edges())
        elif isinstance(a, Edge):
            es = self.difference(set([a]))
            return Graph(gid=str(uuid4()), data={}, nodes=self.nodes(), edges=es)
        else:
            return self.difference(a)
