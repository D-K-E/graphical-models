"""!
Markov network
"""
from gmodels.gtypes.undigraph import UndiGraph
from gmodels.gtypes.edge import Edge
from gmodels.randomvariable import NumCatRVariable
from gmodels.factor import Factor
from gmodels.pgmodel import PGModel
from typing import Set, Optional, Tuple
from uuid import uuid4


class MarkovNetwork(PGModel, UndiGraph):
    def __init__(
        self,
        gid: str,
        nodes: Set[NumCatRVariable],
        edges: Set[Edge],
        factors: Set[Factor],
        data={},
    ):
        """!
        Markov Random Field

        \code{.py}

        >>> idata = {
        >>>     "A": {"outcome-values": [True, False]},
        >>>     "B": {"outcome-values": [True, False]},
        >>>     "C": {"outcome-values": [True, False]},
        >>>     "D": {"outcome-values": [True, False]},
        >>> }

        >>> # misconception example
        >>> A = NumCatRVariable(
        >>>     node_id="A", input_data=idata["A"], distribution=lambda x: 0.5
        >>> )
        >>> B = NumCatRVariable(
        >>>     node_id="B", input_data=idata["B"], distribution=lambda x: 0.5
        >>> )
        >>> C = NumCatRVariable(
        >>>     node_id="C", input_data=idata["C"], distribution=lambda x: 0.5
        >>> )
        >>> D = NumCatRVariable(
        >>>     node_id="D", input_data=idata["D"], distribution=lambda x: 0.5
        >>> )
        >>> AB = Edge(
        >>>     edge_id="AB",
        >>>     edge_type=EdgeType.UNDIRECTED,
        >>>     start_node=A,
        >>>     end_node=B,
        >>> )
        >>> AD = Edge(
        >>>     edge_id="AD",
        >>>     edge_type=EdgeType.UNDIRECTED,
        >>>     start_node=A,
        >>>     end_node=D,
        >>> )
        >>> DC = Edge(
        >>>     edge_id="DC",
        >>>     edge_type=EdgeType.UNDIRECTED,
        >>>     start_node=D,
        >>>     end_node=C,
        >>> )
        >>> BC = Edge(
        >>>     edge_id="BC",
        >>>     edge_type=EdgeType.UNDIRECTED,
        >>>     start_node=B,
        >>>     end_node=C,
        >>> )

        >>> def phi_AB(scope_product):
        >>>     ""
        >>>     ss = frozenset(scope_product)
        >>>     if ss == frozenset([("A", False), ("B", False)]):
        >>>         return 30.0
        >>>     elif ss == frozenset([("A", False), ("B", True)]):
        >>>         return 5.0
        >>>     elif ss == frozenset([("A", True), ("B", False)]):
        >>>         return 1.0
        >>>     elif ss == frozenset([("A", True), ("B", True)]):
        >>>         return 10.0
        >>>     else:
        >>>         raise ValueError("product error")

        >>> def phi_BC(scope_product):
        >>>     ""
        >>>     ss = frozenset(scope_product)
        >>>     if ss == frozenset([("B", False), ("C", False)]):
        >>>         return 100.0
        >>>     elif ss == frozenset([("B", False), ("C", True)]):
        >>>         return 1.0
        >>>     elif ss == frozenset([("B", True), ("C", False)]):
        >>>         return 1.0
        >>>     elif ss == frozenset([("B", True), ("C", True)]):
        >>>         return 100.0
        >>>     else:
        >>>         raise ValueError("product error")

        >>> def phi_CD(scope_product):
        >>>     ""
        >>>     ss = frozenset(scope_product)
        >>>     if ss == frozenset([("C", False), ("D", False)]):
        >>>         return 1.0
        >>>     elif ss == frozenset([("C", False), ("D", True)]):
        >>>         return 100.0
        >>>     elif ss == frozenset([("C", True), ("D", False)]):
        >>>         return 100.0
        >>>     elif ss == frozenset([("C", True), ("D", True)]):
        >>>         return 1.0
        >>>     else:
        >>>         raise ValueError("product error")

        >>> def phi_DA(scope_product):
        >>>     ""
        >>>     ss = frozenset(scope_product)
        >>>     if ss == frozenset([("D", False), ("A", False)]):
        >>>         return 100.0
        >>>     elif ss == frozenset([("D", False), ("A", True)]):
        >>>         return 1.0
        >>>     elif ss == frozenset([("D", True), ("A", False)]):
        >>>         return 1.0
        >>>     elif ss == frozenset([("D", True), ("A", True)]):
        >>>         return 100.0
        >>>     else:
        >>>         raise ValueError("product error")

        >>> AB_f = Factor(
        >>>     gid="ab_f", scope_vars=set([A, B]), factor_fn=phi_AB
        >>> )
        >>> BC_f = Factor(
        >>>     gid="bc_f", scope_vars=set([B, C]), factor_fn=phi_BC
        >>> )
        >>> CD_f = Factor(
        >>>     gid="cd_f", scope_vars=set([C, D]), factor_fn=phi_CD
        >>> )
        >>> DA_f = Factor(
        >>>     gid="da_f", scope_vars=set([D, A]), factor_fn=phi_DA
        >>> )

        >>> mnetwork = MarkovNetwork(
        >>>     gid="mnet",
        >>>     nodes=set([A, B, C, D]),
        >>>     edges=set([AB, AD, BC, DC]),
        >>>     factors=set([DA_f, CD_f, BC_f, AB_f]),
        >>> )

        \endcode
        """
        super().__init__(gid=gid, nodes=nodes, edges=edges, data=data, factors=factors)

    @classmethod
    def from_undigraph(cls, udi: UndiGraph):
        """!
        \brief Make a markov network from undirected graph

        Unless it is specified we assume that edges indicate a joint
        distribution

        \code{.py}

         >>> idata = {"A": {"outcome-values": [True, False]}}
         >>> a = NumCatRVariable(
         >>>     node_id="a",
         >>>     input_data=idata["A"],
         >>>     distribution=lambda x: 0.01 if x else 0.99,
         >>> )
         >>> b = NumCatRVariable(
         >>>     node_id="b", input_data=idata["B"], distribution=lambda x: 0.5
         >>> )
         >>> d = NumCatRVariable(
         >>>     node_id="d",
         >>>     input_data=idata["A"],
         >>>     distribution=lambda x: 0.7468 if x else 0.2532,
         >>> )
         >>> c = NumCatRVariable(
         >>>     node_id="c",
         >>>     input_data=idata["A"],
         >>>     distribution=lambda x: 0.7312 if x else 0.2688,
         >>> )
         >>> ab = Edge(
         >>>     "ab", start_node=a, end_node=b, edge_type=EdgeType.UNDIRECTED
         >>> )
         >>> ad = Edge(
         >>>     "ad", start_node=a, end_node=d, edge_type=EdgeType.UNDIRECTED
         >>> )
            
         >>> bc = Edge(
         >>>     "bc", start_node=b, end_node=c, edge_type=EdgeType.UNDIRECTED
         >>> )
         >>> dc = Edge(
         >>>     "dc", start_node=d, end_node=c, edge_type=EdgeType.UNDIRECTED
         >>> )
         >>> ugraph = UndiGraph(
         >>>     "ug1",
         >>>     data={"m": "f"},
         >>>     nodes=set([a, b, c, d]),
         >>>     edges=set([ab, ad, bc, dc]),
         >>> )
         >>> markov = MarkovNetwork.from_undigraph(udi=ugraph)

        \endcode
        """
        fs: Set[Factor] = set()
        maximal_cliques = udi.find_maximal_cliques()
        for clique in maximal_cliques:
            evidences = set()
            for n in clique:
                edata = n.data()
                if "evidence" in edata:
                    evidences.add((n.id(), edata["evidence"]))
            f = Factor(gid=str(uuid4()), scope_vars=clique)
            if len(evidences) != 0:
                f = f.reduced_by_value(evidences)
            fs.add(f)
        return MarkovNetwork(
            gid=str(uuid4()), nodes=udi.nodes(), edges=udi.edges(), factors=fs
        )


class ConditionalRandomField(MarkovNetwork):
    """!
    Conditional random field as defined by Koller, Friedman 2009, p. 142-3
    """

    def __init__(
        self,
        gid: str,
        observed_vars: Set[NumCatRVariable],
        target_vars: Set[NumCatRVariable],
        edges: Set[Edge],
        factors: Set[Factor],
        data={},
    ):
        """!
        CRF constructor
        """
        if len(observed_vars.intersection(target_vars)) > 0:
            raise ValueError("Observed and target variables intersect")
        for f in factors:
            if f.scope_vars().issubset(target_vars) is True:
                raise ValueError("Scope of some factors are subset of target variables")
        super().__init__(
            gid=gid,
            nodes=observed_vars.union(target_vars),
            edges=edges,
            data=data,
            factors=factors,
        )
        self.ovars = observed_vars
        self.tvars = target_vars

    @property
    def Y(self):
        return self.tvars

    @property
    def X(self):
        return self.ovars

    @property
    def target_vars(self):
        return self.tvars

    @property
    def observed_vars(self):
        return self.ovars

    @classmethod
    def from_markov_network(cls, mn: MarkovNetwork, targets: Set[NumCatRVariable]):
        ""
        mnodes = mn.nodes()
        if targets.issubset(mnodes) is False:
            raise ValueError("target variables are not a subset of network")
        factors = mn.factors()
        crf_factors = set(
            [f for f in factors if f.scope_vars().issubset(targets) is False]
        )
        return ConditionalRandomField(
            gid=str(uuid4()),
            observed_vars=mnodes.difference(targets),
            target_vars=targets,
            edges=mn.edges(),
            factors=crf_factors,
        )

    def joint_target_observed(self) -> Tuple[Factor, float]:
        """!
        Implements the procedure in definition 4.18
        from Koller, Friedman 2009, p. 143
        """
        return self.get_factor_product(self.factors())

    def Z(self) -> Factor:
        """!
        """
        prod, v = self.joint_target_observed()
        zfac = prod.sumout_vars(self.tvars)
        return zfac

    def conditinal_probability(self):
        """!
        Implements the procedure in definition 4.18
        from Koller, Friedman 2009, p. 143
        """
        Zfac = self.Z()
        P_yx = self.joint_target_observed()

        def phi_cond(scope_product):
            ""
            ss = set(scope_product)
            z_i = Zfac.phi(ss)
            p_yx_i = P_yx.phi(ss)
            return p_yx_i / z_i

        return Factor(gid=str(uuid4()), factor_fn=phi_cond, scope_vars=self.X)


"""!
\page markovnetworkexample Markov Network Usage

Markov Network is defined by Koller, Friedman 2009, p. 103 is
<blockquote>
As in a Bayesian network, the nodes in the graph of a Markov network represent
the variables, and the edges correspond to a notion of direct probabilistic
interaction between the neighboring variables — an interaction that is not
mediated by any other variable in the network.
</blockquote>

Usage:

\code{.py}

idata = {
    "A": {"outcome-values": [True, False]},
    "B": {"outcome-values": [True, False]},
    "C": {"outcome-values": [True, False]},
    "D": {"outcome-values": [True, False]},
}
                                                                   
# misconception example
A = NumCatRVariable(
    node_id="A", input_data=idata["A"], distribution=lambda x: 0.5
)
B = NumCatRVariable(
    node_id="B", input_data=idata["B"], distribution=lambda x: 0.5
)
C = NumCatRVariable(
    node_id="C", input_data=idata["C"], distribution=lambda x: 0.5
)
D = NumCatRVariable(
    node_id="D", input_data=idata["D"], distribution=lambda x: 0.5
)
AB = Edge(
    edge_id="AB",
    edge_type=EdgeType.UNDIRECTED,
    start_node=A,
    end_node=B,
)
AD = Edge(
    edge_id="AD",
    edge_type=EdgeType.UNDIRECTED,
    start_node=A,
    end_node=D,
)
DC = Edge(
    edge_id="DC",
    edge_type=EdgeType.UNDIRECTED,
    start_node=D,
    end_node=C,
)
BC = Edge(
    edge_id="BC",
    edge_type=EdgeType.UNDIRECTED,
    start_node=B,
    end_node=C,
)
                                                                   
def phi_AB(scope_product):
    ""
    ss = frozenset(scope_product)
    if ss == frozenset([("A", False), ("B", False)]):
        return 30.0
    elif ss == frozenset([("A", False), ("B", True)]):
        return 5.0
    elif ss == frozenset([("A", True), ("B", False)]):
        return 1.0
    elif ss == frozenset([("A", True), ("B", True)]):
        return 10.0
    else:
        raise ValueError("product error")
                                                                   
def phi_BC(scope_product):
    ""
    ss = frozenset(scope_product)
    if ss == frozenset([("B", False), ("C", False)]):
        return 100.0
    elif ss == frozenset([("B", False), ("C", True)]):
        return 1.0
    elif ss == frozenset([("B", True), ("C", False)]):
        return 1.0
    elif ss == frozenset([("B", True), ("C", True)]):
        return 100.0
    else:
        raise ValueError("product error")
                                                                   
def phi_CD(scope_product):
    ""
    ss = frozenset(scope_product)
    if ss == frozenset([("C", False), ("D", False)]):
        return 1.0
    elif ss == frozenset([("C", False), ("D", True)]):
        return 100.0
    elif ss == frozenset([("C", True), ("D", False)]):
        return 100.0
    elif ss == frozenset([("C", True), ("D", True)]):
        return 1.0
    else:
        raise ValueError("product error")
                                                                   
def phi_DA(scope_product):
    ""
    ss = frozenset(scope_product)
    if ss == frozenset([("D", False), ("A", False)]):
        return 100.0
    elif ss == frozenset([("D", False), ("A", True)]):
        return 1.0
    elif ss == frozenset([("D", True), ("A", False)]):
        return 1.0
    elif ss == frozenset([("D", True), ("A", True)]):
        return 100.0
    else:
        raise ValueError("product error")
                                                                   
AB_f = Factor(
    gid="ab_f", scope_vars=set([A, B]), factor_fn=phi_AB
)
BC_f = Factor(
    gid="bc_f", scope_vars=set([B, C]), factor_fn=phi_BC
)
CD_f = Factor(
    gid="cd_f", scope_vars=set([C, D]), factor_fn=phi_CD
)
DA_f = Factor(
    gid="da_f", scope_vars=set([D, A]), factor_fn=phi_DA
)
                                                                   
mnetwork = MarkovNetwork(
    gid="mnet",
    nodes=set([A, B, C, D]),
    edges=set([AB, AD, BC, DC]),
    factors=set([DA_f, CD_f, BC_f, AB_f]),
)

\endcode

"""
