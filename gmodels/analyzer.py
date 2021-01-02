"""!
\file analyzer.py 
graph analyzer
"""
from typing import Set, Optional, Callable, List, Tuple
from graph import Graph
from node import Node


class GraphAnalyzer:
    """
    Analyze given graphs
    """

    def __init__(self):
        pass

    @staticmethod
    def is_disjoint(g1: Graph, g2: Graph) -> bool:
        "check if g2 is disjoint to g1"
        ns: Set[Node] = g1.nodes()
        ns_ = g2.vertex_intersection(ns)
        return len(ns_) == 0

    @staticmethod
    def is_proper_subgraph(g1: Graph, g2: Graph) -> bool:
        "check if g2 is subgraph of g1"
        ns: Set[Node] = g2.nodes()
        es: Set[Node] = g2.edges()
        contains_nodes: bool = g1.contains_vertices(ns)
        contains_edges: bool = g1.contains_edges(es)
        return contains_edges and contains_nodes

    @staticmethod
    def is_subgraph(g1: Graph, g2: Graph) -> bool:
        "check if g2 is subgraph of g1"
        # check vertex set includes
        # check edge set includes
        if g1 == g2:
            return True
        return GraphAnalyzer.is_proper_subgraph(g1, g2)

    @staticmethod
    def is_induced_subgraph(g1: Graph, g2: Graph) -> bool:
        """
        check if g2 is induced subgraph of g1
        induced subgraph:
        g2 \sub g1 ^ xy \in Edge[g1] with x,y Vertex[g2]
        """
        is_subgraph = GraphAnalyzer.is_subgraph(g1, g2)
        if not is_subgraph:
            return False
        g2_vertices = g2.nodes()
        g1_edges = g1.edges()
        for g1_edge in g1_edges:
            has_node_id1 = False
            has_node_id2 = False
            edge_node_ids = g1_edge.node_ids()
            edge_node_id1 = edge_node_ids[0]
            edge_node_id2 = edge_node_ids[1]
            for g2_vertex in g2_vertices:
                vertex_id = g2_vertex.id()
                if vertex_id == edge_node_id1:
                    has_node_id1 = True
                if vertex_id == edge_node_id2:
                    has_node_id2 = True
            #
            if not has_node_id1 and not has_node_id2:
                return False
        return True

    @staticmethod
    def is_spanning_subgraph(g1: Graph, g2: Graph) -> bool:
        "check if g2 is spanning subgraph of g1"
        if not GraphAnalyzer.is_subgraph(g1, g2):
            return False
        return g1.nodes() == g2.nodes()
