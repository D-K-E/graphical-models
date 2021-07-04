"""!
Markov network
"""
from gmodels.gtype.undigraph import UndiGraph
from gmodels.gtype.edge import Edge
from gmodels.pgmtype.randomvariable import (
    NumCatRVariable,
    RandomVariable,
    NumericValue,
)
from gmodels.pgmtype.factor import Factor
from gmodels.pgmtype.pgmodel import PGModel
from typing import Set, Optional, Tuple
from uuid import uuid4
import pdb


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
        \brief Markov Random Field implementation

        For parameters \see PGModel

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

        \throws ValueError If nodes are not an instance of a random variable,
        we raise a value error.

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
        for n in udi.nodes():
            if not isinstance(n, RandomVariable):
                raise ValueError("Nodes are not an instance of random variable")
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
        \brief Conditional Random Field


        Several traits distinguish Conditional Random Fields (CRFs) from Markov
        Networks.
        Formally Conditional random fields are defined by Koller, Friedman 2009 p. 143
        as: <blockquote> an undirected graph whose nodes correspond to a union of a set
        of observed random variables X, and a set of target random variables Y; the
        network is annotated with a set of factors \f$\phi_1(D_1), \dots, \phi_i(D_i),
        \dots, \phi_m(D_m)\f$ such that \f$D_i \not \subset X\f$.
        </blockquote>
        The network encodes a conditional distribution between target and observed
        variables.

        The purpose of CRFs is best described by Sucar 2015, p. 92:
        <blockquote>
        Conditional models are used to label an observation sequence X by
        selecting the label sequence Y that maximizes the conditional
        probability P(Y|X). The conditional nature of such models means that no
        effort is wasted on modeling observations, and one is free from having
        to make unnecessary independence assumptions.
        </blockquote>

        \throws ValueError We raise a value error if a factor's scope is a
        subset of observed variables

        \param observed_vars observed random variables. These variables must be
        different than target variables. They are allowed to have edges between
        them. The model is conditioned on these variables

        \param target_vars target random variables.

        \param factors factors that encode the conditional distribution of the
        model

        \code{.py}

        >>> idata = {"A": {"outcome-values": [True, False]}}

        >>> # from Koller, Friedman 2009, p. 144-145, example 4.20
        >>> X_1 = NumCatRVariable(
        >>>     node_id="X_1", input_data=idata["A"], distribution=lambda x: 0.5
        >>> )
        >>> X_2 = NumCatRVariable(
        >>>     node_id="X_2", input_data=idata["A"], distribution=lambda x: 0.5
        >>> )
        >>> X_3 = NumCatRVariable(
        >>>     node_id="X_3", input_data=idata["A"], distribution=lambda x: 0.5
        >>> )
        >>> Y_1 = NumCatRVariable(
        >>>     node_id="Y_1", input_data=idata["A"], distribution=lambda x: 0.5
        >>> )
        >>> X1_Y1 = Edge(
        >>>    edge_id="X1_Y1",
        >>>    edge_type=EdgeType.UNDIRECTED,
        >>>    start_node=X_1,
        >>>    end_node=Y_1,
        >>> )
        >>> X2_Y1 = Edge(
        >>>   edge_id="X2_Y1",
        >>>   edge_type=EdgeType.UNDIRECTED,
        >>>   start_node=X_2,
        >>>   end_node=Y_1,
        >>> )
        >>> X3_Y1 = Edge(
        >>>   edge_id="X3_Y1",
        >>>   edge_type=EdgeType.UNDIRECTED,
        >>>   start_node=X_3,
        >>>   end_node=Y_1,
        >>> )

        >>> def phi_X1_Y1(scope_product):
        >>>   ""
        >>>   w = 0.5
        >>>   ss = frozenset(scope_product)
        >>>   if ss == frozenset([("X_1", True), ("Y_1", True)]):
        >>>       return math.exp(1.0 * w)
        >>>   else:
        >>>       return math.exp(0.0)

        >>> def phi_X2_Y1(scope_product):
        >>>   ""
        >>>   w = 5.0
        >>>   ss = frozenset(scope_product)
        >>>   if ss == frozenset([("X_2", True), ("Y_1", True)]):
        >>>       return math.exp(1.0 * w)
        >>>   else:
        >>>       return math.exp(0.0)

        >>> def phi_X3_Y1(scope_product):
        >>>   ""
        >>>   w = 9.4
        >>>   ss = frozenset(scope_product)
        >>>   if ss == frozenset([("X_3", True), ("Y_1", True)]):
        >>>       return math.exp(1.0 * w)
        >>>   else:
        >>>       return math.exp(0.0)

        >>> def phi_Y1(scope_product):
        >>>   ""
        >>>   w = 0.6
        >>>   ss = frozenset(scope_product)
        >>>   if ss == frozenset([("Y_1", True)]):
        >>>       return math.exp(1.0 * w)
        >>>   else:
        >>>       return math.exp(0.0)

        >>> X1_Y1_f = Factor(
        >>>     gid="x1_y1_f", scope_vars=set([X_1, Y_1]), factor_fn=phi_X1_Y1
        >>> )
        >>> X2_Y1_f = Factor(
        >>>     gid="x2_y1_f", scope_vars=set([X_2, Y_1]), factor_fn=phi_X2_Y1
        >>> )
        >>> X3_Y1_f = Factor(
        >>>     gid="x3_y1_f", scope_vars=set([X_3, Y_1]), factor_fn=phi_X3_Y1
        >>> )
        >>> Y1_f = Factor(gid="y1_f", scope_vars=set([Y_1]), factor_fn=phi_Y1)

        >>> crf_koller = ConditionalRandomField(
        >>>     "crf",
        >>>     observed_vars=set([X_1, X_2, X_3]),
        >>>     target_vars=set([Y_1]),
        >>>     edges=set([X1_Y1, X2_Y1, X3_Y1]),
        >>>     factors=set([X1_Y1_f, X2_Y1_f, X3_Y1_f, Y1_f]),
        >>> )
        >>> evidence = set([("Y_1", False)])
        >>> query = set(
        >>>     [
        >>>         ("X_1", choice([False, True])),
        >>>         ("X_2", choice([False, True])),
        >>>         ("X_3", choice([False, True])),
        >>>     ]
        >>> )
        >>> foo1, a1 = crf_koller.cond_prod_by_variable_elimination(
        >>>     queries=query, evidences=evidence
        >>> )
        >>> foo1.phi(query) == 1.0
        >>> True

        \endcode
        """
        if len(observed_vars.intersection(target_vars)) > 0:
            raise ValueError("Observed and target variables intersect")
        for f in factors:
            if f.scope_vars().issubset(observed_vars) is True:
                raise ValueError(
                    "Scope of some factors are subset of observed variables"
                    + "\ntarget vars: "
                    + "".join([t.id() for t in target_vars])
                    + "\n scope vars: "
                    + "".join([s.id() for s in f.scope_vars()])
                )
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
        """!
        \brief target variables \see ConditionalRandomField constructor
        """
        return self.tvars

    @property
    def X(self):
        """!
        \brief observed variables \see ConditionalRandomField constructor
        """
        return self.ovars

    @property
    def target_variables(self):
        """!
        \brief target variables \see ConditionalRandomField constructor
        """
        return self.tvars

    @property
    def observed_variables(self):
        """!
        \brief observed variables \see ConditionalRandomField constructor
        """
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
