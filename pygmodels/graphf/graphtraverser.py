"""!
Traverse graphs in some fashion
"""
from typing import Set, Optional, Callable, List, Tuple, Dict, Union
from pygmodels.gtype.abstractobj import AbstractGraph
from pygmodels.graphf.bgraphops import BaseGraphOps

from pygmodels.gtype.node import Node
from pygmodels.gtype.edge import Edge
import math


class BaseGraphTraverser:
    """!
    """

    @staticmethod
    def dfs_forest(
        g: AbstractGraph,
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
                BaseGraphTraverser.dfs_forest(
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
        g: AbstractGraph,
        edge_generator: Callable[[Node], Set[Node]],
        check_cycle: bool = False,
    ):
        """!
        \brief interior visit function for depth first enumeration of graph
        instance.

        \see dfs_forest() method for more information on parameters.
        """
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
                BaseGraphTraverser.dfs_forest(
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
            "dfs-forest": BaseGraphTraverser.from_preds_to_edgeset(g, preds),
            "first-visit-times": d,
            "last-visit-times": f,
            "components": Ts,
            "cycle-info": cycles,
            "nb-component": component_counter,
        }
        return res

    @staticmethod
    def from_preds_to_edgeset(
        g: AbstractGraph, preds: Dict[str, Dict[str, str]]
    ) -> Dict[str, Set[Edge]]:
        """!
        \brief obtain the edge set implied by the predecessor array.
        """
        esets: Dict[str, Set[Edge]] = {}
        for u, forest in preds.copy().items():
            eset: Set[Edge] = set()
            for child, parent in forest.items():
                cnode = g.V[child]
                if parent is not None:
                    pnode = g.V[parent]
                    eset = eset.union(
                        BaseGraphOps.edge_by_vertices(g, start=pnode, end=cnode)
                    )
            esets[u] = eset
        return esets

    @staticmethod
    def find_shortest_paths(
        g: AbstractGraph, n1: Node, edge_generator: Callable[[Node], Set[Edge]]
    ) -> Dict[str, Union[dict, set]]:
        """!
        \brief find shortest path from given node to all other nodes

        Applies the Breadth first search algorithm from Even and Guy Even 2012, p. 12

        \throws ValueError if given node is not found in graph instance
        """
        if not BaseGraphOps.is_in(g, n1):
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
