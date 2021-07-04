"""!
Path in a given graph
"""
from typing import Set, Optional, Callable, List, Tuple, Dict, Union
from gmodels.gtype.edge import Edge, EdgeType
from gmodels.gtype.node import Node
from gmodels.gtype.graph import Graph
from gmodels.gtype.queue import PriorityQueue
from uuid import uuid4
import math


class Path(Graph):
    """!
    path object as defined in Diestel 2017, p. 6
    """

    def __init__(self, gid: str, data={}, edges: List[Edge] = None):
        ""
        nodes = None
        if edges is not None:
            nodes = set()
            ns = [edges[0].start()]
            for e in edges:
                estart = e.start()
                eend = e.end()
                nodes.add(estart)
                nodes.add(eend)
                if eend not in ns:
                    ns.append(eend)

        super().__init__(gid=gid, data=data, nodes=set(nodes), edges=set(edges))
        self._node_list = ns
        self._edge_list = edges

    @classmethod
    def from_edgelist(cls, edges: List[Edge]):
        """!
        create path from edge list
        """
        return Path(gid=str(uuid4()), edges=edges)

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

    @classmethod
    def uniform_cost_search(
        cls,
        goal: Node,
        start: Node,
        problem_set: Set[Edge],
        filter_fn: Callable[[Set[Edge], str], Set[Edge]] = lambda es, n: set(
            [e for e in es if e.start().id() == n]
        ),
        costfn: Callable[[Edge, float], float] = lambda x, y: y + 1.0,
        is_min=True,
    ):
        """!
        Apply uniform cost search to given problem set
        """
        pnode = {"cost": 0, "state": start.id(), "parent": None, "edge": None}
        frontier = PriorityQueue(is_min=is_min)
        frontier.insert(key=pnode["cost"], val=pnode)
        explored: Set[str] = set()
        while len(frontier) != 0:
            key, pn = frontier.pop()
            if pn["state"] == goal.id():
                return pn
            explored.add(pn["state"])
            for child_edge in filter_fn(problem_set, pn["state"]):
                child: Node = child_edge.get_other(pn["state"])
                cnode = {
                    "cost": costfn(child_edge, pn["cost"]),
                    "state": child.id(),
                    "parent": pn,
                    "edge": child_edge,
                }
                if (child.id() not in explored) or (
                    frontier.is_in(child, cmp_f=lambda x: x["state"]) is False
                ):
                    frontier.insert(cnode["cost"], cnode)
                elif frontier.is_in(child, cmp_f=lambda x: x["state"]) is True:
                    # node is already in frontier
                    ckey = frontier.key(child, f=lambda x: x["state"])
                    if ckey > cnode["cost"]:
                        frontier.insert(cnode["cost"], cnode, f=lambda x: x["state"])

    @classmethod
    def from_ucs_result(cls, ucs_solution):
        """!
        parse uniform cost search solution to create a path
        """
        edges = [ucs_solution["edge"]]
        while ucs_solution["parent"] is not None:
            ucs_solution = ucs_solution["parent"]
            edges.append(ucs_solution["edge"])
        edges.pop()  # last element edge is None
        edges = list(reversed(edges))
        return cls.from_edgelist(edges)

    @classmethod
    def from_ucs(
        cls,
        goal: Node,
        start: Node,
        problem_set: Set[Edge],
        filter_fn: Callable[[Set[Edge], str], Set[Edge]] = lambda es, n: set(
            [e for e in es if e.start().id() == n]
        ),
        costfn: Callable[[Edge, float], float] = lambda x, y: y + 1,
        is_min=True,
    ):
        ""
        ucs_solution = cls.uniform_cost_search(
            goal=goal,
            start=start,
            problem_set=problem_set,
            filter_fn=filter_fn,
            costfn=costfn,
            is_min=is_min,
        )
        return cls.from_ucs_result(ucs_solution)


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
