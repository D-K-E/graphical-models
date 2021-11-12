"""!
Path in a given graph
"""
import math
from typing import Callable, Dict, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pygmodels.graph.graphops.graphsearcher import BaseGraphSearcher
from pygmodels.graph.gtype.abstractobj import (
    AbstractEdge,
    AbstractNode,
    AbstractPath,
)
from pygmodels.graph.gtype.basegraph import BaseGraph
from pygmodels.graph.gtype.queue import PriorityQueue


class Path(BaseGraph, AbstractPath):
    """!
    path object as defined in Diestel 2017, p. 6
    """

    def __init__(self, gid: str, data={}, edges: List[AbstractEdge] = None):
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
        starts = node_groups["start_node_set"]
        ends = node_groups["end_node_set"]
        evertices = []
        if len(starts) == 2:
            s1 = starts.pop()
            s2 = starts.pop()
            evertices = [s1, s2]
        elif len(ends) == 2:
            s1 = ends.pop()
            s2 = ends.pop()
            evertices = [s1, s2]
        elif len(starts) == 1 and len(ends) == 1:
            s1 = starts.pop()
            s2 = ends.pop()
            evertices = [s1, s2]
        else:
            raise ValueError(
                "Start and End node sets do not permit construction of end vertices"
            )
        self._end_vertices = evertices

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
    def from_edgelist(cls, edges: List[AbstractEdge]):
        """!
        create path from edge list
        """
        return Path(gid=str(uuid4()), edges=edges)

    def length(self) -> int:
        """!
        \brief number of edges inside the path, see Diestel 2017, p. 6
        """
        return len(self.E)

    def node_list(self) -> List[AbstractNode]:
        "get vertice list"
        if self._node_list is None or len(self._node_list) == 0:
            raise ValueError("there are no vertices in the path")
        return self._node_list

    def endvertices(self) -> Tuple[AbstractNode, AbstractNode]:
        """"""
        return tuple(self._end_vertices)

    @classmethod
    def from_ucs(
        cls,
        g: AbstractPath,
        goal: AbstractNode,
        start: AbstractNode,
        filter_fn: Callable[
            [Set[AbstractEdge], str], Set[AbstractEdge]
        ] = lambda es, n: set([e for e in es if e.start().id() == n]),
        costfn: Callable[[AbstractEdge, float], float] = lambda x, y: y + 1,
        is_min=True,
        problem_set=None,
    ) -> AbstractPath:
        """"""
        elist, pn = BaseGraphSearcher.uniform_cost_search(
            goal=goal,
            start=start,
            g=g,
            filter_fn=filter_fn,
            costfn=costfn,
            is_min=is_min,
            problem_set=problem_set,
        )
        return cls.from_edgelist(elist)


class Cycle(Path):
    """!
    Cycle as defined in Diestel p. 8
    """

    def __init__(
        self,
        gid: str,
        data={},
        nodes: List[AbstractNode] = None,
        edges: List[AbstractEdge] = None,
    ):
        """"""
        super().__init__(gid, data, nodes, edges)
        vs = self.node_list()
        if vs[0] != vs[-1]:
            raise ValueError(
                "The first and last vertice of a cycle must be same"
            )
