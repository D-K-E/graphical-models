"""
"""

from pygmodels.pgm.pgmtype.pgmodel import PGModel
from pygmodels.graph.graphops.graphops import (
    BaseGraphBoolOps,
    BaseGraphEdgeOps,
    BaseGraphNodeOps,
    BaseGraphOps,
)
import math
from typing import Callable, Dict, List, Optional, Set, Tuple
from uuid import uuid4

from pygmodels.factor.factorfunc.factoralg import FactorAlgebra
from pygmodels.factor.factorfunc.factoranalyzer import FactorAnalyzer
from pygmodels.factor.factorfunc.factorops import FactorOps
from pygmodels.factor.factortype.abstractfactor import AbstractFactor
from pygmodels.factor.factortype.basefactor import BaseFactor
from pygmodels.graph.ganalysis.graphanalyzer import (
    BaseGraphAnalyzer,
    BaseGraphBoolAnalyzer,
    BaseGraphNodeAnalyzer,
    BaseGraphNumericAnalyzer,
)
from pygmodels.graph.graphmodel.graph import Graph
from pygmodels.graph.graphops.graphalg import BaseGraphAlgOps
from pygmodels.graph.graphops.graphops import (
    BaseGraphBoolOps,
    BaseGraphEdgeOps,
    BaseGraphNodeOps,
    BaseGraphOps,
)
from pygmodels.graph.graphtype.edge import Edge
from pygmodels.graph.graphtype.node import Node
from pygmodels.pgm.pgmtype.randomvariable import NumCatRVariable, NumericValue

from pygmodels.pgm.pgmtype.randomvariable import NumCatRVariable, NumericValue
from pygmodels.factor.factorfunc.factoralg import FactorAlgebra
from pygmodels.utils import is_type, is_all_type
from types import FunctionType
from typing import List, Tuple, Dict, List, Set
from copy import deepcopy


def min_unmarked_neighbours(g: Graph, nodes: Set[Node], marked: Dict[str, Node]):
    """!
    \brief find an unmarked node with minimum number of neighbours
    """
    ordered = [(n, BaseGraphNumericAnalyzer.nb_neighbours_of(g, n)) for n in nodes]
    ordered.sort(key=lambda x: x[1])
    for X, nb in sorted(ordered, key=lambda x: x[1]):
        if marked[X.id()] is False:
            return X
    return None


class PGMOps:
    """"""

    @staticmethod
    def markov_blanket(g: PGModel, t: NumCatRVariable) -> Set[NumCatRVariable]:
        """!
        get markov blanket of a node from K. Murphy, 2012, p. 662
        """
        if BaseGraphBoolOps.is_in(g, t) is False:
            raise ValueError("Node not in graph: " + str(t))
        ns: Set[NumCatRVariable] = BaseGraphNodeOps.neighbours_of(g, t)
        return ns

    @staticmethod
    def factors(g: PGModel, f=lambda x: x):
        """!
        Get factors of graph
        """
        is_type(g, "g", PGModel, True)
        is_type(f, "f", FunctionType, True)
        return set([f(ff) for ff in g.Fs])

    @staticmethod
    def closure_of(g: PGModel, t: NumCatRVariable) -> Set[NumCatRVariable]:
        """!
        get closure of node
        from K. Murphy, 2012, p. 662
        """
        return set([t]).union(PGMOps.markov_blanket(g, t))

    @staticmethod
    def is_conditionaly_independent_of(
        g: PGModel, n1: NumCatRVariable, n2: NumCatRVariable
    ) -> bool:
        """!
        check if two nodes are conditionally independent
        from K. Murphy, 2012, p. 662
        """
        return BaseGraphBoolAnalyzer.is_node_independent_of(g, n1, n2)

    @staticmethod
    def scope_of(g: PGModel, phi: AbstractFactor) -> Set[NumCatRVariable]:
        """!"""
        is_type(g, "g", PGModel, True)
        is_type(phi, "phi", AbstractFactor, True)
        return phi.scope_vars()

    @staticmethod
    def is_scope_subset_of(
        g: PGModel, phi: BaseFactor, X: Set[NumCatRVariable]
    ) -> bool:
        """!
        filter factors using Koller, Friedman 2009, p. 299 as criteria
        """
        is_all_type(X, "X", NumCatRVariable, True)
        s: Set[NumCatRVariable] = PGMOps.scope_of(g, phi)
        return s.intersection(X) == s

    @staticmethod
    def scope_subset_factors(g: PGModel, X: Set[NumCatRVariable]) -> Set[BaseFactor]:
        """!
        choose factors using Koller, Friedman 2009, p. 299 as criteria
        """
        return set(
            [f for f in PGMOps.factors(g) if PGMOps.is_scope_subset_of(g, f, X) is True]
        )

    @staticmethod
    def get_factor_product(g: PGModel, fs: Set[BaseFactor]):
        """!
        Multiply a set of factors.
        \f \prod_{i} \phi_i \f
        """
        is_all_type(fs, "fs", BaseFactor, True)
        factors = list(fs)
        if len(factors) == 0:
            raise ValueError("Must have a non empty list of factors")
        if len(factors) == 1:
            return factors[0], None
        prod = factors.pop(0)
        for i in range(0, len(factors)):
            prod, val = FactorAlgebra.product(
                f=prod,
                other=factors[i],
                product_fn=lambda x, y: x * y,
                accumulator=lambda x, y: x * y,
            )
        return prod, val

    @staticmethod
    def get_factor_product_var(
        g: PGModel, fs: Set[BaseFactor], Z: NumCatRVariable
    ) -> Tuple[BaseFactor, Set[BaseFactor], Set[BaseFactor]]:
        """!
        Get products of factors whose scope involves variable Z.
        """
        is_all_type(fs, "fs", BaseFactor, True)
        is_type(Z, "Z", NumCatRVariable, True)
        factors = set([f for f in fs if Z in PGMOps.scope_of(g, f)])
        other_factors = set([f for f in fs if f not in factors])
        prod, v = PGMOps.get_factor_product(g, factors)
        return prod, set(factors), other_factors

    @staticmethod
    def eliminate_variable_by(
        g: PGModel,
        factors: Set[BaseFactor],
        Z: NumCatRVariable,
        elimination_strategy=lambda x, y: x.sumout_var(y),
    ) -> Tuple[set, BaseFactor, float]:
        """!
        eliminate variables using given strategy. Unites max product and sum
        product
        """
        is_type(elimination_strategy, "elimination_strategy", FunctionType, True)
        (prod, scope_factors, other_factors) = PGMOps.get_factor_product_var(
            g, factors, Z
        )
        sum_factor = elimination_strategy(prod, Z)
        other_factors = other_factors.union({sum_factor})
        return other_factors, sum_factor, prod

    @staticmethod
    def sum_prod_var_eliminate(
        g: PGModel, factors: Set[BaseFactor], Z: NumCatRVariable
    ) -> Set[NumCatRVariable]:
        """!
        Koller and Friedman 2009, p. 298
        multiply factors and sum out the given variable
        \param factors factors that we are going to multiply
        \param Z variable that we are going to sum out, i.e. marginalize
        """
        res = PGMOps.eliminate_variable_by(
            g=g,
            factors=factors,
            Z=Z,
            elimination_strategy=lambda x, y: FactorAlgebra.sumout_var(x, y),
        )
        return res[0]

    @staticmethod
    def sum_product_elimination(
        g: PGModel, factors: Set[BaseFactor], Zs: List[NumCatRVariable]
    ) -> BaseFactor:
        """!
        sum product variable elimination
        Koller and Friedman 2009, p. 298

        \param factors factor representation of our graph, it corresponds
        mostly to edges if other factors are not provided.

        \param Zs elimination variables. They correspond to all variables that
        are not query variables.
        """
        is_all_type(Zs, "Zs", NumCatRVariable, True)
        for Z in Zs:
            nfactors = PGMOps.sum_prod_var_eliminate(g, factors, Z)

        prod, v = PGMOps.get_factor_product(g, nfactors)
        return prod

    @staticmethod
    def order_by_max_cardinality(
        g: PGModel, nodes: Set[NumCatRVariable]
    ) -> Dict[str, int]:
        """!
        from Koller and Friedman 2009, p. 312
        """
        is_all_type(nodes, "nodes", NumCatRVariable, True)
        marked = {n.id(): False for n in nodes}
        cardinality = {n.id(): -1 for n in nodes}
        unmarked_node_with_largest_marked_neighbor = None
        nb_marked_neighbours = float("-inf")
        for i in range(len(nodes)):
            for n in nodes:
                if marked[n.id()] is True:
                    continue
                nb_marked_neighbours_counter = 0
                for n_ in BaseGraphNodeOps.neighbours_of(g, n):
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

    @staticmethod
    def order_by_greedy_metric(
        g: PGModel,
        nodes: Set[NumCatRVariable],
        s: Callable[
            [Graph, Dict[Node, bool]], Optional[Node]
        ] = min_unmarked_neighbours,
    ) -> Dict[str, int]:
        """!
        From Koller and Friedman 2009, p. 314
        """
        is_type(g, "g", PGModel, True)
        is_all_type(nodes, "nodes", NumCatRVariable, True)
        is_type(s, "s", FunctionType, True)

        ng = g.copy()
        marked = {n.id(): False for n in nodes}
        cardinality = {n.id(): -1 for n in nodes}
        for i in range(len(nodes)):
            X = s(g=ng, nodes=nodes, marked=marked)
            if X is not None:
                cardinality[X.id()] = i
                TEMP = BaseGraphNodeOps.neighbours_of(ng, X)
                while TEMP:
                    n_x = TEMP.pop()
                    for n in BaseGraphNodeOps.neighbours_of(ng, X):
                        ng = BaseGraphAlgOps.added_edge_between_if_none(
                            ng, n_x, n, is_directed=False
                        )
                marked[X.id()] = True
        return cardinality

    @staticmethod
    def reduce_queries_with_evidence(
        g: PGModel,
        queries: Set[NumCatRVariable],
        evidences: Set[Tuple[str, NumericValue]],
    ) -> Set[NumCatRVariable]:
        """"""
        is_all_type(queries, "queries", NumCatRVariable, True)
        is_all_type(evidences, "evidences", tuple, True)
        reduced_queries = set()
        evs = {e[0]: e[1] for e in evidences}
        nqueries = deepcopy(queries)
        for q in nqueries:
            if q.id() in evs:
                ev = evs[q.id()]
                q.reduce_to_value(ev)
            reduced_queries.add(q)
        return reduced_queries

    @staticmethod
    def reduce_factors_with_evidence(
        g: PGModel, evidences: Set[Tuple[str, NumericValue]]
    ) -> Tuple[Set[BaseFactor], Set[NumCatRVariable]]:
        """!
        reduce factors if there is evidence
        """
        is_all_type(evidences, "evidences", tuple, True)
        is_type(g, "g", PGModel, True)
        if len(evidences) == 0:
            return PGMOps.factors(g), set()
        if any(e[0] not in {v.id() for v in g.V} for e in evidences):
            raise ValueError("evidence set contains variables out of vertices of graph")
        elist = [e[0] for e in evidences]
        E = set([v for v in g.V if v.id() in elist])
        fs = PGMOps.factors(g)
        factors = set(
            [FactorAlgebra.reduced_by_value(f, assignments=evidences) for f in fs]
        )
        return factors, E

    @staticmethod
    def cond_prod_by_variable_elimination(
        g: PGModel,
        queries: Set[NumCatRVariable],
        evidences: Set[Tuple[str, NumericValue]],
        ordering_fn=min_unmarked_neighbours,
    ):
        """!
        Compute conditional probabilities with variable elimination
        from Koller and Friedman 2009, p. 304
        """
        is_type(g, "g", PGModel, True)
        if queries.issubset(g.V) is False:
            raise ValueError("Query variables must be a subset of vertices of graph")
        queries = PGMOps.reduce_queries_with_evidence(g, queries, evidences)
        factors, E = PGMOps.reduce_factors_with_evidence(g, evidences)
        Zs = set()
        for z in g.V:
            if z not in E and z not in queries:
                Zs.add(z)
        return PGMOps.conditional_prod_by_variable_elimination(
            g=g, queries=queries, Zs=Zs, factors=factors, ordering_fn=ordering_fn
        )

    @staticmethod
    def conditional_prod_by_variable_elimination(
        g: PGModel,
        queries: Set[NumCatRVariable],
        Zs: Set[NumCatRVariable],
        factors: Set[AbstractFactor],
        ordering_fn=min_unmarked_neighbours,
    ) -> Tuple[AbstractFactor, AbstractFactor]:
        """!
        Main conditional product by variable elimination function
        """
        cardinality = PGMOps.order_by_greedy_metric(g=g, nodes=Zs, s=ordering_fn)
        V = {v.id(): v for v in g.V}
        ordering = [
            V[n[0]] for n in sorted(list(cardinality.items()), key=lambda x: x[1])
        ]
        phi = PGMOps.sum_product_elimination(g=g, factors=factors, Zs=ordering)
        alpha = FactorAlgebra.sumout_vars(phi, queries)
        return phi, alpha

    @staticmethod
    def max_product_eliminate_var(
        g: PGModel, factors: Set[Edge], Z: NumCatRVariable
    ) -> Tuple[Set[AbstractFactor], AbstractFactor]:
        """!
        from Koller and Friedman 2009, p. 557
        """
        return PGMOps.eliminate_variable_by(
            g=g,
            factors=factors,
            Z=Z,
            elimination_strategy=lambda x, y: FactorAlgebra.maxout_var(x, y),
        )

    @staticmethod
    def max_product_eliminate_vars(
        g: PGModel, factors: Set[Edge], Zs: List[NumCatRVariable]
    ):
        """!
        from Koller and Friedman 2009, p. 557
        """
        is_all_type(Zs, "Zs", NumCatRVariable, True)
        Z_potential: List[Tuple[AbstractFactor, int]] = []
        for i in range(len(Zs)):
            Z = Zs[i]
            factors, maxed_out, z_phi = PGMOps.max_product_eliminate_var(
                g, factors, Z=Z
            )
            Z_potential.append(z_phi)
        #
        values = PGMOps.traceback_map(g=g, potentials=Z_potential, X_is=Zs)
        return values, factors, z_phi

    @staticmethod
    def max_product_ve(g: PGModel, evidences: Set[Tuple[str, NumericValue]]):
        """!
        Compute most probable assignments given evidences
        """
        factors, E = PGMOps.reduce_factors_with_evidence(g=g, evidences=evidences)
        Zs = set()
        for z in g.V:
            if z not in E:
                Zs.add(z)
        cardinality = PGMOps.order_by_greedy_metric(
            g=g, nodes=Zs, s=min_unmarked_neighbours
        )
        V = {v.id(): v for v in g.V}
        ordering = [
            V[n[0]] for n in sorted(list(cardinality.items()), key=lambda x: x[1])
        ]
        assignments, factors, z_phi = PGMOps.max_product_eliminate_vars(
            g=g, factors=factors, Zs=ordering
        )
        return assignments, factors, z_phi

    @staticmethod
    def mpe_prob(g: PGModel, evidences: Set[Tuple[str, NumericValue]]) -> float:
        """!
        obtain the probability of the most probable instantiation of
        the model
        """
        assignments, factors, z_phi = PGMOps.max_product_ve(g=g, evidences=evidences)
        probs = set()
        for f in FactorOps.cartesian(z_phi):
            probs.add(z_phi.phi(f))
        return max(probs)

    @staticmethod
    def traceback_map(
        g: PGModel, potentials: List[AbstractFactor], X_is: List[NumCatRVariable]
    ) -> List[Tuple[str, NumericValue]]:
        """!
        from Koller and Friedman 2009, p. 557
        The idea here is the following:
        For the last variable eliminated, Z, the factor for the value x
        contains the probability of the most likely assignment that contains
        Z=x.
        For example:
        let's say g* = argmax(psi(G))
        2. l* = argmax(psi[g*](L))
        3. d* = argmax(psi[l*](D))
        """
        is_all_type(potentials, "potentials", AbstractFactor, True)
        max_assignments = {}
        for i in range(len(potentials) - 1, -1, -1):
            pmax = FactorAnalyzer.max_value(potentials[i])
            diff = set([p for p in pmax if p[0] not in max_assignments])
            max_assign = diff.pop()
            max_assignments[max_assign[0]] = max_assign[1]
        return max_assignments
