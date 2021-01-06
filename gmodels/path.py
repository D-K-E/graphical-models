"""!
Path in a given graph
"""
from typing import Set, Optional, Callable, List, Tuple, Dict, Union
from gmodels.edge import Edge
from gmodels.node import Node
from gmodels.graph import Graph
from uuid import uuid4
import math


class Path(Graph):
    """!
    path object as defined in Diestel 2017, p. 6
    """

    def __init__(
        self, gid: str, data={}, nodes: List[Node] = None, edges: List[Edge] = None
    ):
        ""
        super().__init__(gid=gid, data=data, nodes=set(nodes), edges=set(edges))
        self._node_list = nodes
        self._edge_list = edges

    def length(self) -> int:
        if self._edge_list is None:
            return 0
        return len(self._edge_list)

    def node_list(self) -> List[Node]:
        "get vertice list"
        if self._node_list is None or len(self._node_list) == 0:
            raise ValueError("there are no vertices in the path")
        return self._node_list

    def endvertices(self) -> Tuple[Node, Node]:
        ""
        vs = self.node_list()
        if len(vs) == 1:
            return (vs[0], vs[0])
        return (vs[0], vs[-1])

    @staticmethod
    def dfs_forest(
        g: Graph,
        u: str,
        pred: Dict[str, Optional[str]],
        marked: Dict[str, int],
        d: Dict[str, int],
        f: Dict[str, int],
        cycles: Dict[str, List[Dict[str, Union[str, int]]]],
        time: int,
        generative_fn: Callable[[Graph, Node], Set[Node]],
        check_cycle: bool = False,
    ) -> Optional[Tuple[str, str]]:
        """!
        adapted for cycle detection
        dfs recursive forest from Erciyes 2018, Guide Graph ..., p.152 alg. 6.7

        \param f storing last visit times per node
        \param d storing first visit times per node
        \param cycles storing cycle info
        \param marked storing if node is visited
        \param pred storing the parent of nodes
        \param g graph we are searching for
        \param u node id
        \param time global visit counter
        \param check_cycle fill cycles if it is detected
        \param generative_fn generate neighbour of a vertex with respect to graph type
        """
        marked[u] = True
        time += 1
        d[u] = time
        unode = g.V[u]
        for vnode in generative_fn(g, unode):
            v = vnode.id()
            if marked[v] is False:
                pred[v] = u
                Path.dfs_forest(
                    g=g,
                    u=v,
                    pred=pred,
                    marked=marked,
                    d=d,
                    f=f,
                    cycles=cycles,
                    time=time,
                    check_cycle=check_cycle,
                    generative_fn=generative_fn,
                )
        #
        time += 1
        f[u] = time
        if check_cycle:
            # v ancestor, u visiting node
            # edge between them is a back edge
            # see p. 151, and p. 159-160
            for vnode in generative_fn(g, unode):
                if d[vnode.id()] < f[u]:
                    cycle_info = {
                        "ancestor": vnode.id(),
                        "before": u,
                        "first-time-visit": d[vnode.id()],
                        "final-time-visit": f[u],
                    }
                    cycles[u].append(cycle_info)
        return None

    @staticmethod
    def visit_graph(
        g: Graph, generative_fn: Callable[[Node], Set[Node]], check_cycle: bool = False,
    ) -> Tuple[
        Dict[str, Optional[str]],
        Dict[str, int],
        Dict[str, int],
        Dict[str, List[Dict[str, Union[str, int]]]],
        int,
    ]:
        """!
        dfs with for directed and undirected graphs and for cycle detection
        """
        time = 0
        marked: Dict[str, bool] = {n: False for n in g.V}
        pred: Dict[str, Optional[str]] = {n: None for n in g.V}
        d: Dict[str, int] = {}
        f: Dict[str, int] = {}
        cycles: Dict[str, List[Dict[str, Union[str, int]]]] = {n: [] for n in g.V}
        component_counter = 0
        #
        for u in g.V:
            if marked[u] is False:
                Path.dfs_forest(
                    g=g,
                    u=u,
                    pred=pred,
                    cycles=cycles,
                    marked=marked,
                    d=d,
                    f=f,
                    time=time,
                    check_cycle=check_cycle,
                    generative_fn=generative_fn,
                )
                component_counter += 1

        return pred, d, f, cycles, component_counter

    @classmethod
    def from_graph_nodes(
        cls, g: Graph, generative_fn: Callable[[Graph, Node], Set[Node]]
    ):
        """!
        construct path from graph and nodes
        """
        res = Path.visit_graph(g, generative_fn=generative_fn, check_cycle=False)
        if res is None:
            raise ValueError("can not create path with these parameters")
        nodelist, edgelist = res
        return Path(gid=str(uuid4()), data={}, nodes=nodelist, edges=edgelist)


class Tree(Graph):
    """!
    Tree object
    """


class Cycle(Path):
    """!
    Cycle as defined in Diestel p. 8
    """

    def __init__(
        self, gid: str, data={}, nodes: List[Node] = None, edges: List[Edge] = None
    ):
        ""
        super().__init__(gid, data, nodes, edges)
        vs = self.vertices()
        if vs[0] != vs[-1]:
            raise ValueError("The first and last vertice of a cycle must be same")
