"""!
Path in a given graph
"""

from typing import Set, Optional, Callable, List, Tuple, Dict, Union
from gmodels.edge import Edge, EdgeType
from gmodels.node import Node
from gmodels.graph import Graph
from uuid import uuid4
import math


class Tree(Graph):
    """!
    Tree object
    """

    def __init__(self, gid: str, data={}, edges: Set[Edge] = None):
        ""
        nodes = None
        if edges is not None:
            nodes = set()
            for e in edges:
                estart = e.start()
                eend = e.end()
                nodes.add(estart)
                nodes.add(eend)
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges)
        self.root = self._root()

    @classmethod
    def from_node_tuples(cls, ntpls: Set[Tuple[Node, Node, EdgeType]]):
        ""
        edges: Set[Edge] = set()
        root = None

        for e in ntpls:
            child = e[0]
            parent = e[1]
            edge = Edge(
                edge_id=str(uuid4()), start_node=parent, end_node=child, edge_type=e[2]
            )
            edges.add(edge)
        return Tree(gid=str(uuid4()), edges=edges)

    @classmethod
    def from_edgeset(cls, eset: Set[Edge]):
        ""
        return Tree(gid=str(uuid4()), edges=eset)

    def node_table(self):
        ""
        node_table = {v: {"child": False, "parent": False} for v in self.V}
        for e in self.edges():
            estart_id = e.start().id()
            eend_id = e.end().id()
            node_table[estart_id]["parent"] = True
            node_table[eend_id]["child"] = True
        #
        return node_table

    def _root(self):
        ""
        node_table = self.node_table()
        root_ids = [
            k
            for k, v in node_table.items()
            if v["child"] is False and v["parent"] is True
        ]
        return self.V[root_ids[0]]

    def leaves(self) -> Set[Node]:
        ""
        node_table = self.node_table()
        #
        leave_ids = [
            k
            for k, v in node_table.items()
            if v["child"] is True and v["parent"] is False
        ]
        return set([self.V[v] for v in leave_ids])

    def root_node(self) -> Node:
        ""
        return self.root

    def upset_of(self, n: Node) -> Set[Node]:
        ""
        raise NotImplementedError

    def downset_of(self, n: Node) -> Set[Node]:
        ""
        raise NotImplementedError

    def less_than_or_equal(self, first: Node, second: Node) -> bool:
        ""
        raise NotImplementedError

    def greater_than_or_equal(self, first: Node, second: Node) -> bool:
        ""
        raise NotImplementedError

    #
    def assign_num(
        self,
        v: str,
        num: Dict[str, int],
        visited: Dict[str, bool],
        parent: Dict[str, str],
        counter: int,
        generative_fn: Callable[[Node], Set[Node]],
    ):
        ""
        counter += 1
        num[v] = counter
        visited[v] = True
        vnode = self.V[v]
        for unode in generative_fn(vnode):
            u = unode.id()
            cond = visited.get(u)
            if cond is None or cond is False:
                parent[u] = v
                self.assign_num(
                    u,
                    num=num,
                    generative_fn=generative_fn,
                    visited=visited,
                    parent=parent,
                    counter=counter,
                )

    #
    def check_ap(
        self,
        v: str,
        num: Dict[str, int],
        visited: Dict[str, bool],
        parent: Dict[str, str],
        low: Dict[str, int],
        counter: int,
        aset: Set[str],
        generative_fn: Callable[[Node], Set[Node]],
    ):
        ""
        low[v] = num[v]
        vnode = self.V[v]
        for unode in generative_fn(vnode):
            u = unode.id()
            if num[u] >= num[v]:
                self.check_ap(
                    v=u,
                    num=num,
                    visited=visited,
                    parent=parent,
                    low=low,
                    counter=counter,
                    generative_fn=generative_fn,
                    aset=aset,
                )
                if low[u] >= num[v]:
                    aset.add(v)
                #
                low[v] = min(low[v], low[u])
            elif parent[v] != u:
                low[v] = min(low[v], num[u])

    def find_separating_vertices(
        self, generative_fn: Callable[[Node], Set[Node]]
    ) -> Set[Node]:
        """!
        find separating vertices of graph
        as in Erciyes 2018, p. 230, algorithm 8.3
        """
        num: Dict[str, float] = {n: math.inf for n in self.V}
        low: Dict[str, float] = {n: math.inf for n in self.V}
        visited: Dict[str, bool] = {}
        parent: Dict[str, str] = {n: "" for n in self.V}
        aset: Set[str] = set()

        counter = 1
        v = [node for node in self.V][0]
        self.assign_num(
            v=v,
            num=num,
            visited=visited,
            parent=parent,
            counter=counter,
            generative_fn=generative_fn,
        )
        self.check_ap(
            v=v,
            num=num,
            visited=visited,
            generative_fn=generative_fn,
            parent=parent,
            low=low,
            counter=counter,
            aset=aset,
        )
        return set([self.V[a] for a in aset])
