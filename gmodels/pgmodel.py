"""!
Probabilistic Graphic Model with Factors
"""
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.gtypes.node import Node
from gmodels.randomvariable import NumCatRVariable, NumericValue
from gmodels.factor import Factor
from gmodels.gtypes.graph import Graph
from typing import Callable, Set, List, Optional, Dict, Tuple
import math
from uuid import uuid4


class PGModel(Graph):
    ""

    def __init__(
        self,
        gid: str,
        nodes: Set[NumCatRVariable],
        edges: Set[Edge],
        factors: Optional[Set[Factor]] = None,
        data={},
    ):
        ""
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges)
        if factors is None:
            fs: Set[Factor] = set()
            for e in self.edges():
                estart = e.start()
                eend = e.end()
                sdata = estart.data()
                edata = eend.data()
                evidences = set()
                if "evidence" in sdata:
                    evidences.add((estart.id(), sdata["evidence"]))
                if "evidence" in edata:
                    evidences.add((eend.id(), edata["evidence"]))
                f = Factor(gid=str(uuid4()), scope_vars=set([estart, eend]))
                if len(evidences) != 0:
                    f.reduced_by_value(evidences)
                fs.add(f)
            self.Fs = fs
        else:
            self.Fs = factors

    def markov_blanket(self, t: NumCatRVariable) -> Set[NumCatRVariable]:
        """!
        get markov blanket of a node
        from K. Murphy, 2012, p. 662
        """
        if self.is_in(t) is False:
            raise ValueError("Node not in graph: " + str(t))
        ns: Set[NumCatRVariable] = self.neighbours_of(t)
        return ns

    def factors(self, f=lambda x: x):
        """!
        Get factors of graph
        """
        return set([f(ff) for ff in self.Fs])

    def closure_of(self, t: NumCatRVariable) -> Set[NumCatRVariable]:
        """!
        get closure of node 
        from K. Murphy, 2012, p. 662
        """
        return set([t]).union(self.markov_blanket(t))

    def is_conditionaly_independent_of(
        self, n1: NumCatRVariable, n2: NumCatRVariable
    ) -> bool:
        """!
        check if two nodes are conditionally independent
        from K. Murphy, 2012, p. 662
        """
        return self.is_node_independant_of(n1, n2)

    def scope_of(self, phi: Factor) -> Set[NumCatRVariable]:
        """!
        """
        return phi.scope_vars()

    def is_scope_subset_of(self, phi: Factor, X: Set[NumCatRVariable]) -> bool:
        """!
        filter factors using Koller, Friedman 2009, p. 299 as criteria
        """
        s = self.scope_of(phi)
        return s.intersection(X) == s

    def scope_subset_factors(self, X: Set[NumCatRVariable]) -> Set[Factor]:
        """!
        choose factors using Koller, Friedman 2009, p. 299 as criteria
        """
        return set([f for f in self.factors() if self.is_scope_subset_of(f, X) is True])

    def get_factor_product(self, fs: Set[Factor]):
        """!
        Multiply a set of factors.
        \f \prod_{i} \phi_i \f
        """
        factors = list(fs)
        if len(factors) == 1:
            return factors[0], None
        prod = factors.pop(0)
        for i in range(0, len(factors)):
            prod, val = prod.product(
                factors[i],
                product_fn=lambda x, y: x * y,
                accumulator=lambda x, y: x * y,
            )
        return prod, val

    def get_factor_product_var(
        self, fs: Set[Factor], Z: NumCatRVariable
    ) -> Tuple[Factor, Set[Factor], Set[Factor]]:
        """!
        Get products of factors whose scope involves variable Z.
        """
        factors = set([f for f in fs if Z in self.scope_of(f)])
        other_factors = set([f for f in fs if f not in factors])
        prod, v = self.get_factor_product(factors)
        return prod, set(factors), other_factors

    def sum_prod_var_eliminate(self, factors: Set[Factor], Z: NumCatRVariable):
        """!
        Koller and Friedman 2009, p. 298
        multiply factors and sum out the given variable
        \param factors factors that we are going to multiply
        \param Z variable that we are going to sum out, i.e. marginalize
        """
        (prod, scope_factors, other_factors) = self.get_factor_product_var(factors, Z)
        sum_factor = prod.sumout_var(Z)
        other_factors = other_factors.union({sum_factor})
        return other_factors

    def sum_product_elimination(
        self, factors: Set[Factor], Zs: List[NumCatRVariable]
    ) -> Factor:
        """!
        sum product variable elimination
        Koller and Friedman 2009, p. 298

        \param factors factor representation of our graph, it corresponds
        mostly to edges if other factors are not provided.

        \param Zs elimination variables. They correspond to all variables that
        are not query variables.
        """
        for Z in Zs:
            factors = self.sum_prod_var_eliminate(factors, Z)

        prod, v = self.get_factor_product(factors)
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

    def min_unmarked_neighbours(self, nodes, marked):
        """!
        find an unmarked node with minimum number of neighbours
        """
        ordered = [(n, self.nb_neighbours_of(n)) for n in nodes]
        ordered.sort(key=lambda x: x[1])
        for X, nb in sorted(ordered, key=lambda x: x[1]):
            if marked[X.id()] is False:
                return X
        return None

    def order_by_greedy_metric(
        self,
        nodes: Set[NumCatRVariable],
        s: Callable[[Graph, Dict[Node, bool]], Optional[Node]],
    ) -> Dict[str, int]:
        """!
        From Koller and Friedman 2009, p. 314
        """
        marked = {n.id(): False for n in nodes}
        cardinality = {n.id(): -1 for n in nodes}
        for i in range(len(nodes)):
            X = s(nodes, marked)
            if X is not None:
                cardinality[X.id()] = i
                TEMP = self.neighbours_of(X)
                while TEMP:
                    n_x = TEMP.pop()
                    for n in self.neighbours_of(X):
                        self.added_edge_between_if_none(n_x, n)
                marked[X.id()] = True
        return cardinality

    def reduce_factors_with_evidence(self, evidences: Set[Tuple[str, NumericValue]]):
        """!
        reduce factors if there is evidence
        """
        if len(evidences) == 0:
            return self.factors(), set()
        if any(e[0] not in self.V for e in evidences):
            raise ValueError("evidence set contains variables out of vertices of graph")
        E = set([self.V[e[0]] for e in evidences])
        fs = self.factors()
        factors = set([f.reduced_by_value(context=evidences) for f in fs])
        return factors, E

    def cond_prod_by_variable_elimination(
        self, queries: Set[NumCatRVariable], evidences: Set[Tuple[str, NumericValue]]
    ):
        """!
        Compute conditional probabilities with variable elimination
        from Koller and Friedman 2009, p. 304
        """
        if queries.issubset(self.nodes()) is False:
            raise ValueError("Query variables must be a subset of vertices of graph")
        factors, E = self.reduce_factors_with_evidence(evidences)
        Zs = set()
        for z in self.nodes():
            if z not in E and z not in queries:
                Zs.add(z)
        return self.conditional_prod_by_variable_elimination(queries, Zs, factors)

    def conditional_prod_by_variable_elimination(
        self,
        queries: Set[NumCatRVariable],
        Zs: Set[NumCatRVariable],
        factors: Set[Factor],
    ):
        """!
        Main conditional product by variable elimination function
        """
        cardinality = self.order_by_greedy_metric(
            nodes=Zs, s=self.min_unmarked_neighbours
        )
        ordering = [
            self.V[n[0]] for n in sorted(list(cardinality.items()), key=lambda x: x[1])
        ]
        phi = self.sum_product_elimination(factors=factors, Zs=ordering)
        alpha = phi.sumout_vars(queries)
        return phi, alpha

    def max_product_eliminate_var(
        self, factors: Set[Edge], Z: NumCatRVariable
    ) -> Tuple[Set[Factor], Factor]:
        """!
        from Koller and Friedman 2009, p. 557
        """
        prod_factor, scope_factors, other_factors = self.get_factor_product_var(
            fs=factors, Z=Z
        )
        max_factor = prod_factor.maxout_var(Z)
        return other_factors.union(max_factor), prod_factor

    def max_product_variable_elimination(
        self, factors: Set[Edge], Zs: List[NumCatRVariable]
    ):
        """!
        from Koller and Friedman 2009, p. 557
        """
        Z_potential = {}
        value_table = {Z.id(): None for Z in Zs}
        for i in range(len(Zs)):
            Z = Zs[i]
            factors, z_phi = self.max_product_eliminate_var(factors, Z=Z)
            Z_potential[Z.id()] = (z_phi, i)

    def traceback_map(
        self, potentials: Dict[str, Tuple[float, int]], Zs: List[NumCatRVariable]
    ):
        """!
        from Koller and Friedman 2009, p. 557
        The idea here is the following: 
        For the last variable eliminated, Z, the factor for the value x
        contains the probability of the most likely assignment that contains
        Z=x.
        """
