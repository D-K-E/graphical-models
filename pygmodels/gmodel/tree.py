"""!
Path in a given graph
"""

import math
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pygmodels.gmodel.path import Path
from pygmodels.graphops.bgraphops import BaseGraphOps
from pygmodels.graphops.bgraphops import BaseGraphNodeOps
from pygmodels.graphops.bgraphops import BaseGraphEdgeOps
from pygmodels.graphops.bgraphops import BaseGraphBoolOps
from pygmodels.graphops.graphsearcher import BaseGraphSearcher
from pygmodels.gtype.abstractobj import AbstractTree
from pygmodels.gtype.basegraph import BaseGraph
from pygmodels.gtype.edge import Edge, EdgeType
from pygmodels.gtype.node import Node
from pygmodels.gtype.queue import PriorityQueue


class Tree(BaseGraph, AbstractTree):
    """!
    Ordered Tree object
    """

    def __init__(self, gid: str, data={}, edges: Set[Edge] = None):
        """"""
        nodes = None
        if edges is not None:
            nodes = set()
            for e in edges:
                estart = e.start()
                eend = e.end()
                nodes.add(estart)
                nodes.add(eend)
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges)
        self.__root = None
        es = [e.type() for e in self.E]
        if es[0] == EdgeType.DIRECTED:

            def egen(x):
                return BaseGraphEdgeOps.outgoing_edges_of(self, x)

        else:

            def egen(x):
                return BaseGraphEdgeOps.edges_of(self, x)

        self.paths: Dict[
            str, Union[dict, set]
        ] = BaseGraphSearcher.breadth_first_search(
            self, n1=self.root, edge_generator=egen
        )
        self.topsort = self.paths.top_sort
        self.bfs_tree = self.paths.tree[self.root.id()]

    @classmethod
    def from_node_tuples(cls, ntpls: Set[Tuple[Node, Node, EdgeType]]):
        """"""
        edges: Set[Edge] = set()

        for e in ntpls:
            child = e[0]
            parent = e[1]
            edge = Edge(
                edge_id=str(uuid4()), start_node=parent, end_node=child, edge_type=e[2],
            )
            edges.add(edge)
        return Tree(gid=str(uuid4()), edges=edges)

    @classmethod
    def from_edgeset(cls, eset: Set[Edge]):
        """"""
        return Tree(gid=str(uuid4()), edges=eset)

    def node_table(self):
        """"""
        node_table = {v.id(): {"child": False, "parent": False} for v in self.V}
        for e in self.E:
            estart_id = e.start().id()
            eend_id = e.end().id()
            node_table[estart_id]["parent"] = True
            node_table[eend_id]["child"] = True
        #
        return node_table

    def get_root(self):
        """"""
        node_table = self.node_table()
        root_ids = [
            k
            for k, v in node_table.items()
            if v["child"] is False and v["parent"] is True
        ]
        V = {v.id(): v for v in self.V}
        return V[root_ids[0]]

    def leaves(self) -> Set[Node]:
        """"""
        node_table = self.node_table()
        #
        leave_ids = [
            k
            for k, v in node_table.items()
            if v["child"] is True and v["parent"] is False
        ]
        return set([v for v in self.V if v.id() in leave_ids])

    @property
    def root(self) -> Node:
        """"""
        if self.__root is None:
            self.__root = self.get_root()
        return self.__root

    def height_of(self, n: Node) -> int:
        """!"""
        if not BaseGraphBoolOps.is_in(self, n):
            raise ValueError("node not in tree")
        nid = n.id()
        return self.topsort[nid]

    def _is_closure_of(self, x: Node, y: Node, fn: Callable[[int, int], bool]) -> bool:
        """"""
        xheight = self.height_of(x)
        yheight = self.height_of(y)
        f = fn(xheight, yheight)
        print(f)
        print(x)
        print(y)
        return f

    def is_upclosure_of(self, x_src: Node, y_dst: Node) -> bool:
        """!
        From Diestel 2017, p. 15
        is x upclosure of y
        """
        xheight = self.height_of(x_src)
        yheight = self.height_of(y_dst)
        return yheight >= xheight

    def is_downclosure_of(self, x_src: Node, y_dst: Node) -> bool:
        """!
        From Diestel 2017, p. 15
        is x down closure of y
        """
        xheight = self.height_of(x_src)
        yheight = self.height_of(y_dst)
        return yheight <= xheight

    def upset_of(self, n: Node) -> Set[Node]:
        """!
        From Diestel 2017, p. 15
        """
        return self.is_set_of(n, fn=self.is_upclosure_of)

    def downset_of(self, n: Node) -> Set[Node]:
        """!
        From Diestel 2017, p. 15
        """
        return self.is_set_of(n, fn=self.is_downclosure_of)

    def is_set_of(self, n: Node, fn: Callable[[Node, Node], bool]) -> Set[Node]:
        nodes = self.V
        nset = set([y for y in nodes if fn(n, y) is True])
        return nset

    def less_than_or_equal(self, first: Node, second: Node) -> bool:
        """"""
        return self.height_of(first) <= self.height_of(second)

    def greater_than_or_equal(self, first: Node, second: Node) -> bool:
        """"""
        return self.height_of(first) >= self.height_of(second)

    def nodes_per_level(self, level: int) -> Set[Node]:
        """!
        extract nodes of certain level in tree
        """
        return set([n for n in self.V if self.height_of(n) == level])

    def extract_path(
        self,
        start: Node,
        end: Node,
        filter_fn: Callable[[Set[Edge], str], Set[Edge]] = lambda es, n: set(
            [e for e in es if e.start().id() == n]
        ),
        costfn: Callable[[Edge, float], float] = lambda x, y: y + 1.0,
        is_min=True,
    ):
        """"""
        if (
            BaseGraphBoolOps.is_in(self, start) is False
            or BaseGraphBoolOps.is_in(self, end) is False
        ):
            raise ValueError("start or end node is not inside tree")
        #
        upset = self.upset_of(start)
        if end not in upset:
            raise ValueError("end node is not in upset of start.")
        downset = self.downset_of(end)
        upset_edges = set()
        for u in upset:
            for e in BaseGraphEdgeOps.outgoing_edges_of(self, u):
                upset_edges.add(e)
        downset_edges = set()
        for d in downset:
            for e in BaseGraphEdgeOps.outgoing_edges_of(self, d):
                downset_edges.add(e)
        problem_set = upset_edges.intersection(downset_edges)
        ucs_path = Path.from_ucs(
            g=self,
            goal=end,
            start=start,
            filter_fn=filter_fn,
            costfn=costfn,
            is_min=is_min,
            problem_set=problem_set,
        )
        return ucs_path

    @classmethod
    def find_mst_prim(
        cls, g: BaseGraph, edge_generator: Callable[[Node], Set[Node]]
    ) -> AbstractTree:
        """!
        Find minimum spanning tree as per Prim's algorithm
        Even and Guy Even 2012, p. 32
        """
        l_e = 1  # length of an edge
        l_vs = {}
        vs = []
        eps = {}

        for v in g.V:
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
            for edge in edge_generator(g.V[minv]):
                unode = edge.get_other(g.V[minv])
                u = unode.id()
                if u in TEMP and l_vs[u] > l_e:
                    l_vs[u] = l_e
                    eps[u] = set([edge])
        return cls.from_edgeset(eset=T)

    @classmethod
    def find_mnmx_st(
        cls,
        g: BaseGraph,
        edge_generator: Callable[[Node], Set[Edge]],
        weight_function: Callable[[Edge], float] = lambda x: 1,
        is_min: bool = True,
    ) -> Tuple[AbstractTree, List[Edge]]:
        """!
        a modified version of kruskal minimum spanning tree adapted for
        finding minimum and maximum weighted spanning tree of a graph

        from Even and Guy Even 2012, p. 42
        """
        queue = PriorityQueue(is_min=is_min)
        T: Set[Edge] = set()
        clusters = {v.id(): set([v]) for v in g.V}
        L: List[Edge] = []
        for edge in g.E:
            queue.insert(weight_function(edge), edge)
        #
        while len(queue) > 0:
            edge = None
            if is_min is True:
                k, edge = queue.min()
            else:
                k, edge = queue.max()
            #
            u = edge.start().id()
            v = edge.end().id()
            vset = clusters[v]
            uset = clusters[u]
            if vset != uset:
                T.add(edge)
                L.append(edge)
                clusters[v] = vset.union(uset)
                clusters[u] = vset.union(uset)
        return cls.from_edgeset(eset=T), L

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
        """"""
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
        """"""
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
