"""!
Probabilistic Graph Model, a general model for inference
"""
from gmodels.gtypes.undigraph import UndiGraph
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.randomvariable import NumCatRVariable
from typing import Callable, Set, List, Optional
import math
from uuid import uuid4


class PGModel(UndiGraph):
    def __init__(
        self, gid: str, nodes: Set[NumCatRVariable], edges: Set[Edge], data={}
    ):
        ""
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges)

    def factor(self, f: Edge):
        """!
        """
        Pa_X = f.start()
        X = f.end()
        return X.conditional(Pa_X)

    def scope_of(self, phi_X_i: Edge) -> Set[NumCatRVariable]:
        """!
        """
        return set([phi_X_i.start(), phi_X_i.end()])

    def get_factor_product(self, fs: Set[Edge], Z: NumCatRVariable):
        """!
        """
        factors = set([f for f in fs if Z in self.scope_of(f)])
        other_factors = set([f for f in fs if f not in factors])
        prod = 1.0
        for potential in factors:
            pdata = potential.data()
            if "factor" in pdata:
                prod *= pdata["factor"]
            else:
                prod *= self.factor(potential)
        return prod, factors, other_factors

    def merge_factors(self, val: float, fs: Set[Edge], ofs: Set[Edge]):
        """!
        Koller and Friedman 2009, p. 298
        Bottom part of the algorithm
        """
        for f in fs:
            fdata = f.data()
            fdata["factor"] = val

        ofs = ofs.union(fs)
        return ofs

    def sum_prod_var_eliminate(self, factors: Set[Edge], Z: NumCatRVariable):
        """!
        Koller and Friedman 2009, p. 298
        """
        (prod, scope_factors, other_factors) = self.get_factor_product(factors, Z)
        marginal_over = Z.P_X_e() * prod
        return self.merge_factors(marginal_over, scope_factors, other_factors)

    def sum_product_elimination(self, factors: Set[Edge], Zs: List[NumCatRVariable]):
        """!
        sum product variable elimination
        Koller and Friedman 2009, p. 298
        """
        for Z in Zs:
            factors = self.sum_prod_var_eliminate(factors, Z)
        prod = 1.0
        for f in factors:
            prod *= f.data()["factor"]
        return prod

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

    def min_unmarked_neighbours(self, g, marked):
        """!
        find an unmarked node with minimum number of neighbours
        """
        ordered = [(n, self.nb_neighbours_of(n)) for n in g.nodes()]
        ordered.sort(key=lambda x: x[1])
        for X, nb in ordered:
            if marked[X.id()] is False:
                return X
        return None

    def order_by_greedy_metric(
        self,
        nodes: Set[NumCatRVariable],
        s: Callable[[Graph, Dict[Node, bool]], Optional[Node]],
    ):
        """!
        From Koller and Friedman 2009, p. 314
        """
        marked = {n.id(): False for n in nodes}
        cardinality = {n.id(): -1 for n in nodes}
        for i in range(len(nodes)):
            X = s(self, marked)
            if X is not None:
                cardinality[X.id()] = i
                TEMP = self.neighbours_of(X)
                while TEMP:
                    n_x = TEMP.pop()
                    for n in self.neighbours_of(X):
                        self.added_edge_between_if_none(n_x, n)
                marked[X.id()] = True
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
        #
        g = self.to_undirected()
        return g

    def junction_tree(self):
        """!
        from Sucar 2015, p. 121-122
        """
        undir_edges = set()
        for e in self.edges():
            e.set_type(EdgeType.UNDIRECTED)
            undir_edges.add(e)

        node_order = self.order_by_max_cardinality(self.nodes())
