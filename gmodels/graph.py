"""
general graph object
"""
from typing import Set, Optional, Callable, List, Tuple, Union
from graphobj import GraphObject
from edge import Edge
from node import Node
from info import NodeInfo, SNodeInfo
from uuid import uuid4
import math


class Graph(GraphObject):
    """!
    Simple graph
    """

    def __init__(
        self, gid: str, data={}, nodes: Set[Node] = None, edges: Set[Edge] = None
    ):
        ""
        super().__init__(oid=gid, odata=data)
        self._nodes: Optional[Set[Node]] = nodes
        self._edges: Optional[Set[Edge]] = edges
        if self._nodes is not None:
            self.is_empty = len(self._nodes) == 0
        else:
            self.is_empty = True

        if self.is_trivial():
            raise ValueError(
                "This library is not compatible with computations with trivial graph"
            )

    def __eq__(self, n):
        if isinstance(n, Graph):
            return self.id() == n.id()
        return False

    def __str__(self):
        ""
        return (
            self.id()
            + "--"
            + str([str(n) + "::" for n in self.nodes()])
            + "--"
            + str([str(n) + "!!" for n in self.edges()])
            + "--"
            + str(self.data())
        )

    def __hash__(self):
        return hash(self.__str__())

    @classmethod
    def merge_edges(cls, e1: Edge, e2: Edge) -> Edge:
        "merge two edges if they have the same id"
        e1id = e1.id()
        e2id = e2.id()
        if e1id() != e2id():
            msg = "Can not merge edges with different ids: "
            msg += "first edge id: " + e1id
            msg += "second edge id: " + e2id
            raise ValueError(msg)
        #
        e1data = e1.data()
        e2data = e2.data()
        e1data.update(e2data)
        e1info = e1.info()
        e2info = e2.info()
        #
        einfo = NodeInfo()
        einfo.set_to_null(e1info.first())
        einfo.set_to_null(e1info.second())
        einfo.set_to_null(e2info.first())
        einfo.set_to_null(e2info.second())
        return Edge(edge_id=e1id, edge_type=e1.type(), data=ei1data, node_info=einfo)

    @classmethod
    def from_nodes(cls, ns: Set[Node]):
        "construct a graph from vertex set"
        edges: List[Edge] = []
        for n in ns:
            info = n.info()
            for eid, etype in info.items():
                node_position = n.position_in(edge_id=eid)
                snode_info = SNodeInfo(node_id=n.id(), position=node_position)
                node_info = NodeInfo(first=snode_info)
                edges.append(Edge(edge_id=eid, edge_type=etype, node_info=node_info))
        edges.sort(key=lambda e: e.id())
        edge_s = set()
        for edge_index in range(0, len(edges) - 1, 2):
            e1 = edges[edge_index]
            e2 = edges[edge_index + 1]
            edge_s.add(cls.merge_edges(e1, e2))
        return Graph(gid=str(uuid4()), nodes=ns, edges=edge_s)

    def vertices(self) -> Set[Node]:
        if self._nodes is None:
            raise ValueError("Nodes are None for this graph")
        return self._nodes

    def nodes(self) -> Set[Node]:
        return self.vertices()

    def edges(self) -> Set[Edge]:
        if self._edges is None:
            raise ValueError("Edges are None for this graph")
        return self._edges

    def is_in(self, ne: Union[Node, Edge]) -> bool:
        ""
        aset = None
        if isinstance(ne, Node):
            aset = self.nodes()
        else:
            aset = self.edges()
        check = False
        for a in aset:
            if a.id() == ne.id():
                check = True
        return check

    def order(self) -> int:
        return len(self.nodes())

    def nb_edges(self) -> int:
        return len(self.edges())

    def is_trivial(self) -> bool:
        "check if graph is trivial"
        return self.order() < 2

    def vertex_by_id(self, node_id: str) -> Node:
        n = None
        for node in self.nodes():
            if node.id() == node_id:
                n = node
        return n

    def edge_by_id(self, edge_id: str) -> Edge:
        ""
        e = None
        for edge in self.edges():
            if edge.id() == edge_id:
                e = edge
        return e

    def edge_by_vertices(self, n1: Node, n2: Node) -> Edge:
        ""
        e = None
        for edge in self.edges():
            info = edge.info()
            fid = info.first().id()
            sid = info.second().id()
            n1id = n1.id() == fid or n1.id() == sid
            n2id = n2.id() == fid or n2.id() == sid
            if n1id and n2id:
                e = edge
        return e

    def vertices_of(self, e: Edge) -> Tuple[Node, Node]:
        ""
        info = e.info()
        first_node_id = info.first().id()
        second_node_id = info.second().id()
        first_node = self.vertex_by_id(first_node_id)
        second_node = self.vertex_by_id(second_node_id)
        return (first_node, second_node)

    def is_homomorphism(self, fn: Callable[[Node], Node]) -> bool:
        "Check if a function is a homomorphism"
        edges = self.edges()
        nodes = set()
        for n in self.nodes():
            nodes.add(fn(n))
        ngraph = Graph.from_nodes(nodes)

        for e in edges:
            vs = self.vertices_of(e)
            v1 = vs[0]
            v2 = vs[1]
            v1_ = fn(v1)
            v2_ = fn(v2)
            nedge = ngraph.edge_by_vertices(v1_, v2_)
            if nedge is None:
                return False
        return True

    def vertex_intersection(self, vs: Set[Node]) -> Set[Node]:
        ""
        return self.nodes().intersection(vs)

    def vertex_union(self, vs: Set[Node]) -> Set[Node]:
        ""
        return self.nodes().union(vs)

    def edge_intersection(self, es: Set[Edge]) -> Set[Edge]:
        ""
        return self.edges().intersection(es)

    def edge_union(self, es: Set[Edge]) -> Set[Edge]:
        ""
        return self.edges().union(es)

    def contains_edges(self, es: Set[Edge]) -> bool:
        "check if graph contains edges"
        return self.edges().intersection(es) == es

    def contains_vertices(self, vs: Set[Node]) -> bool:
        "check if graph contains edges"
        return self.nodes().intersection(vs) == vs

    def contains_graph(self, g) -> bool:
        "check if graph g is contained"
        return self.contains_vertices(g.nodes()) and self.contains_edges(g.edges())

    def graph_intersection(self, gs):
        ""
        ns: Set[Node] = gs.nodes()
        es: Set[Edge] = gs.edges()
        es_ = self.edge_intersection(es)
        ns_ = self.vertex_intersection(ns)
        return Graph(gid=str(uuid4()), nodes=ns_, edges=es_)

    def graph_union(self, gs):
        ""
        ns: Set[Node] = gs.nodes()
        es: Set[Edge] = gs.edges()
        es_ = self.edge_union(es)
        ns_ = self.vertex_union(ns)
        return Graph(gid=str(uuid4()), nodes=ns_, edges=es_)

    def _subtract_node(self, n: Node) -> Tuple[Set[Node], Set[Edge]]:
        "subtract a given node from graph"
        nodes = self.nodes()
        edges = self.edges()
        nnodes: Set[Node] = set()
        nedges: Set[Edge] = set()
        for node in nodes:
            if node != n:
                nnodes.add(node)
        for edge in edges:
            node_ids = edge.node_ids()
            n_id = n.id()
            if n_id not in node_ids:
                nedges.add(edge)
        return (nnodes, nedges)

    def subtract_node_from_self(self, n: Node):
        ""
        nodes, edges = self._subtract_node(n)
        self._nodes = nodes
        self._edges = edges

    def subtract_node(self, n: Node):
        ""
        nodes, edges = self._subtract_node(n)
        data = self.data()
        return Graph(gid=str(uuid4()), data=data, nodes=nodes, edges=edges)

    def subtract_nodes_from_self(self, ns: Set[Node]):
        ""
        for n in ns:
            self.subtract_node_from_self(n)

    def subtract_nodes(self, ns: Set[Node]):
        ""
        for n in ns:
            self = self.subtract_node(n)

    def _subtract_edge(self, e: Edge) -> Set[Edge]:
        "subtract a given node from graph"
        edges = self.edges()
        nedges: Set[Edge] = set()
        for edge in edges:
            if e != edge:
                nedges.add(edge)
        return nedges

    def subtract_edge_from_self(self, e: Edge):
        ""
        edges = self._subtract_edge(e)
        self._edges = edges

    def subtract_edge(self, e: Edge) -> GraphObject:
        ""
        edges = self._subtract_edge(e)
        return Graph(
            gid=str(uuid4()), data=self.data(), nodes=self.nodes(), edges=edges
        )

    def subtract_edges_from_self(self, es: Set[Edge]):
        ""
        for e in es:
            self.subtract_edge_from_self(e)

    def subtract_edges(self, es: Set[Edge]):
        ""
        for e in es:
            self = self.subtract_edge(e)

    def add_edge_to_self(self, e: Edge):
        ""
        edges = self.edges()
        edges.add(e)
        self._edges = edges

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

    def comp_degree(self, fn: Callable[[int, int], bool], comp_val: int):
        ""
        compare_v = comp_val
        for n in self.nodes():
            nb_edges = n.nb_edges()
            if fn(nb_edges, compare_v):
                compare_v = nb_edges
        return compare_v

    def max_degree(self) -> int:
        ""
        return self.comp_degree(
            fn=lambda nb_edges, compare: nb_edges > compare, comp_val=0
        )

    def min_degree(self) -> int:
        ""
        return int(
            self.comp_degree(
                fn=lambda nb_edges, compare: nb_edges < compare, comp_val=math.inf
            )
        )

    def average_degree(self) -> float:
        """!
        \f d(G) = \frac{1}{V[G]} \sum_{v \in V[G]} d(v) \f
        """
        coeff = 1 / len(self.nodes())
        deg_sum = sum([n.nb_edges() for n in self.nodes()])
        return coeff * deg_sum

    def edge_vertex_ratio(self) -> float:
        ""
        return len(self.edges()) / len(self.nodes())

    def ev_ratio_from_average_degree(self, average_degree: float):
        """!
        \f |E[G]| = \frac{1}{2} \sum_{v \in V[G]} d(v) = 1/2 * d(G) * |V[G]| \f
        """
        return average_degree / 2
