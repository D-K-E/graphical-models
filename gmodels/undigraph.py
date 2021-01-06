"""
Undirected graph object
"""
from typing import Set, Optional, List, Tuple, Dict
from gmodels.edge import Edge
from gmodels.node import Node
from gmodels.path import Path, Cycle
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

    def find_shortest_path(self, n1: Node, n2: Node) -> Optional[Path]:
        ""
        try:
            Path.from_graph_nodes(self, n1=n1, n2=n2, generative_fn=self.neighbours_of)
        except ValueError:
            return None

    def check_for_path(self, n1: Node, n2: Node) -> bool:
        "check if there is a path between nodes"
        return self.find_shortest_path(n1, n2) is not None

    def shortest_path_length(self) -> int:
        "see proof Diestel 2017, p. 8"
        return self.min_degree()

    def find_shortest_path_per_node(self, n: Node) -> Path:
        "find shortest path for node n"
        nodes = self.nodes()
        result = None
        result_len = math.inf
        for node in nodes:
            if n.id() != node.id():
                path = self.find_shortest_path(n1=n, n2=node)
                if path is not None:
                    plen = path.length()
                    if plen < result_len:
                        result = path
                        result_len = plen
        return result

    def find_connected_components(self):
        """!
        Find connected components as per Roughgarden 2018, 8.8.3 UCC algorithm
        """
        # mark all vertices as unexplored
        vertices = {k: False for k in self.gdata.keys()}
        #
        numCC = 0
        components = {}
        for i, explored in vertices.items():
            if not explored:
                numCC += 1
                components[numCC] = set()
                frontier = [i]
                while frontier:
                    v = frontier.pop(0)
                    cc_v = numCC
                    node_v = self.V[v]
                    for w in self.neighbours_of(node_v):
                        wid = w.id()
                        if not vertices[wid]:
                            vertices[wid] = True
                            components[cc_v].add(wid)
        return components

    def find_minimum_spanning_tree(self):
        """!
        Find minimum spanning tree as per Prim's algorithm
        Christopher Griffin, Graph Theory lecture notes, 2016, p.39 - 42
        """
        e_prim: Set[str] = set()
        v_prim: Set[str] = set([[v for v in self.V][0]])
        weights: Dict[str, int] = {e: 1 for e in self.E}
        V: Set[str] = set([v for v in self.V])
        while v_prim != V:
            X = V.difference(v_prim)
            e: Edge = None
            w_star = math.inf
            u_prime: str = None
            for v in v_prim:
                for u in X:
                    vnode = self.V[v]
                    unode = self.V[u]
                    edge = self.edge_by_vertices(vnode, unode)
                    w_edge = weights[edge.id()]
                    if w_edge < w_star:
                        w_star = w_edge
                        e = edge
                        u_prime = u
            e_prim.add(e.id())
            v_prim.add(u_prime)
        #
        V_prime = set([self.V[v] for v in v_prim])
        E_prime = set([self.E[e] for v in e_prim])
        return UndiGraph(gid=str(uuid4()), nodes=V_prime, edges=E_prime)

    def dfs_forest(
        self,
        u: str,
        pred: Dict[str, str],
        marked: Dict[str, int],
        d: Dict[str, int],
        f: Dict[str, int],
        time: int,
        check_cycle: bool = True,
    ) -> Optional[Tuple[str, str]]:
        """!
        adapted for cycle detection
        dfs recursive forest from Erciyes 2018, Guide Graph ..., p.152 alg. 6.7
        """
        marked[u] = True
        time += 1
        d[u] = time
        unode = self.V[u]
        for vnode in self.neighbours_of(unode):
            v = vnode.id()
            if marked[v] is False:
                pred[v] = u
                self.dfs_forest(v, pred, marked, d, f, time)
        #
        time += 1
        f[u] = time
        if check_cycle:
            for vnode in self.neighbours_of(unode):
                if d[vnode.id()] < f[u]:
                    return (vnode.id(), u)
        return None

    def from_preds(
        self,
        before_last: str,
        start_end_cycle: str,
        pred: Dict[str, Optional[str]],
        nlist: List[Node],
        elist: List[Edge],
    ):
        "derive from predicates"
        temp = pred[before_last]
        while temp != start_end_cycle:
            tnode = self.V[temp]
            nlist.append(temp)
            temp = pred[temp]
            tnode2 = self.V[temp]
            edge = self.edge_by_vertices(tnode, tnode2)
            elist.append(edge)

    def find_cycle(self) -> Cycle:
        "find if graph has a cycle exit at first found cycle"
        time = 0
        marked: Dict[str, bool] = {n: False for n in self.V}
        pred: Dict[str, Optional[str]] = {n: None for n in self.V}
        d: Dict[str, int] = {}
        f: Dict[str, int] = {}
        for u in self.V:
            if marked[u] is False:
                res = self.dfs_forest(
                    u=u, pred=pred, marked=marked, d=d, f=f, time=time, check_cycle=True
                )
                if res is not None:
                    start_end_cycle, before_last = res
                    nlist: List[Node] = []
                    elist: List[Edge] = []
                    self.from_preds(
                        pred=pred,
                        before_last=before_last,
                        start_end_cycle=start_end_cycle,
                        nlist=nlist,
                        elist=elist,
                    )
                    return Cycle(gid=str(uuid4()), nodes=nlist, edges=elist)

    def has_cycle(self) -> bool:
        "check if graph has a cycle"
        cycle = self.find_cycle()
        return cycle is not None

    def assign_num(
        self,
        v: str,
        num: Dict[str, int],
        visited: Dict[str, bool],
        parent: Dict[str, str],
        counter: int,
    ):
        ""
        counter += 1
        num[v] = counter
        visited[v] = True
        vnode = self.V[v]
        for unode in self.neighbours_of(vnode):
            u = unode.id()
            if visited[u] is False:
                parent[u] = v
                self.assign_num(
                    u, num=num, visited=visited, parent=parent, counter=counter
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
    ):
        ""
        low[v] = num[v]
        vnode = self.V[v]
        for unode in self.neighbours_of(vnode):
            u = unode.id()
            if num[u] >= num[v]:
                self.check_ap(
                    v=u,
                    num=num,
                    visited=visited,
                    parent=parent,
                    low=low,
                    counter=counter,
                    aset=aset,
                )
                if low[u] >= low[v]:
                    aset.add(v)
                #
                low[v] = min(low[v], low[u])
            elif parent[v] != u:
                low[v] = min(low[v], num[u])

    def find_separating_vertices(self) -> Set[Node]:
        """!
        find separating vertices of graph
        as in Erciyes 2018, p. 230, algorithm 8.3
        """
        num: Dict[str, int] = {n: int(math.inf) for n in self.V}
        low: Dict[str, int] = {n: int(math.inf) for n in self.V}
        visited: Dict[str, bool] = {n: False for n in self.V}
        parent: Dict[str, str] = {n: "" for n in self.V}
        aset: Set[str] = set()

        counter = 1
        v = [node for node in self.V.values()][0]
        self.assign_num(v=v, num=num, visited=visited, parent=parent, counter=counter)
        self.check_ap(
            v=v,
            num=num,
            visited=visited,
            parent=parent,
            low=low,
            counter=counter,
            aset=aset,
        )
        return set([self.V[a] for a in aset])
