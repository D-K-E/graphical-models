"""!
Traverse graphs in some fashion
"""
from typing import Set, Optional, Callable, List, Tuple, Dict, Union
from gmodels.gtype.abstractobj import AbstractGraph
from gmodels.gtype.basegraph import BaseGraph
from gmodels.gtype.finitegraph import FiniteGraph

from gmodels.gtype.node import Node
from gmodels.gtype.edge import Edge
import math


class GraphTraverser:
    def __init__(self):
        pass

    @staticmethod
    def cast_graph(g_: AbstractGraph):
        """!
        """
        if isinstance(g_, FiniteGraph):
            return g_
        elif isinstance(g_, BaseGraph):
            return FiniteGraph.from_base_graph(g_)
        else:
            return FiniteGraph.from_abstract_graph(g_)

    @staticmethod
    def dfs_forest(
        g_: AbstractGraph,
        u: str,
        pred: Dict[str, str],
        marked: Dict[str, int],
        d: Dict[str, int],
        f: Dict[str, int],
        T: Set[str],
        cycles: Dict[str, List[Dict[str, Union[str, int]]]],
        time: int,
        edge_generator: Callable[[Node], Set[Edge]],
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
        \param T set of pred nodes
        \param time global visit counter
        \param check_cycle fill cycles if it is detected
        \param edge_generator generate edges of a vertex with respect to graph type
        """
        g = GraphTraverser.cast_graph(g_)
        marked[u] = True
        time += 1
        d[u] = time
        unode = g.V[u]
        for edge in edge_generator(unode):
            vnode = edge.get_other(unode)
            v = vnode.id()
            if marked[v] is False:
                pred[v] = u
                T.add(v)
                GraphTraverser.dfs_forest(
                    g,
                    u=v,
                    pred=pred,
                    marked=marked,
                    d=d,
                    f=f,
                    T=T,
                    cycles=cycles,
                    time=time,
                    check_cycle=check_cycle,
                    edge_generator=edge_generator,
                )
        #
        time += 1
        f[u] = time
        if check_cycle:
            # v ancestor, u visiting node
            # edge between them is a back edge
            # see p. 151, and p. 159-160
            unode = g.V[u]
            for edge in edge_generator(unode):
                vnode = edge.get_other(unode)
                vid = vnode.id()
                if pred[u] != vid:
                    first_visit = d.get(vid)
                    last_visit = f.get(vid)
                    cond = d[vid] < f[u]
                    if cond:
                        cycle_info = {
                            "ancestor": vid,
                            "before": u,
                            "ancestor-first-time-visit": d[vid],
                            "current-final-time-visit": f[u],
                        }
                        cycles[u].append(cycle_info)
        #
        return None

    @staticmethod
    def visit_graph_dfs(
        g_: AbstractGraph,
        edge_generator: Callable[[Node], Set[Node]],
        check_cycle: bool = False,
    ):
        """!
        \brief interior visit function for depth first enumeration of graph
        instance.

        \see dfs_forest() method for more information on parameters.
        """
        g = GraphTraverser.cast_graph(g_)
        time = 0
        marked: Dict[str, bool] = {n: False for n in g.V}
        preds: Dict[str, Dict[str, str]] = {}
        Ts: Dict[str, Set[str]] = {}
        d: Dict[str, int] = {n: math.inf for n in g.V}
        f: Dict[str, int] = {n: math.inf for n in g.V}
        cycles: Dict[str, List[Dict[str, Union[str, int]]]] = {n: [] for n in g.V}
        component_counter = 0
        #
        for u in g.V:
            if marked[u] is False:
                pred: Dict[str, Optional[str]] = {n: None for n in g.V}
                T: Set[str] = set()
                GraphTraverser.dfs_forest(
                    g,
                    u=u,
                    pred=pred,
                    cycles=cycles,
                    marked=marked,
                    d=d,
                    T=T,
                    f=f,
                    time=time,
                    check_cycle=check_cycle,
                    edge_generator=edge_generator,
                )
                component_counter += 1
                for child, parent in pred.copy().items():
                    if child != u and child is None:
                        pred.pop(child)
                Ts[u] = T
                preds[u] = pred
        #
        res = {
            "dfs-forest": GraphTraverser.from_preds_to_edgeset(g, preds),
            "first-visit-times": d,
            "last-visit-times": f,
            "components": Ts,
            "cycle-info": cycles,
            "nb-component": component_counter,
        }
        return res

    @staticmethod
    def from_preds_to_edgeset(
        g_: AbstractGraph, preds: Dict[str, Dict[str, str]]
    ) -> Dict[str, Set[Edge]]:
        """!
        \brief obtain the edge set implied by the predecessor array.
        """
        g = GraphTraverser.cast_graph(g_)
        esets: Dict[str, Set[Edge]] = {}
        for u, forest in preds.copy().items():
            eset: Set[Edge] = set()
            for child, parent in forest.items():
                cnode = g.V[child]
                if parent is not None:
                    pnode = g.V[parent]
                    eset = eset.union(g.edge_by_vertices(start=pnode, end=cnode))
            esets[u] = eset
        return esets

    @staticmethod
    def find_shortest_paths(
        g_: AbstractGraph, n1: Node, edge_generator: Callable[[Node], Set[Edge]]
    ) -> Dict[str, Union[dict, set]]:
        """!
        \brief find shortest path from given node to all other nodes

        Applies the Breadth first search algorithm from Even and Guy Even 2012, p. 12

        \throws ValueError if given node is not found in graph instance
        """
        g = GraphTraverser.cast_graph(g_)
        if not g.is_in(n1):
            raise ValueError("argument node is not in graph")
        nid = n1.id()
        Q = [nid]
        l_vs = {v: math.inf for v in g.V}
        l_vs[nid] = 0
        T = set([nid])
        P: Dict[str, Dict[str, str]] = {}
        P[nid] = {}
        while Q:
            u = Q.pop(0)
            unode = g.V[u]
            for edge in edge_generator(unode):
                vnode = edge.get_other(unode)
                vid = vnode.id()
                if vid not in T:
                    T.add(vid)
                    l_vs[vid] = int(l_vs[u] + 1)
                    P[nid][u] = vid
                    Q.append(vid)
        #
        T = set([g.V[t] for t in T])
        path_props = {"bfs-tree": P, "path-set": T, "top-sort": l_vs}
        return path_props
