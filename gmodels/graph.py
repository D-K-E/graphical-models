"""
graph object
"""
from typing import Set, Optional, Callable, List
from graphobj import GraphObject
from edge import Edge
from node import Node


class Graph(GraphObject):
    "Simple graph"

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

    @classmethod
    def from_nodes(cls, ns: Set[Node]):
        "construct a graph from vertex set"
        edges: List[Edge] = []
        for n in ns:
            info = n.info()
            for eid, etype in info.items():
                node_position = n.position_in(edge_id=eid)
                edges.append(Edge(edge_id=eid, edge_type=etype))

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

    def is_homomorphism(self, fn: Callable[Set[Node], Set[Node]]):
        "Check if a function is a homomorphism"
        new_nodes = fn(self.nodes())
