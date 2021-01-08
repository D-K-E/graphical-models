"""
Undirected graph object
"""
from typing import Set, Optional, List, Tuple, Dict
from gmodels.edge import Edge
from gmodels.node import Node
from gmodels.path import Path, Cycle
from gmodels.tree import Tree
from gmodels.abstractobj import EdgeType
from gmodels.graph import Graph
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

    def find_shortest_paths(
        self, n1: Node
    ) -> Tuple[Dict[str, Dict[str, str]], Set[Node], Dict[str, int]]:
        """!
        Breadth first search
        Even and Guy Even 2012, p. 12
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
            for vnode in self.neighbours_of(unode):
                vid = vnode.id()
                if vid not in T:
                    T.add(vid)
                    l_vs[vid] = int(l_vs[u] + 1)
                    P[nid][u] = vid
                    Q.append(vid)
        #
        T = set([self.V[t] for t in T])
        return P, T, l_vs

    def check_for_path(self, n1: Node, n2: Node) -> bool:
        "check if there is a path between nodes"
        paths = self.find_shortest_path(n1)
        n1_vertices = paths[1]
        return n2 in n1_vertices

    def lower_bound_for_path_length(self) -> int:
        "see proof Diestel 2017, p. 8"
        return self.min_degree()

    def find_minimum_spanning_tree(self) -> Tree:
        """!
        Find minimum spanning tree as per Prim's algorithm
        Even and Guy Even 2012, p. 32
        """
        l_e = 1  # length of an edge
        l_vs = {}
        vs = []
        eps = {}

        for v in self.V:
            l_vs[v] = math.inf
            vs.append(v)
        #
        s = vs[0]
        l_vs[s] = 0
        eps[s] = set()
        TEMP = vs.copy()
        T: Set[Edge] = set()
        while TEMP:
            minv = None
            minl = math.inf
            for v in TEMP:
                if l_vs[v] < minl:
                    minl = l_vs[v]
                    minv = v
            TEMP = [v for v in TEMP if v != minv]
            if minv is None:
                raise ValueError(
                    "Min vertex is not found. Graph is probably not connected"
                )
            T = T.union(eps[minv])
            for unode in self.neighbours_of(self.V[minv]):
                u = unode.id()
                if u in TEMP and l_vs[u] > l_e:
                    l_vs[u] = l_e
                    e = self.edge_by_vertices(self.V[minv], unode)
                    eps[u] = set([e])
        return Tree.from_edgeset(eset=T)

    def find_articulation_points(self) -> Set[Node]:
        ""
        nb_component = self.nb_components()
        points: Set[Node] = set()
        for node in self.nodes():
            graph = self.subtract_node(n=node)
            if graph.nb_components() > nb_component:
                points.add(node)
        return points
