"""!
Path in a given graph
"""
import math
from typing import Callable, Dict, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pygmodels.gmodel.graph import Graph
from pygmodels.gtype.abstractobj import AbstractEdge, AbstractNode
from pygmodels.gtype.edge import Edge, EdgeType
from pygmodels.gtype.node import Node
from pygmodels.gtype.queue import PriorityQueue


class Path(Graph):
    """!
    path object as defined in Diestel 2017, p. 6
    """

    def __init__(self, gid: str, data={}, edges: List[Edge] = None):
        """"""
        flag, node_groups = Path.is_path(edges)
        if flag is False:
            raise ValueError("Can not construct a path with given edges")
        #
        super().__init__(
            gid=gid, data=data, nodes=node_groups["node_set"], edges=set(edges)
        )
        # starts path specific constructor

        self._node_list = node_groups["node_list"]
        self._edge_list = edges

    @classmethod
    def get_node_groups(
        cls, edges: Set[AbstractEdge]
    ) -> Dict[str, Union[List[AbstractNode], Set[AbstractNode]]]:
        """!
        Output nodes of the argument edges with different groupings
        """
        nodes = set()
        snodes = set()
        enodes = set()
        ns = [edges[0].start()]
        for e in edges:
            estart = e.start()
            snodes.add(estart)
            #
            eend = e.end()
            enodes.add(eend)
            #
            nodes.add(estart)
            nodes.add(eend)
            #
            if eend not in ns:
                ns.append(eend)
        #
        return {
            "node_list": ns,
            "node_set": nodes,
            "end_node_set": {n for n in enodes if n not in snodes},
            "start_node_set": set([n for n in snodes if n not in enodes]),
        }

    @classmethod
    def is_path(
        cls, edges: Set[AbstractEdge]
    ) -> Tuple[bool, Dict[str, Union[List[AbstractNode], Set[AbstractNode]]]]:
        """!
        Check if edge set meets necessary conditions to be a path
        """
        node_groups = cls.get_node_groups(edges=edges)
        # start nodes are those who are never end nodes
        starts = node_groups["start_node_set"]
        # end nodes are those who are never start nodes
        ends = node_groups["end_node_set"]

        # check if starts or ends have more than 2 elements
        # they should not.
        if len(starts) > 2:
            raise ValueError("Path should not have more than 2 start nodes")

        if len(ends) > 2:
            raise ValueError("Path should not have more than 2 end nodes")

        if len(starts) == 2 and len(ends) == 2:
            raise ValueError("Path can not have 2 start and end nodes")

        return True, node_groups

    @classmethod
    def get_start_end_node(
        cls, edges: Set[AbstractEdge]
    ) -> Tuple[bool, Optional[Dict[str, AbstractNode]]]:
        """"""
        flag, node_group = cls.is_path(edges)
        if flag is False:
            return False, None

        # start nodes are those who are never end nodes
        starts = node_group["start_node_set"]
        # end nodes are those who are never start nodes
        ends = node_group["end_node_set"]

        # the easy option that does not depend on any graph types
        if len(starts) == 1 and len(ends) == 1:
            start_node = starts.pop()
            end_node = ends.pop()
            return True, {"start": start_node, "end": end_node}
        return False, None

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
        """"""
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
                        frontier.insert(
                            cnode["cost"], cnode, f=lambda x: x["state"]
                        )

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
        """"""
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
        self,
        gid: str,
        data={},
        nodes: List[Node] = None,
        edges: List[Edge] = None,
    ):
        """"""
        super().__init__(gid, data, nodes, edges)
        vs = self.vertices()
        if vs[0] != vs[-1]:
            raise ValueError(
                "The first and last vertice of a cycle must be same"
            )
