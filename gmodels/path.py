"""!
Path in a given graph
"""
from typing import Set, Optional, Callable, List, Tuple
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

    def vertices(self):
        "get vertice list"
        if self._node_list is None or len(self._node_list) == 0:
            raise ValueError("there are no vertices in the path")
        return self._node_list

    def endvertices(self) -> Tuple[Node, Node]:
        ""
        vs = self.vertices()
        if len(vs) == 1:
            return (vs[0], vs[0])
        return (vs[0], vs[-1])

    @staticmethod
    def traverse_search_nodes(
        g: Graph, snode: dict, nlist: List[Node], elist: List[Edge]
    ):
        ""
        if snode["parent"] is None:
            nlist.append(snode["state"])
            return
        #
        nlist.append(snode["state"])
        elist.append(g.edge_by_id(snode["edge-id"]))
        Path.traverse_search_nodes(g, snode["parent"], nlist, elist)

    @staticmethod
    def extract_path_from_search_node(
        g: Graph, search_node: dict
    ) -> Tuple[List[Node], Optional[List[Edge]]]:
        ""
        nodelist: List[Node] = []
        edgelist: List[Edge] = []
        Path.traverse_search_nodes(g, search_node, nlist=nodelist, elist=edgelist)
        if not edgelist:
            edgelist = None
        return (nodelist, edgelist)

    @staticmethod
    def find_shortest_path(
        g: Graph, n1: Node, n2: Node, generative_fn: Callable[[Node], Set[Node]]
    ) -> Optional[Tuple[List[Node], Optional[List[Edge]]]]:
        """
        find path between two nodes using uniform cost search
        """
        if not self.is_in(n1):
            raise ValueError("first node is not inside this graph")
        if not self.is_in(n2):
            raise ValueError("second node is not inside this graph")
        if n1 == n2:
            nset = [n1]
            return (nset, None)
        search_node = {"state": n1, "cost": 0, "parent": None, "edge-id": None}
        explored = set()
        frontier = [search_node]
        while frontier:
            explored_search_node = frontier.pop()
            explored_state = explored_search_node["state"]
            explored_id = explored_state.id()
            if explored_id == n2.id():
                return Path.extract_path_from_search_node(g, explored_search_node)
            #
            explored.add(explored_id)
            path_cost = explored_search_node["cost"]
            for neighbour in generative_fn(explored_state):
                parent_edge = g.edge_by_vertices(explored_state, neighbour)
                ncost = path_cost + 1
                child_search_node = {
                    "state": neighbour,
                    "cost": ncost,
                    "parent": explored_search_node,
                    "edge-id": parent_edge,
                }
                child_id = child_search_node["state"].id()
                if (child_id not in explored) and (
                    all(
                        [
                            front_node["state"].id() != child_id
                            for front_node in frontier
                        ]
                    )
                ):
                    #
                    frontier.append(child_search_node)
                    frontier.sort(key=lambda x: x["cost"])
                elif any(
                    [child_id == front_node["state"].id() for front_node in frontier]
                ):
                    frontcp = frontier.copy()
                    for i, snode in enumerate(frontcp):
                        snode_id = snode["state"].id()
                        if snode_id == child_id:
                            if snode["cost"] > child_search_node["cost"]:
                                frontier[i] = child_search_node
        #
        return None

    @classmethod
    def from_graph_nodes(
        cls, g: Graph, n1: Node, n2: Node, generative_fn: Callable[[Node], Set[Node]]
    ):
        """!
        construct path from graph and nodes
        """
        res = Path.find_shortest_path(g, n1, n2, generative_fn)
        if res is None:
            raise ValueError("can not create path with these parameters")
        nodelist, edgelist = res
        return Path(gid=str(uuid4()), data={}, nodes=nodelist, edges=edgelist)


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
