"""
Undirected graph object
"""
from typing import Set, Optional, Callable, List, Tuple
from edge import Edge
from node import Node
from info import NodeInfo, SNodeInfo
from path import Path, Cycle
from abstractobj import EdgeType
from graph import Graph
from uuid import uuid4
import math


class UndirectedGraph(Graph):
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

    def is_node_incident(self, n: Node, e: Edge) -> bool:
        ""
        einfo = e.edge_info()
        return n.is_incident(info=einfo)

    def is_neighbour_of(self, n1: Node, n2: Node) -> bool:
        ""
        n1_edge_ids = n1.edge_ids()
        n2_edge_ids = n2.edge_ids()
        return len(n1_edge_ids.intersection(n2_edge_ids)) > 0

    def is_adjacent_of(self, e1: Edge, e2: Edge) -> bool:
        ""
        n1_ids = e1.node_ids()
        n2_ids = e2.node_ids()
        return len(n1_ids.intersection(n2_ids)) > 0

    def is_node_independant_of(self, n1: Node, n2: Node) -> bool:
        return not self.is_neighbour_of(n1, n2)

    def is_stable(self, ns: Set[Node]) -> bool:
        ""
        node_list = list(ns)
        while node_list:
            n1 = node_list.pop()
            for n2 in node_list:
                if self.is_neighbour_of(n1=n1, n2=n2):
                    return False
        return True

    def neighbours_of(self, n1: Node) -> Set[Node]:
        ""
        neighbours = set()
        for n2 in self.nodes():
            if self.is_neighbour_of(n1=n1, n2=n2):
                neighbours.add(n2)
        return neighbours

    def edges_of(self, n: Node) -> Set[Edge]:
        ""
        edge_ids = n.edge_ids()
        edges = set()
        for edge in self.edges():
            if edge.id() in edge_ids:
                edges.add(edge)
        return edges

    def traverse_search_nodes(self, snode: dict, nlist: List[Node], elist: List[Node]):
        ""
        if snode["parent"] is None:
            nlist.append(snode["state"])
            return
        #
        nlist.append(snode["state"])
        elist.append(self.edge_by_id(snode["edge-id"]))
        self.traverse_search_nodes(snode["parent"], nlist, elist)

    def extract_path_from_search_node(self, search_node: dict) -> Path:
        ""
        nodelist: List[Node] = []
        edgelist: List[Edge] = []
        self.traverse_search_nodes(search_node, nlist=nodelist, elist=edgelist)
        if not edgelist:
            edgelist = None
        return Path(gid=str(uuid4()), nodes=nodelist, edges=edgelist)

    def find_shortest_path(self, n1: Node, n2: Node) -> Path:
        """
        find path between two nodes using uniform cost search
        """
        if not self.is_in(n1):
            raise ValueError("first node is not inside this graph")
        if not self.is_in(n2):
            raise ValueError("second node is not inside this graph")
        if n1 == n2:
            nset = [n1]
            return Path(gid=str(uuid4()), nodes=nset, edges=None)
        search_node = {"state": n1, "cost": 0, "parent": None, "edge-id": None}
        explored = set()
        frontier = [search_node]
        while frontier:
            explored_search_node = frontier.pop()
            explored_state = explored_search_node["state"]
            explored_id = explored_state.id()
            if explored_id == n2.id():
                return self.extract_path_from_search_node(explored_search_node)
            #
            explored.add(explored_id)
            path_cost = explored_search_node["cost"]
            for neighbour in self.neighbours_of(explored_state):
                parent_edge = self.edge_by_vertices(explored_state, neighbour)
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
        return

    def check_for_path(self, n1: Node, n2: Node) -> bool:
        "check if there is a path between nodes"
        return self.find_shortest_path(n1, n2) is not None

    def shortest_path_length(self) -> int:
        "see proof Diestel p. 8"
        return self.min_degree()

    def has_cycle(self):
        "see Diestel p. 8"
        return self.shortest_path_length() >= 2

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

    def find_cycle(self, n: Node) -> Cycle:
        """!
        Find if given node can make a cycle using depth first search
        """
        # TODO finish this algorithm the main idea is search node contains
        # visit info.
        if not self.is_in(n):
            raise ValueError("node not in graph")
        search_node = {"state": n, "parent": None, "edge-id": None, "visited": -1}
        explored = set()
        frontier = [search_node]
        while frontier:
            explored_search_node = frontier.pop()
            explored_state = explored_search_node["state"]
            explored_id = explored_state.id()
            if explored_id == n.id() and explored_search_node["visited"] == 1:
                # found the cycle
                path = self.extract_path_from_search_node(explored_search_node)
                return Cycle(
                    gid=path.id(),
                    data=path.data(),
                    nodes=path.vertices(),
                    edges=path._edge_list,
                )
            #
            explored.add((explored_id, explored_search_node["visited"]))
            for neighbour in self.neighbours_of(explored_state):
                parent_edge = self.edge_by_vertices(explored_state, neighbour)
                child_search_node = {
                    "state": neighbour,
                    "parent": explored_search_node,
                    "edge-id": parent_edge,
                }
                child_id = child_search_node["state"].id()
                if (child_id not in explored) and (
                    not any(
                        [
                            front_node["state"].id() == child_id
                            for front_node in frontier
                        ]
                    )
                ):
                    #
                    frontier.append(child_search_node)
        #
        return
