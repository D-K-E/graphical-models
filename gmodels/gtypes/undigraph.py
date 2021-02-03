"""!
\file undigraph.py

# Undirected Graph Object

This file contains the implementation of an undirected graph object along
with some common algorithms. The methods that have a common name with the
parent class include in most cases a specific edge related function to pass
along to the parent's method in order to adapt its functionality.

"""
from typing import Set, List, Dict, Callable, Union
from gmodels.gtypes.edge import Edge
from gmodels.gtypes.node import Node
from gmodels.gtypes.tree import Tree
from gmodels.gtypes.abstractobj import EdgeType
from gmodels.gtypes.graph import Graph
from uuid import uuid4


class UndiGraph(Graph):
    """!
    \brief Unidrected graph whose edges are of type Undirected
    """

    def __init__(
        self, gid: str, data={}, nodes: Set[Node] = None, edges: Set[Edge] = None
    ):
        """!
        \brief constructor for undirected graph

        The general procedure is described in Graph constructor.
        The only procedure we apply here is to check that every 
        edge is indeed an undirected edge.

        \throws ValueError if a directed edge is found in the given edge set.
        """
        if edges is not None:
            for edge in edges:
                if edge.type() == EdgeType.DIRECTED:
                    raise ValueError(
                        "Can not instantiate undirected graph with" + " directed edges"
                    )
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges)

    @classmethod
    def from_graph(cls, g: Graph):
        """!
        \brief Construct an undirected graph from given graph.

        \throws ValueError if the graph contains a directed edge.

        \param g source graph
        """
        for e in g.edges():
            if e.type() == EdgeType.DIRECTED:
                raise ValueError("Graph contains directed edges")
        return UndiGraph(
            gid=str(uuid4()), data=g.data(), nodes=g.nodes(), edges=g.edges()
        )

    def find_shortest_paths(self, n1: Node) -> Dict[str, Union[dict, set]]:
        """!
        \brief Find shortest path between given node and all other nodes.

        This mostly the same function from Graph with the difference being the 
        edge generating function. We consider every edge that is incident with
        nodes not just incoming or outgoing edges.
        """
        return super().find_shortest_paths(n1=n1, edge_generator=self.edges_of)

    def check_for_path(self, n1: Node, n2: Node) -> bool:
        """!
        \brief check if there is a path between given two nodes

        \param n1 source node
        \param n2 destination node

        We search for the shortest paths that can be obtained from the source
        node. Since we obtain also a vertex set that are reachable from the 
        source node, if the node is inside the vertex set, we consider that
        there must be a path between source node and the destination node
        """
        paths = self.find_shortest_path(n1)
        n1_vertices = paths["path-set"]
        return n2 in n1_vertices

    def lower_bound_for_path_length(self) -> int:
        """!
        \brief also known as shortest possible path length
        see proof Diestel 2017, p. 8
        """
        return self.min_degree()

    def find_minimum_spanning_tree(
        self, weight_fn: Callable[[Edge], int] = lambda x: 1
    ):
        """!
        \brief Obtain the minimum spanning tree of the graph instance

        \param weight_fn weighting function used to extract weights from edges.

        We apply the generic weighted tree extraction algorithm from Tree.
        We consider that the graph is evenly weighted, however if this is not
        the case the weighting function can be used for determining weight of
        each edge.
        """
        # t = Tree.find_mst_prim(self, edge_generator=self.edges_of)
        t, L = Tree.find_mnmx_st(
            self, edge_generator=self.edges_of, weight_function=weight_fn
        )
        return t, L

    def find_maximum_spanning_tree(self, weight_fn=lambda x: 1):
        """!
        \brief obtain maximum weight spanning tree from graph.

        \see find_minimum_spanning_tree()

        \param weight_fn weighting function for edges.
        """
        # t = Tree.find_mst_prim(self, edge_generator=self.edges_of)
        t, L = Tree.find_mnmx_st(
            self, edge_generator=self.edges_of, weight_function=weight_fn, is_min=False
        )
        return t, L

    def find_articulation_points(self) -> Set[Node]:
        """!
        \brief find articulation points in the given graph instance

        Applies the parent's Graph.find_articulation_points() function with
        a different graph making function.
        \see Graph.find_articulation_points() for more information
        """
        gmaker = lambda x: self.from_graph(self.subtract_node(x))
        return super().find_articulation_points(graph_maker=gmaker)

    def find_bridges(self) -> Set[Node]:
        """!
        \brief find bridges in the given graph instance

        Applies the parent's Graph.find_bridges() function with
        a different graph making function.
        \see Graph.find_bridges() for more information
        """
        gmaker = lambda x: self.from_graph(self.subtract(x))
        return super().find_bridges(graph_maker=gmaker)

    def bron_kerbosch(
        self, P: Set[Node], R: Set[Node], X: Set[Node], Cs: List[Set[Node]]
    ):
        """!
        \brief apply bron kerbosch algorithm for finding maximal cliques

        Code taken from: arxiv.org/1006.5440
        \code
        proc BronKerbosch(P,R,X)
        1: if P∪X = empty then
        2:   report R as a maximal clique
        3: end if
        4: for each vertex v∈P do
        5:   BronKerbosch(P ∩ Neigbours(v), R ∪ {v}, X ∩ Neighbours(v))
        6:   P←P\{v}
        7:   X←X∪{v}
        8: end for
        \endcode
        """
        if len(P.union(X)) == 0:
            Cs.append(R)
        for v in P:
            self.bron_kerbosch(
                P=P.intersection(self.neighbours_of(v)),
                R=R.union([v]),
                X=X.intersection(self.neighbours_of(v)),
                Cs=Cs,
            )
            P = P.difference([v])
            X = X.union([v])

    def find_maximal_cliques(self):
        """!
        find maximal cliques in graph using Bron Kerbosch algorithm
        as per arxiv.org/1006.5440
        """
        P: Set[Node] = self.nodes()
        X: Set[Node] = set()
        R: Set[Node] = set()
        Cs: List[Set[Node]] = []
        self.bron_kerbosch(P, R, X, Cs)
        return Cs
