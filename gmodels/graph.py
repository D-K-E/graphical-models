"""
graph object
"""
from typing import Set, Optional, Callable, List, Tuple
from graphobj import GraphObject
from edge import Edge
from node import Node
from info import NodeInfo, SNodeInfo
from uuid import uuid4


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
        # TODO bunu da bitir
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
        # TODO buradasin
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

    def order(self) -> int:
        return len(self.nodes())

    def nb_edges(self) -> int:
        return len(self.edges())

    def is_trivial(self) -> bool:
        "check if graph is trivial"
        return self.order() < 2

    def is_node_incident(self, n: Node, e: Edge) -> bool:
        ""
        einfo = e.edge_info()
        return n.is_incident(info=einfo)

    def is_neighbour_of(self, n1: Node, n2: Node) -> bool:
        ""
        n1_edge_ids = n1.edge_ids()
        n2_edge_ids = n2.edge_ids()
        return len(n1_edge_ids.intersection(n2_edge_ids)) > 0

    def is_adjacent_of(self, e1: Edge, e2: Edge) -> bool:
        ""
        n1_ids = e1.node_ids()
        n2_ids = e2.node_ids()
        return len(n1_ids.intersection(n2_ids)) > 0

    def is_node_independant_of(self, n1: Node, n2: Node) -> bool:
        return not self.is_neighbour_of(n1, n2)

    def is_stable(self, ns: Set[Node]) -> bool:
        ""
        node_list = list(ns)
        while node_list:
            n1 = node_list.pop()
            for n2 in node_list:
                if self.is_neighbour_of(n1=n1, n2=n2):
                    return False
        return True

    def neighbours_of(self, n1: Node) -> Set[Node]:
        ""
        neighbours = set()
        for n2 in self.nodes():
            if self.is_neighbour_of(n1=n1, n2=n2):
                neighbours.add(n2)
        return neighbours

    def edges_of(self, n: Node) -> Set[Edge]:
        ""
        edge_ids = n.edge_ids()
        edges = set()
        for edge in self.edges():
            if edge.id() in edge_ids:
                edges.add(edge)
        return edges

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

    def is_disjoint(self, g):
        ""
        ns: Set[Node] = g.nodes()
        ns_ = self.vertex_intersection(ns)
        return len(ns_) == 0
