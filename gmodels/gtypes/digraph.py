"""!
Directed graph
"""
from typing import Set, Optional, List, Tuple, Dict
from gmodels.gtypes.edge import Edge
from gmodels.gtypes.node import Node
from gmodels.gtypes.path import Path, Cycle
from gmodels.gtypes.tree import Tree
from gmodels.gtypes.abstractobj import EdgeType
from gmodels.gtypes.graph import Graph
from gmodels.gtypes.undigraph import UndiGraph
from uuid import uuid4
import math


class DiGraph(Graph):
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
        self.path_props = {v.id(): self.find_shortest_paths(v) for v in self.nodes()}
        self.dprops = self.visit_graph_dfs(
            edge_generator=self.outgoing_edges_of, check_cycle=True
        )

    @classmethod
    def from_graph(cls, g: Graph):
        ""
        return DiGraph(
            gid=str(uuid4()), data=g.data(), nodes=g.nodes(), edges=g.edges()
        )

    def is_family_of(self, src: Node, dst: Node) -> bool:
        """!
        Check if src is family of dst
        """
        for e in self.edges():
            # dst is child of src
            child_cond = e.start() == src and e.end() == dst
            # dst is parent of src
            parent_cond = e.start() == dst and e.end() == src
            if child_cond or parent_cond:
                return True
        return False

    def is_parent_of(self, parent: Node, child: Node) -> bool:
        def cond(n_1: Node, n_2: Node, e: Edge):
            ""
            c = n_1 == e.start() and e.end() == n_2
            return c

        return self.is_related_to(n1=parent, n2=child, condition=cond)

    def is_child_of(self, child: Node, parent: Node) -> bool:
        ""
        return self.is_parent_of(parent=parent, child=child)

    def edge_by_vertices(self, n1: Node, n2: Node) -> Set[Edge]:
        """!
        """
        if not self.is_in(n1) or not self.is_in(n2):
            raise ValueError("argument nodes are not in graph")
        #
        eset: Set[Edge] = set()
        for e in self.edges():
            if e.start().id() == n1.id() and e.end().id() == n2.id():
                eset.add(e)
        return eset

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
        for e in self.edges():
            if e.start().id() == n.id():
                children.add(e.end())
        return children

    def parents_of(self, n: Node) -> Set[Node]:
        """!
        """
        if not self.is_in(n):
            raise ValueError("node not in graph")

        parents: Set[Node] = set()
        for e in self.edges():
            if e.end().id() == n.id():
                parents.add(e.start())
        return parents

    def to_undirected(self) -> UndiGraph:
        """!
        to undirected graph
        """
        nodes = self.nodes()
        edges = self.edges()
        nedges = set()
        nnodes = set([n for n in nodes])
        for e in edges:
            e.set_type(etype=EdgeType.UNDIRECTED)
            nedges.add(e)
        return UndiGraph(gid=str(uuid4()), data=self.data(), nodes=nnodes, edges=nedges)

    def in_degree_of(self, n: Node) -> int:
        return len(self.parents_of(n))

    def out_degree_of(self, n: Node) -> int:
        return len(self.children_of(n))

    def find_shortest_paths(self, n: Node):
        """!
        """
        return super().find_shortest_paths(n1=n, edge_generator=self.outgoing_edges_of)

    def check_for_path(self, n1: Node, n2: Node) -> bool:
        "check if there is a path between nodes"
        path_props = self.path_props[n1.id()]
        pset = path_props["path-set"]
        return n2 in pset

    def find_transitive_closure(self) -> Graph:
        """!
        From algorithmic graph theory Joyner, Phillips, Nguyen, 2013, p.134
        """
        T = self.transitive_closure_matrix()
        nodes = set()
        edges = set()
        for tpl, tval in T.items():
            if tval is False:
                n1 = self.V[tpl[0]]
                n2 = self.V[tpl[1]]
                nodes.add(n1)
                nodes.add(n2)
                e = Edge(
                    edge_id=str(uuid4()),
                    start_node=n1,
                    end_node=n2,
                    edge_type=EdgeType.DIRECTED,
                )
                edges.add(e)

        return DiGraph(gid=str(uuid4()), nodes=nodes, edges=edges)
