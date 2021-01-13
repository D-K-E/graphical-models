"""
Undirected graph object
"""
from typing import Set, Optional, List, Tuple, Dict
from gmodels.gtypes.edge import Edge
from gmodels.gtypes.node import Node
from gmodels.gtypes.path import Path, Cycle
from gmodels.gtypes.tree import Tree
from gmodels.gtypes.abstractobj import EdgeType
from gmodels.gtypes.graph import Graph
from uuid import uuid4
import math


class UndiGraph(Graph):
    """!
    Unidrected graph whose edges are of type Undirected
    """

    def __init__(
        self, gid: str, data={}, nodes: Set[Node] = None, edges: Set[Edge] = None
    ):
        ""
        if edges is not None:
            for edge in edges:
                if edge.type() == EdgeType.DIRECTED:
                    raise ValueError(
                        "Can not instantiate undirected graph with" + " directed edges"
                    )
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges)

    @classmethod
    def from_graph(cls, g: Graph):
        ""
        return UndiGraph(
            gid=str(uuid4()), data=g.data(), nodes=g.nodes(), edges=g.edges()
        )

    def find_shortest_paths(
        self, n1: Node
    ) -> Tuple[Dict[str, Dict[str, str]], Set[Node], Dict[str, int]]:
        """!
        Breadth first search
        Even and Guy Even 2012, p. 12
        """
        return super().find_shortest_paths(n1=n1, edge_generator=self.edges_of)

    def check_for_path(self, n1: Node, n2: Node) -> bool:
        "check if there is a path between nodes"
        paths = self.find_shortest_path(n1)
        n1_vertices = paths[1]
        return n2 in n1_vertices

    def lower_bound_for_path_length(self) -> int:
        "see proof Diestel 2017, p. 8"
        return self.min_degree()

    def find_minimum_spanning_tree(self, weight_fn=lambda x: 1):
        """!
        """
        # t = Tree.find_mst_prim(self, edge_generator=self.edges_of)
        t, L = Tree.find_mnmx_st(
            self, edge_generator=self.edges_of, weight_function=weight_fn
        )
        return t, L

    def find_maximum_spanning_tree(self, weight_fn=lambda x: 1):
        """!
        """
        # t = Tree.find_mst_prim(self, edge_generator=self.edges_of)
        t, L = Tree.find_mnmx_st(
            self, edge_generator=self.edges_of, weight_function=weight_fn, is_min=False
        )
        return t, L

    def find_articulation_points(self) -> Set[Node]:
        """!
        """
        gmaker = lambda x: self.from_graph(self.subtract_node(x))
        return super().find_articulation_points(graph_maker=gmaker)

    def find_bridges(self) -> Set[Node]:
        """!
        """
        gmaker = lambda x: self.from_graph(self.subtract(x))
        return super().find_bridges(graph_maker=gmaker)
