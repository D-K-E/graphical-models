"""!
Directed graph
"""
from typing import Set, Optional, List, Tuple, Dict
from edge import Edge
from node import Node
from path import Path, Cycle
from abstractobj import EdgeType
from graph import Graph
from uuid import uuid4
import math


class DirectedGraph(Graph):
    """!
    Directed graph implementation
    """

    def __init__(
        self, gid: str, data={}, nodes: Set[Node] = None, edges: Set[Edge] = None
    ):
        ""

    if edges is not None:
        for edge in edges:
            if edge.type() == EdgeType.UNDIRECTED:
                raise ValueError(
                    "Can not instantiate directed graph with" + " undirected edges"
                )
    super().__init__(gid=gid, data=data, nodes=nodes, edges=edges)

    def is_family_of(self, src: Node, dst: Node, is_parent: bool = True) -> bool:
        """!
        Check if src is family of dst
        """
        edge = self.edge_by_vertices(src, dst)
        if is_parent:
            if edge.start() == src:
                return True
            return False
        else:
            if edge.end() == src:
                return True
            return False

    def is_parent_of(self, parent: Node, child: Node) -> bool:
        return self.is_family_of(src=parent, dst=child, is_parent=True)

    def is_child_of(self, child: Node, parent: Node) -> bool:
        return self.is_family_of(src=child, dst=parent, is_parent=False)

    def is_adjacent_of(self, e1: Edge, e2: Edge) -> bool:
        ""
        n1_ids = e1.node_ids()
        n2_ids = e2.node_ids()
        return len(n1_ids.intersection(n2_ids)) > 0

    def children_of(self, n: Node) -> Set[Node]:
        """!
        """
        if not self.is_in(n):
            raise ValueError("node not in graph")

        children: Set[Node] = set()
        for node in self.nodes():
            if self.is_child_of(node, n):
                children.add(node)
        return children

    def parents_of(self, n: Node) -> Set[Node]:
        """!
        """
        if not self.is_in(n):
            raise ValueError("node not in graph")

        parents: Set[Node] = set()
        for node in self.nodes():
            if self.is_parent_of(node, n):
                parents.add(node)
        return parents

    def in_degree_of(self, n: Node) -> int:
        return len(self.parents_of(n))

    def out_degree_of(self, n: Node) -> int:
        return len(self.children_of(n))

    def has_self_loop(self) -> bool:
        ""
        for edge in self.edges():
            if edge.start() == edge.end():
                return True
        return False

    def find_shortest_path(self, n1: Node, n2: Node) -> Optional[Path]:
        ""
        try:
            return Path.from_graph_nodes(
                self, n1=n1, n2=n2, generative_fn=self.children_of
            )
        except ValueError:
            return None

    def check_for_path(self, n1: Node, n2: Node) -> bool:
        "check if there is a path between nodes"
        return self.find_shortest_path(n1, n2) is not None
