"""!
test lwf chain graph test
"""
import pdb
import unittest
from uuid import uuid4

from pygmodels.factor.factor import Factor
from pygmodels.factor.factorfunc.factorops import FactorOps
from pygmodels.graph.graphmodel.undigraph import UndiGraph
from pygmodels.graph.graphops.graphops import BaseGraphOps
from pygmodels.graph.graphtype.edge import Edge, EdgeType
from pygmodels.pgm.pgmodel.lwfchain import LWFChainGraph
from pygmodels.pgm.pgmodel.markov import ConditionalRandomField
from pygmodels.pgm.pgmtype.pgmodel import PGModel
from pygmodels.pgm.pgmtype.randomvariable import NumCatRVariable


class LWFChainGraphTest(unittest.TestCase):
    """"""

    def data_1(self):
        """"""
        idata = {"outcome-values": [True, False]}
        self.A = NumCatRVariable(
            node_id="A", input_data=idata, marginal_distribution=lambda x: 0.5
        )
        self.B = NumCatRVariable(
            node_id="B", input_data=idata, marginal_distribution=lambda x: 0.5
        )
        self.C = NumCatRVariable(
            node_id="C", input_data=idata, marginal_distribution=lambda x: 0.5
        )
        self.D = NumCatRVariable(
            node_id="D", input_data=idata, marginal_distribution=lambda x: 0.5
        )
        self.E = NumCatRVariable(
            node_id="E", input_data=idata, marginal_distribution=lambda x: 0.5
        )
        self.F = NumCatRVariable(
            node_id="F", input_data=idata, marginal_distribution=lambda x: 0.5
        )
        self.G = NumCatRVariable(
            node_id="G", input_data=idata, marginal_distribution=lambda x: 0.5
        )
        self.H = NumCatRVariable(
            node_id="H", input_data=idata, marginal_distribution=lambda x: 0.5
        )
        self.Irvar = NumCatRVariable(
            node_id="I", input_data=idata, marginal_distribution=lambda x: 0.5
        )
        self.K = NumCatRVariable(
            node_id="K", input_data=idata, marginal_distribution=lambda x: 0.5
        )
        self.L = NumCatRVariable(
            node_id="L", input_data=idata, marginal_distribution=lambda x: 0.5
        )
        #
        #  Cowell 2005, p. 110
        #
        #   A                      E---+
        #   |                          |
        #   +----+                 F <-+
        #        |                 |
        #   B <--+---> C --> D <---+
        #   |                |
        #   +---> H <--------+----> G
        #   |     |
        #   +---> I
        #
        self.AB_c = Edge(
            edge_id="AB",
            start_node=self.A,
            end_node=self.B,
            edge_type=EdgeType.DIRECTED,
        )
        self.AC_c = Edge(
            edge_id="AC",
            start_node=self.A,
            end_node=self.C,
            edge_type=EdgeType.DIRECTED,
        )
        self.CD_c = Edge(
            edge_id="CD",
            start_node=self.C,
            end_node=self.D,
            edge_type=EdgeType.DIRECTED,
        )
        self.EF_c = Edge(
            edge_id="EF",
            start_node=self.E,
            end_node=self.F,
            edge_type=EdgeType.DIRECTED,
        )
        self.FD_c = Edge(
            edge_id="FD",
            start_node=self.F,
            end_node=self.D,
            edge_type=EdgeType.DIRECTED,
        )
        self.DG_c = Edge(
            edge_id="DG",
            start_node=self.D,
            end_node=self.G,
            edge_type=EdgeType.DIRECTED,
        )
        self.DH_c = Edge(
            edge_id="DH",
            start_node=self.D,
            end_node=self.H,
            edge_type=EdgeType.DIRECTED,
        )
        self.BH_c = Edge(
            edge_id="BH",
            start_node=self.B,
            end_node=self.H,
            edge_type=EdgeType.DIRECTED,
        )
        self.BI_c = Edge(
            edge_id="BI",
            start_node=self.B,
            end_node=self.Irvar,
            edge_type=EdgeType.DIRECTED,
        )
        self.HI_c = Edge(
            edge_id="HI",
            start_node=self.H,
            end_node=self.Irvar,
            edge_type=EdgeType.UNDIRECTED,
        )

    def data_2(self):
        """"""

        def phi_e(scope_product):
            """!
            Visit to Asia factor
            p(a)
            """
            ss = set(scope_product)
            if ss == set([("E", True)]):
                return 0.01
            elif ss == set([("E", False)]):
                return 0.99
            else:
                raise ValueError("Unknown scope product")

        self.E_cf = Factor(
            gid="E_cf", scope_vars=set([self.E]), factor_fn=phi_e
        )

        def phi_fe(scope_product):
            """!
            Tuberculosis | Visit to Asia factor
            p(t,a)
            """
            ss = set(scope_product)
            if ss == set([("F", True), ("E", True)]):
                return 0.05
            elif ss == set([("F", False), ("E", True)]):
                return 0.95
            elif ss == set([("F", True), ("E", False)]):
                return 0.01
            elif ss == set([("F", False), ("E", False)]):
                return 0.99
            else:
                raise ValueError("Unknown scope product")

        self.EF_cf = Factor(
            gid="EF_cf", scope_vars=set([self.E, self.F]), factor_fn=phi_fe
        )

        def phi_dg(scope_product):
            """!
            either tuberculosis or lung cancer | x ray
            p(e,x)
            """
            ss = set(scope_product)
            if ss == set([("D", True), ("G", True)]):
                return 0.98
            elif ss == set([("D", False), ("G", True)]):
                return 0.05
            elif ss == set([("D", True), ("G", False)]):
                return 0.02
            elif ss == set([("D", False), ("G", False)]):
                return 0.95
            else:
                raise ValueError("Unknown scope product")

        self.DG_cf = Factor(
            gid="DG_cf", scope_vars=set([self.D, self.G]), factor_fn=phi_dg
        )

    def data_3(self):
        """"""

        def phi_a(scope_product):
            """!
            smoke factor
            p(s)
            """
            ss = set(scope_product)
            if ss == set([("A", True)]):
                return 0.5
            elif ss == set([("A", False)]):
                return 0.5
            else:
                raise ValueError("Unknown scope product")

        self.A_cf = Factor(
            gid="A_cf", scope_vars=set([self.A]), factor_fn=phi_a
        )

        def phi_ab(scope_product):
            """!
            smoke given bronchitis
            p(s,b)
            """
            ss = set(scope_product)
            if ss == set([("A", True), ("B", True)]):
                return 0.6
            elif ss == set([("A", False), ("B", True)]):
                return 0.3
            elif ss == set([("A", True), ("B", False)]):
                return 0.4
            elif ss == set([("A", False), ("B", False)]):
                return 0.7
            else:
                raise ValueError("Unknown scope product")

        self.AB_cf = Factor(
            gid="AB_cf", scope_vars=set([self.A, self.B]), factor_fn=phi_ab
        )

        def phi_ac(scope_product):
            """!
            lung cancer given smoke
            p(s,l)
            """
            ss = set(scope_product)
            if ss == set([("A", True), ("C", True)]):
                return 0.1
            elif ss == set([("A", False), ("C", True)]):
                return 0.01
            elif ss == set([("A", True), ("C", False)]):
                return 0.9
            elif ss == set([("A", False), ("C", False)]):
                return 0.99
            else:
                raise ValueError("Unknown scope product")

        self.AC_cf = Factor(
            gid="AC_cf", scope_vars=set([self.A, self.C]), factor_fn=phi_ac
        )

    def data_4(self):
        """"""
        # Factors
        #

        def phi_cdf(scope_product):
            """!
            either tuberculosis or lung given lung cancer and tuberculosis
            p(e, l, t)
            """
            ss = set(scope_product)
            if ss == set([("C", True), ("D", True), ("F", True)]):
                return 1
            elif ss == set([("C", True), ("D", False), ("F", True)]):
                return 0
            elif ss == set([("C", False), ("D", True), ("F", True)]):
                return 1
            elif ss == set([("C", False), ("D", False), ("F", True)]):
                return 0
            elif ss == set([("C", True), ("D", True), ("F", False)]):
                return 1
            elif ss == set([("C", True), ("D", False), ("F", False)]):
                return 0
            elif ss == set([("C", False), ("D", True), ("F", False)]):
                return 0
            elif ss == set([("C", False), ("D", False), ("F", False)]):
                return 1
            else:
                raise ValueError("Unknown scope product")

        self.CDF_cf = Factor(
            gid="CDF_cf",
            scope_vars=set([self.D, self.C, self.F]),
            factor_fn=phi_cdf,
        )

        def phi_ihb(scope_product):
            """!
            cough, dyspnoea, bronchitis
            I, H, B
            p(c,d,b)
            """
            ss = set(scope_product)
            if ss == set([("H", True), ("I", True), ("B", True)]):
                return 16
            elif ss == set([("H", True), ("I", False), ("B", True)]):
                return 1
            elif ss == set([("H", False), ("I", True), ("B", True)]):
                return 4
            elif ss == set([("H", False), ("I", False), ("B", True)]):
                return 1
            elif ss == set([("H", True), ("I", True), ("B", False)]):
                return 2
            elif ss == set([("H", True), ("I", False), ("B", False)]):
                return 1
            elif ss == set([("H", False), ("I", True), ("B", False)]):
                return 1
            elif ss == set([("H", False), ("I", False), ("B", False)]):
                return 1
            else:
                raise ValueError("Unknown scope product")

        self.IHB_cf = Factor(
            gid="IHB_cf",
            scope_vars=set([self.H, self.Irvar, self.B]),
            factor_fn=phi_ihb,
        )

        def phi_hbd(scope_product):
            """!
            cough, either tuberculosis or lung cancer, bronchitis
            D, H, B
            p(c,b,e)
            """
            ss = set(scope_product)
            if ss == set([("H", True), ("D", True), ("B", True)]):
                return 5
            elif ss == set([("H", True), ("D", False), ("B", True)]):
                return 2
            elif ss == set([("H", False), ("D", True), ("B", True)]):
                return 1
            elif ss == set([("H", False), ("D", False), ("B", True)]):
                return 1
            elif ss == set([("H", True), ("D", True), ("B", False)]):
                return 3
            elif ss == set([("H", True), ("D", False), ("B", False)]):
                return 1
            elif ss == set([("H", False), ("D", True), ("B", False)]):
                return 1
            elif ss == set([("H", False), ("D", False), ("B", False)]):
                return 1
            else:
                raise ValueError("Unknown scope product")

        self.HBD_cf = Factor(
            gid="HBD_cf",
            scope_vars=set([self.H, self.D, self.B]),
            factor_fn=phi_hbd,
        )

        def phi_bd(scope_product):
            """!
            bronchitis, either tuberculosis or lung cancer
            B, D
            p(b,e)
            """
            ss = set(scope_product)
            if ss == set([("B", True), ("D", True)]):
                return 1 / 90
            elif ss == set([("B", False), ("D", True)]):
                return 1 / 11
            elif ss == set([("B", True), ("D", False)]):
                return 1 / 39
            elif ss == set([("B", False), ("D", False)]):
                return 1 / 5
            else:
                raise ValueError("Unknown scope product")

        self.BD_cf = Factor(
            gid="BD_cf", scope_vars=set([self.D, self.B]), factor_fn=phi_bd
        )

    def setUp(self):
        """"""
        self.data_1()
        self.data_2()
        self.data_3()
        self.data_4()
        #

        self.cowell = LWFChainGraph(
            gid="cowell",
            nodes=set(
                [
                    self.A,
                    self.B,
                    self.C,
                    self.D,
                    self.E,
                    self.F,
                    self.G,
                    self.H,
                    self.Irvar,
                ]
            ),
            edges=set(
                [
                    self.AB_c,
                    self.AC_c,
                    self.CD_c,
                    self.EF_c,
                    self.FD_c,
                    self.DG_c,
                    self.DH_c,
                    self.BH_c,
                    self.BI_c,
                    self.HI_c,
                ]
            ),
            factors=set(
                [
                    self.E_cf,
                    self.EF_cf,
                    self.DG_cf,
                    self.A_cf,
                    self.AB_cf,
                    self.AC_cf,
                    self.CDF_cf,
                    self.IHB_cf,
                    self.HBD_cf,
                    self.BD_cf,
                ]
            ),
        )

        # Koller, Friedman 2009, p. 149
        #
        #  +--------------+
        #  |              |
        #  |    A         +         B
        #  |    |         |         |
        #  |    +--> C -- D -- E <--+
        #  |    |    |         |
        #  |    +--+ |         v
        #  |       | +-------> I <---- H
        #  |   F <-+
        #  |   |
        #  |   +----- G
        #  |          ^
        #  |          |
        #  +----------+
        self.AC_k = Edge(
            edge_id="AC",
            start_node=self.A,
            end_node=self.C,
            edge_type=EdgeType.DIRECTED,
        )
        self.FG_k = Edge(
            edge_id="FG",
            start_node=self.F,
            end_node=self.G,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.DG_k = Edge(
            edge_id="DG",
            start_node=self.D,
            end_node=self.G,
            edge_type=EdgeType.DIRECTED,
        )
        self.CF_k = Edge(
            edge_id="CF",
            start_node=self.C,
            end_node=self.F,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.CD_k = Edge(
            edge_id="CD",
            start_node=self.C,
            end_node=self.D,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.CI_k = Edge(
            edge_id="CI",
            start_node=self.C,
            end_node=self.Irvar,
            edge_type=EdgeType.DIRECTED,
        )
        self.DE_k = Edge(
            edge_id="DE",
            start_node=self.D,
            end_node=self.E,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.EI_k = Edge(
            edge_id="EI",
            start_node=self.E,
            end_node=self.Irvar,
            edge_type=EdgeType.DIRECTED,
        )
        self.BE_k = Edge(
            edge_id="BE",
            start_node=self.B,
            end_node=self.E,
            edge_type=EdgeType.DIRECTED,
        )
        self.HI_k = Edge(
            edge_id="HI",
            start_node=self.H,
            end_node=self.Irvar,
            edge_type=EdgeType.DIRECTED,
        )
        self.koller = LWFChainGraph(
            gid="koller",
            nodes=set(
                [
                    self.A,
                    self.C,
                    self.D,
                    self.E,
                    self.B,
                    self.Irvar,
                    self.F,
                    self.G,
                ]
            ),
            edges=set(
                [
                    self.AC_k,
                    self.FG_k,
                    self.CF_k,
                    self.HI_k,
                    self.CD_k,
                    self.CI_k,
                    self.DE_k,
                    self.DG_k,
                    self.EI_k,
                    self.BE_k,
                ]
            ),
            factors=None,
        )
        # evidence values taken from
        # Cowell 2005, p. 119, table 6.12
        e_comp_val = [("E", True, 0.0096), ("E", False, 0.9904)]
        h_comp_val = [("H", True, 0.7635), ("H", False, 0.2365)]
        c_comp_val = [("C", True, 0.0025), ("C", False, 0.9975)]
        i_comp_val = [("I", True, 0.7939), ("I", False, 0.2061)]
        g_comp_val = [("G", True, 0.1849), ("G", False, 0.8151)]
        a_comp_val = [("A", True, 0.4767), ("A", False, 0.5233)]
        f_comp_val = [("F", True, 0.0012), ("F", False, 0.9988)]
        d_comp_val = [("D", True, 0.0036), ("D", False, 0.9964)]
        b_comp_val = [("B", True, 0.60), ("B", False, 0.40)]
        self.evidences = set([("E", True), ("A", True), ("G", False)])
        self.q_tsts = {
            (self.E): e_comp_val,  # asia
            (self.Irvar): i_comp_val,  # dyspnoea
            (self.H): h_comp_val,  # cough
            (self.A): a_comp_val,  # smoke
            (self.B): b_comp_val,  # bronchitis
            (self.C): c_comp_val,  # lung
            (self.D): d_comp_val,  # either
            (self.F): f_comp_val,  # tuberculosis
            (self.G): g_comp_val,  # x ray
        }

    def test_id(self):
        """"""
        self.assertEqual(self.cowell.id(), "cowell")

    def test_nb_chain_components(self):
        """"""
        nb = self.cowell.nb_components
        self.assertEqual(nb, 8)

    def test_ccomponents(self):
        """"""
        ccomps_nds = set(
            [
                set(s).pop()
                for s in self.cowell.ccomponents
                if isinstance(s, frozenset)
            ]
        )
        ccomps_undi = [
            s for s in self.cowell.ccomponents if isinstance(s, UndiGraph)
        ].pop()
        self.assertEqual(
            ccomps_nds,
            set([self.A, self.B, self.C, self.E, self.F, self.D, self.G]),
        )
        self.assertEqual(set(ccomps_undi.V), set([self.H, self.Irvar]))

    def test_get_chain_dag(self):
        """"""
        dag_comps = self.cowell.dag_components
        self.assertEqual(len(dag_comps.V), 8)

    def test_parents_of_K(self):
        """"""
        ccomps_undi = [
            s
            for s in enumerate(self.cowell.ccomponents)
            if isinstance(s[1], UndiGraph)
        ].pop()
        parents_k = self.cowell.parents_of_K(ccomps_undi[0])
        self.assertEqual(parents_k, set([self.B, self.D]))
        ccomps_undi = [
            s
            for s in enumerate(self.koller.ccomponents)
            if isinstance(s[1], frozenset)
        ]
        parents = set()
        for c in ccomps_undi:
            obj = set(c[1]).pop()
            parent = self.koller.parents_of_K(c[0])
            parents.add(frozenset([obj, frozenset(parent)]))
        self.assertEqual(
            parents,
            set(
                [
                    frozenset([self.B, frozenset()]),
                    frozenset([self.A, frozenset()]),
                    frozenset([self.H, frozenset()]),
                    frozenset(
                        [self.Irvar, frozenset([self.H, self.C, self.E])]
                    ),
                ]
            ),
        )

    def test_K(self):
        """"""
        ccomps_undi = [
            s
            for s in enumerate(self.cowell.ccomponents)
            if isinstance(s[1], UndiGraph)
        ]
        hi = self.cowell.K(ccomps_undi[0][0])
        self.assertEqual(hi.V, set([self.H, self.Irvar]))

    def test_moralize(self):
        """!
        Test according to figure 4.15 in
        Koller, Friedman 2009, p. 149
        """
        moral = self.koller.moralize()
        koller_moralized = set(
            [
                frozenset([self.A.id(), self.B.id()]),
                frozenset([self.A.id(), self.C.id()]),
                frozenset([self.C.id(), self.F.id()]),
                frozenset([self.C.id(), self.D.id()]),
                frozenset([self.C.id(), self.E.id()]),
                frozenset([self.C.id(), self.Irvar.id()]),
                frozenset([self.C.id(), self.H.id()]),
                frozenset([self.D.id(), self.E.id()]),
                frozenset([self.D.id(), self.G.id()]),
                frozenset([self.F.id(), self.G.id()]),
                frozenset([self.E.id(), self.Irvar.id()]),
                frozenset([self.B.id(), self.E.id()]),
                frozenset([self.E.id(), self.H.id()]),
                frozenset([self.H.id(), self.Irvar.id()]),
            ]
        )
        medges = moral.E
        ms = set([frozenset([m.start().id(), m.end().id()]) for m in medges])
        # [print(m) for m in ms]

        self.assertEqual(
            ms,
            koller_moralized,
        )

    def test_cond_prod_by_variable_elimination_evidence(self):
        """!"""
        qs = set([self.B])
        evs = set([("E", True), ("A", True), ("G", False)])
        moral = self.cowell
        p, a = moral.cond_prod_by_variable_elimination(qs, evs)
        # check if it is a valid distribution
        s = 0
        for ps in FactorOps.cartesian(p):
            pss = set(ps)
            f = round(FactorOps.phi_normal(p, pss), 4)
            s += f
            if set([("A", True)]) == pss:
                self.assertEqual(f, 0.01)
            elif set([("A", False)]) == pss:
                self.assertEqual(f, 0.99)
        self.assertTrue(s, 1.0)

    def test_cond_prod_by_variable_elimination(self):
        """!
        Test values taken from
        Cowell 2005, p. 116, table 6.9
        """
        e_comp_val = [("E", True, 0.01), ("E", False, 0.99)]
        i_comp_val = [("I", True, 0.7468), ("I", False, 0.2532)]
        h_comp_val = [("H", True, 0.7312), ("H", False, 0.2688)]
        c_comp_val = [("C", True, 0.055), ("C", False, 0.945)]
        a_comp_val = [("A", True, 0.5), ("A", False, 0.5)]
        b_comp_val = [("B", True, 0.45), ("B", False, 0.55)]
        d_comp_val = [("D", True, 0.0648), ("D", False, 0.9352)]
        f_comp_val = [("F", True, 0.0104), ("F", False, 0.9896)]
        q_tsts = {
            (self.E): e_comp_val,
            (self.Irvar): i_comp_val,  # dyspnoea
            (self.H): h_comp_val,  # cough
            (self.A): a_comp_val,  # smoke
            (self.B): b_comp_val,  # bronchitis
            (self.C): c_comp_val,  # lung
            (self.D): d_comp_val,  # either
            (self.F): f_comp_val,  # tuberculosis
        }
        evs = set()
        for q, cvals in q_tsts.items():
            final_factor, a = self.cowell.cond_prod_by_variable_elimination(
                set([q]), evs
            )
            s = 0
            for cval in cvals:
                cname = cval[0]
                c_v = cval[1]
                c_a = cval[2]
                cs = set([(cname, c_v)])
                f = round(FactorOps.phi_normal(final_factor, cs), 4)
                s += f
                self.assertEqual(c_a, f)
            self.assertEqual(s, 1)

    def test_cond_prod_by_variable_elimination_evidences_B(self):
        """!
        Test values taken from
        Cowell 2005, p. 119, table 6.12
        """
        comp_vals = self.q_tsts[self.B]
        final_factor, a = self.cowell.cond_prod_by_variable_elimination(
            set([self.B]), self.evidences
        )
        for e_val in comp_vals:
            ename = e_val[0]
            e_v = e_val[1]
            f = round(
                FactorOps.phi_normal(final_factor, set([(ename, e_v)])), 4
            )
            self.assertEqual(f, e_val[2])

    def test_cond_prod_by_variable_elimination_evidences_I(self):
        """!
        Test values taken from
        Cowell 2005, p. 119, table 6.12
        """
        comp_vals = self.q_tsts[self.Irvar]
        final_factor, a = self.cowell.cond_prod_by_variable_elimination(
            set([self.Irvar]), self.evidences
        )
        for e_val in comp_vals:
            ename = e_val[0]
            e_v = e_val[1]
            f = round(
                FactorOps.phi_normal(final_factor, set([(ename, e_v)])), 4
            )
            self.assertEqual(f, e_val[2])

    def test_cond_prod_by_variable_elimination_evidences_H(self):
        """!
        Test values taken from
        Cowell 2005, p. 119, table 6.12
        """
        comp_vals = self.q_tsts[self.H]
        final_factor, a = self.cowell.cond_prod_by_variable_elimination(
            set([self.H]), self.evidences
        )
        for e_val in comp_vals:
            ename = e_val[0]
            e_v = e_val[1]
            f = round(
                FactorOps.phi_normal(final_factor, set([(ename, e_v)])), 4
            )
            self.assertEqual(f, e_val[2])

    def test_cond_prod_by_variable_elimination_evidences_C(self):
        """!
        Test values taken from
        Cowell 2005, p. 119, table 6.12
        """
        comp_vals = self.q_tsts[self.C]
        final_factor, a = self.cowell.cond_prod_by_variable_elimination(
            set([self.C]), self.evidences
        )
        for e_val in comp_vals:
            ename = e_val[0]
            e_v = e_val[1]
            f = round(
                FactorOps.phi_normal(final_factor, set([(ename, e_v)])), 4
            )
            self.assertEqual(f, e_val[2])

    def test_cond_prod_by_variable_elimination_evidences_F(self):
        """!
        Test values taken from
        Cowell 2005, p. 119, table 6.12
        """
        comp_vals = self.q_tsts[self.F]
        final_factor, a = self.cowell.cond_prod_by_variable_elimination(
            set([self.F]), self.evidences
        )
        for e_val in comp_vals:
            ename = e_val[0]
            e_v = e_val[1]
            f = round(
                FactorOps.phi_normal(final_factor, set([(ename, e_v)])), 4
            )
            self.assertEqual(f, e_val[2])

    @unittest.skip("unfinished test")
    def test_most_probable_assignment(self):
        """!
        From Cowell 2005, p. 119
        """
        assignments, factors, z_phi = self.cowell.max_product_ve(set())

    def test_mpe_prob_no_evidence(self):
        """!
        From Cowell 2005, p. 119
        """
        cval = 0.2063
        prob = self.cowell.mpe_prob(set())
        self.assertEqual(round(prob, 4), cval)

    def test_mpe_prob_evidence(self):
        """!
        From Cowell 2005, p. 119
        """
        cval = 0.002
        evs = set([("E", True), ("A", True), ("G", False)])
        prob = self.cowell.mpe_prob(evs)
        self.assertEqual(round(prob, 4), cval)

    def test_max_product_ve_evidence(self):
        """!
        From Cowell 2005, p. 119
        """
        cval = {
            "B": True,
            "A": True,
            "C": False,
            "D": False,
            "F": False,
            "H": True,
            "G": False,
            "I": True,
            "E": True,
        }
        evs = set([("E", True), ("A", True), ("G", False)])
        assignments, factors, z_phi = self.cowell.max_product_ve(evs)
        self.assertEqual(assignments, cval)


if __name__ == "__main__":
    unittest.main()
