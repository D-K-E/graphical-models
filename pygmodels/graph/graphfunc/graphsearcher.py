"""!
Traverse graphs in some fashion
"""
import math
from typing import Callable, Dict, List, Optional, Set, Tuple, Union

from pygmodels.graph.graphfunc.graphops import (
    BaseGraphBoolOps,
    BaseGraphEdgeOps,
    BaseGraphNodeOps,
    BaseGraphOps,
)
from pygmodels.graph.graphtype.abstractobj import (
    AbstractEdge,
    AbstractGraph,
    AbstractNode,
)
from pygmodels.graph.graphtype.searchresult import (
    BaseGraphBFSResult,
    BaseGraphDFSResult,
)
from pygmodels.graph.graphtype.queue import PriorityQueue
from pygmodels.utils import is_type


class BaseGraphSearcher:
    """!"""

    @staticmethod
    def dfs_forest(
        g: AbstractGraph,
        V: Dict[str, AbstractNode],
        u: str,
        pred: Dict[str, str],
        marked: Dict[str, int],
        d: Dict[str, int],
        f: Dict[str, int],
        T: Set[str],
        cycles: Dict[str, List[Dict[str, Union[str, int]]]],
        time: int,
        edge_generator: Callable[[AbstractNode], Set[AbstractEdge]],
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
        \param V vertex set of g converted to dict for easy access
        \param u node id
        \param T set of pred nodes
        \param time global visit counter
        \param check_cycle fill cycles if it is detected
        \param edge_generator generate edges of a vertex with respect to graph type
        """
        is_type(g, "g", AbstractGraph, True)
        marked[u] = True
        time += 1
        d[u] = time
        unode = V[u]
        for edge in edge_generator(unode):
            vnode = edge.get_other(unode)
            v = vnode.id
            if marked[v] is False:
                pred[v] = u
                T.add(v)
                BaseGraphSearcher.dfs_forest(
                    g=g,
                    V=V,
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
            # unode = V[u]
            for edge in edge_generator(unode):
                vnode = edge.get_other(unode)
                vid = vnode.id
                if pred[u] != vid:
                    first_visit = d.get(vid)
                    last_visit = f.get(vid)
                    cond = d[vid] < f[u]
                    if cond:
                        cycle_info = {
                            "ancestor": vid,
                            "before": u,
                            "ancestor-first-time-visit": first_visit,
                            "ancestor-last-time-visit": last_visit,
                            "current-final-time-visit": f[u],
                        }
                        cycles[u].append(cycle_info)
        #
        return None

    @staticmethod
    def depth_first_search(
        g: AbstractGraph,
        edge_generator: Callable[[AbstractNode], Set[AbstractNode]],
        check_cycle: bool = False,
        start_node: Optional[AbstractNode] = None,
    ) -> BaseGraphDFSResult:
        """!
        \brief interior visit function for depth first enumeration of graph
        instance.

        \see dfs_forest() method for more information on parameters.
        """
        is_type(g, "g", AbstractGraph, True)
        V: Dict[str, AbstractNode] = {n.id: n for n in g.V}
        if start_node is not None:
            if not BaseGraphBoolOps.is_in(g, start_node):
                raise ValueError("Specified start node not in graph")
            #
            Vlst: List[str] = list(v for v in V.keys() if v != start_node.id)
            Vlst.insert(0, start_node.id)
            Vlst.sort()
        else:
            Vlst = list(v for v in V.keys())
            Vlst.sort()
        time = 0
        marked: Dict[str, bool] = {n: False for n in V}
        preds: Dict[str, Dict[str, str]] = {}
        Ts: Dict[str, Set[str]] = {}
        d: Dict[str, int] = {n: math.inf for n in V}
        f: Dict[str, int] = {n: math.inf for n in V}
        cycles: Dict[str, List[Dict[str, Union[str, int]]]] = {n: [] for n in V}
        component_counter = 0
        #
        for u in Vlst:
            if marked[u] is False:
                pred: Dict[str, Optional[str]] = {n: None for n in V}
                T: Set[str] = set()
                BaseGraphSearcher.dfs_forest(
                    g=g,
                    V=V,
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
            "dfs-forest": BaseGraphSearcher.from_preds_to_edgeset(g, preds),
            "dfs-trees": preds,
            "first-visit-times": d,
            "last-visit-times": f,
            "components": Ts,
            "cycle-info": cycles,
            "nb-component": component_counter,
        }
        return BaseGraphDFSResult(
            props=res,
            result_id="dfs-result-of-" + g.id,
            search_name="depth_first_search",
            data={},
        )

    @staticmethod
    def from_preds_to_edgeset(
        g: AbstractGraph, preds: Dict[str, Dict[str, str]]
    ) -> Dict[str, Set[AbstractEdge]]:
        """!
        \brief obtain the edge set implied by the predecessor array.
        """
        is_type(g, "g", AbstractGraph, True)
        esets: Dict[str, Set[AbstractEdge]] = {}
        V = {v.id: v for v in g.V}
        for u, forest in preds.copy().items():
            eset: Set[AbstractEdge] = set()
            for child, parent in forest.items():
                cnode = V[child]
                if parent is not None:
                    pnode = V[parent]
                    eset = eset.union(
                        BaseGraphEdgeOps.edge_by_vertices(g, start=pnode, end=cnode)
                    )
            esets[u] = eset
        return esets

    @staticmethod
    def breadth_first_search(
        g: AbstractGraph,
        n1: AbstractNode,
        edge_generator: Callable[[AbstractNode], Set[AbstractEdge]],
    ) -> BaseGraphBFSResult:
        """!
        \brief find shortest path from given node to all other nodes

        Applies the Breadth first search algorithm from Even and Guy Even 2012, p. 12

        \throws ValueError if given node is not found in graph instance
        """
        is_type(g, "g", AbstractGraph, True)
        if not BaseGraphBoolOps.is_in(g, n1):
            raise ValueError("argument node is not in graph")
        nid = n1.id
        Q = [nid]
        V: Dict[str, AbstractNode] = {v.id: v for v in g.V}
        l_vs = {v: math.inf for v in V}
        l_vs[nid] = 0
        T = set([nid])
        P: Dict[str, Dict[str, str]] = {}
        P[nid] = {}
        while Q:
            u = Q.pop(0)
            unode = V[u]
            for edge in edge_generator(unode):
                vnode = edge.get_other(unode)
                vid = vnode.id
                if vid not in T:
                    T.add(vid)
                    l_vs[vid] = int(l_vs[u] + 1)
                    P[nid][u] = vid
                    Q.append(vid)
        #
        T = set([V[t] for t in T])
        path_props = {"bfs-tree": P, "path-set": T, "top-sort": l_vs}
        return BaseGraphBFSResult(
            props=path_props,
            result_id="bfs-result-of-" + g.id,
            search_name="breadth_first_search",
            data={},
        )

    @staticmethod
    def uniform_cost_search(
        g: AbstractGraph,
        start: AbstractNode,
        goal: AbstractNode,
        filter_fn: Callable[
            [Set[AbstractEdge], str], Set[AbstractEdge]
        ] = lambda es, n: set([e for e in es if e.start.id == n]),
        costfn: Callable[[AbstractEdge, float], float] = lambda x, y: y + 1.0,
        is_min=True,
        problem_set: Optional[Set[AbstractEdge]] = None,
    ) -> Tuple[
        Dict[str, Union[int, AbstractNode, AbstractEdge, str]],
        Tuple[AbstractEdge],
    ]:
        """!
        Apply uniform cost search to given problem set
        """
        is_type(g, "g", AbstractGraph, True)
        if not BaseGraphBoolOps.is_in(g, start) or not BaseGraphBoolOps.is_in(g, goal):
            raise ValueError("Start node or goal node is not in graph")
        problem_set = g.E if problem_set is None else problem_set
        pnode = {"cost": 0, "state": start.id, "parent": None, "edge": None}
        frontier = PriorityQueue(is_min=is_min)
        frontier.insert(key=pnode["cost"], val=pnode)
        explored: Set[str] = set()
        while len(frontier) != 0:
            key, pn = frontier.pop()
            if pn["state"] == goal.id:
                return BaseGraphSearcher.from_ucs_result(pn), pn
            explored.add(pn["state"])
            for child_edge in filter_fn(problem_set, pn["state"]):
                child: AbstractNode = child_edge.get_other(pn["state"])
                cnode = {
                    "cost": costfn(child_edge, pn["cost"]),
                    "state": child.id,
                    "parent": pn,
                    "edge": child_edge,
                }
                if (child.id not in explored) or (
                    frontier.is_in(child, cmp_f=lambda x: x["state"]) is False
                ):
                    frontier.insert(cnode["cost"], cnode)
                elif frontier.is_in(child, cmp_f=lambda x: x["state"]) is True:
                    # node is already in frontier
                    ckey = frontier.key(child, f=lambda x: x["state"])
                    if ckey > cnode["cost"]:
                        frontier.insert(cnode["cost"], cnode, f=lambda x: x["state"])

    @staticmethod
    def from_ucs_result(
        ucs_solution: Dict[str, Union[int, AbstractNode, AbstractEdge, str]]
    ) -> Tuple[AbstractEdge]:
        """!
        parse uniform cost search solution to create a path
        """
        edges = [ucs_solution["edge"]]
        while ucs_solution["parent"] is not None:
            ucs_solution = ucs_solution["parent"]
            edges.append(ucs_solution["edge"])
        edges.pop()  # last element edge is None
        edges = tuple(reversed(edges))
        return edges
