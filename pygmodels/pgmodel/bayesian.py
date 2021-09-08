"""!
Bayesian Network model
"""

from typing import Callable, Optional, Set
from uuid import uuid4

from pygmodels.gmodel.digraph import DiGraph
from pygmodels.graphf.bgraphops import BaseGraphOps
from pygmodels.gtype.edge import Edge
from pygmodels.pgmtype.factor import Factor
from pygmodels.pgmtype.pgmodel import PGModel
from pygmodels.pgmtype.randomvariable import NumCatRVariable


class BayesianNetwork(PGModel, DiGraph):
    """!
    bayesian network implementation
    """

    def __init__(
        self,
        gid: str,
        nodes: Set[NumCatRVariable],
        edges: Set[Edge],
        factors: Set[Factor],
        data={},
    ):
        """!
        \see PGModel for parameters

        Simple bayesian network implementation where edges are checked for
        being directed

        \code{.py}

        >>> idata = {"outcome-values": [True, False]}

        >>> C = NumCatRVariable(
        >>>     node_id="C", input_data=idata, distribution=lambda x: 0.5
        >>> )
        >>> E = NumCatRVariable(
        >>>     node_id="E", input_data=idata, distribution=lambda x: 0.5
        >>> )
        >>> F = NumCatRVariable(
        >>>     node_id="F", input_data=idata, distribution=lambda x: 0.5
        >>> )
        >>> D = NumCatRVariable(
        >>>     node_id="D", input_data=idata, distribution=lambda x: 0.5
        >>> )
        >>> CE = Edge(
        >>>   edge_id="CE",
        >>>   start_node=C,
        >>>   end_node=E,
        >>>   edge_type=EdgeType.DIRECTED,
        >>> )
        >>> ED = Edge(
        >>>     edge_id="ED",
        >>>     start_node=E,
        >>>     end_node=D,
        >>>     edge_type=EdgeType.DIRECTED,
        >>> )
        >>> EF = Edge(
        >>>     edge_id="EF",
        >>>     start_node=E,
        >>>     end_node=F,
        >>>     edge_type=EdgeType.DIRECTED,
        >>> )

        >>> def phi_c(scope_product):
        >>>     ss = set(scope_product)
        >>>    if ss == set([("C", True)]):
        >>>        return 0.8
        >>>     elif ss == set([("C", False)]):
        >>>         return 0.2
        >>>     else:
        >>>         raise ValueError("scope product unknown")

        >>> def phi_ec(scope_product):
        >>>     ss = set(scope_product)
        >>>     if ss == set([("C", True), ("E", True)]):
        >>>         return 0.9
        >>>     elif ss == set([("C", True), ("E", False)]):
        >>>         return 0.1
        >>>   elif ss == set([("C", False), ("E", True)]):
        >>>       return 0.7
        >>>   elif ss == set([("C", False), ("E", False)]):
        >>>       return 0.3
        >>>   else:
        >>>        raise ValueError("scope product unknown")

        >>> def phi_fe(scope_product):
        >>>   ss = set(scope_product)
        >>>   if ss == set([("E", True), ("F", True)]):
        >>>       return 0.9
        >>>   elif ss == set([("E", True), ("F", False)]):
        >>>       return 0.1
        >>>   elif ss == set([("E", False), ("F", True)]):
        >>>         return 0.5
        >>>     elif ss == set([("E", False), ("F", False)]):
        >>>         return 0.5
        >>>     else:
        >>>         raise ValueError("scope product unknown")

        >>> def phi_de(scope_product):
        >>>     ss = set(scope_product)
        >>>   if ss == set([("E", True), ("D", True)]):
        >>>       return 0.7
        >>>   elif ss == set([("E", True), ("D", False)]):
        >>>       return 0.3
        >>>   elif ss == set([("E", False), ("D", True)]):
        >>>       return 0.4
        >>>   elif ss == set([("E", False), ("D", False)]):
        >>>       return 0.6
        >>>    else:
        >>>        raise ValueError("scope product unknown")

        >>> CE_f = Factor(
        >>>     gid="CE_f", scope_vars=set([C, E]), factor_fn=phi_ec
        >>> )
        >>> C_f = Factor(gid="C_f", scope_vars=set([C]), factor_fn=phi_c)
        >>> FE_f = Factor(
        >>>     gid="FE_f", scope_vars=set([F, E]), factor_fn=phi_fe
        >>> )
        >>> DE_f = Factor(
        >>>     gid="DE_f", scope_vars=set([D, E]), factor_fn=phi_de
        >>> )
        >>> bayes_n = BayesianNetwork(
        >>>     gid="ba",
        >>>     nodes=set([C, E, D, F]),
        >>>     edges=set([EF, CE, ED]),
        >>>     factors=set([C_f, DE_f, CE_f, FE_f]),
        >>> )

        \endcode
        """
        super().__init__(
            gid=gid, data=data, nodes=nodes, edges=edges, factors=factors
        )

    @classmethod
    def deduce_factors_from_digraph(
        cls,
        dig: DiGraph,
        fn: Optional[
            Callable[[NumCatRVariable, Set[NumCatRVariable]], Factor]
        ] = None,
    ) -> Set[Factor]:
        """"""
        fs: Set[Factor] = set()
        for X_i in dig.nodes():
            evidences = set()
            if "evidence" in X_i.data():
                evidences.add((X_i.id(), X_i.data()["evidence"]))
            for n in dig.parents_of(X_i):
                if "evidence" in n.data():
                    evidences.add((n.id(), n.data()["evidence"]))
            if fn is not None:
                f = fn(X_i, dig.parents_of(X_i))
                if len(evidences) != 0:
                    f = f.reduced_by_value(evidences)
                fs.add(f)
        return fs

    @classmethod
    def from_digraph(cls, dig: DiGraph, fs: Optional[Set[Factor]]):
        """!
        \brief Construct a BayesianNetwork from a directed graph

        We assume that edges encode an independence structure of the system.
        Hence we deduce factors from them. If there is any evidence associated
        with a random variable, we apply them to reduce factors.

        \param dig A Directed Graph whose nodes are random variables

        \return BayesianNetwork

        \code{.py}

        >>> myDiGraph = DiGraph()

        \endcode
        """
        if fs is None:
            fs = cls.deduce_factors_from_digraph(dig)
        #
        return BayesianNetwork(
            gid=str(uuid4()),
            nodes=dig.V,
            edges=dig.E,
            factors=fs,
        )
