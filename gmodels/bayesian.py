"""!
Bayesian Network model
"""

from gmodels.gtypes.digraph import DiGraph
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.randomvariable import NumCatRVariable
from typing import Callable, Set, Any, List
import math
from uuid import uuid4


class BayesianNetwork(DiGraph):
    """!
    bayesian network implementation
    """

    def __init__(
        self, gid: str, nodes: Set[NumCatRVariable], edges: Set[Edge], data={}
    ):
        ""
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges)

    #
    def cond2(self, X: NumCatRVariable, Y: NumCatRVariable) -> float:
        """!
        get joint probability distribution: Koller, Friedman 2009, p. 31
        p(X|Y) = P(Y, X) / P(Y)
        """
        return X.conditional(Y)

    def cond3(
        self, X: NumCatRVariable, Y: NumCatRVariable, Z: NumCatRVariable
    ) -> float:
        """!
        get joint probability distribution: Koller, Friedman 2009, p. 24
        p(X, Y | Z) = P(X | Z) P(Y | Z)
        """
        return X.conditional(Z) * Y.conditional(Z)

    def scope_of(self, phi_X_i: Edge) -> Set[NumCatRVariable]:
        """!
        """
        return set([phi_X_i.start(), phi_X_i.end()])

    def order_by_max_cardinality(self, nodes: Set[NumCatRVariable]):
        """!
        from Koller and Friedman 2009, p. 312
        """
        marked = {n.id(): False for n in nodes}
        cardinality = {n.id(): -1 for n in nodes}
        unmarked_node_with_largest_marked_neighbor = None
        nb_marked_neighbours = float("-inf")
        for i in range(len(nodes)):
            for n in nodes:
                if marked[n.id()] is True:
                    continue
                nb_marked_neighbours_counter = 0
                for n_ in self.neighbours_of(n):
                    if marked[n_.id()] is False:
                        nb_marked_neighbours_counter += 1
                #
                if nb_marked_neighbours_counter > nb_marked_neighbours:
                    nb_marked_neighbours = nb_marked_neighbours_counter
                    unmarked_node_with_largest_marked_neighbor = n
            #
            cardinality[n.id()] = i
            marked[n.id()] = True
        #
        return cardinality

    def add_moral_edges(self, n: NumCatRVariable):
        """!
        add moral edges nodes that has common children but no edge with
        argument
        """
        n_children = self.children_of(n)
        for node in self.nodes():
            if len(self.children_of(node).intersection(n_children)) > 0:
                try:
                    es = self.edge_by_vertices(n1=n, n2=node)
                except ValueError:
                    e = Edge(
                        edge_id=str(uuid4()),
                        edge_type=EdgeType.UNDIRECTED,
                        start_node=n,
                        end_node=node,
                    )
                    self.add_edge_to_self(e)
        return

    def moralize(self):
        """!
        from Sucar 2015, p. 121 - 122
        """
        for v in self.V.copy():
            self.add_moral_edges(self.V[v])

    def junction_tree(self):
        """!
        from Sucar 2015, p. 121-122
        """
        undir_edges = set()
        for e in self.edges():
            e.set_type(EdgeType.UNDIRECTED)
            undir_edges.add(e)

        node_order = self.order_by_max_cardinality(self.nodes())
