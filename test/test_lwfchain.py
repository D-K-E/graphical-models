"""!
test lwf chain graph test
"""
from gmodels.pgmodel import PGModel
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.gtypes.undigraph import UndiGraph
from gmodels.factor import Factor
from gmodels.randomvariable import NumCatRVariable
from gmodels.lwfchain import LWFChainGraph
from gmodels.markov import ConditionalRandomField
from uuid import uuid4
import pdb

import unittest


class LWFChainGraphTest(unittest.TestCase):
    ""

    def setUp(self):
        ""
        idata = {"outcome-values": [True, False]}
        self.A = NumCatRVariable(
            node_id="A", input_data=idata, distribution=lambda x: 0.5
        )
        self.B = NumCatRVariable(
            node_id="B", input_data=idata, distribution=lambda x: 0.5
        )
        self.C = NumCatRVariable(
            node_id="C", input_data=idata, distribution=lambda x: 0.5
        )
        self.D = NumCatRVariable(
            node_id="D", input_data=idata, distribution=lambda x: 0.5
        )
        self.E = NumCatRVariable(
            node_id="E", input_data=idata, distribution=lambda x: 0.5
        )
        self.F = NumCatRVariable(
            node_id="F", input_data=idata, distribution=lambda x: 0.5
        )
        self.G = NumCatRVariable(
            node_id="G", input_data=idata, distribution=lambda x: 0.5
        )
        self.H = NumCatRVariable(
            node_id="H", input_data=idata, distribution=lambda x: 0.5
        )
        self.I = NumCatRVariable(
            node_id="I", input_data=idata, distribution=lambda x: 0.5
        )
        self.K = NumCatRVariable(
            node_id="K", input_data=idata, distribution=lambda x: 0.5
        )
        self.L = NumCatRVariable(
            node_id="L", input_data=idata, distribution=lambda x: 0.5
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
            end_node=self.I,
            edge_type=EdgeType.DIRECTED,
        )
        self.HI_c = Edge(
            edge_id="HI",
            start_node=self.H,
            end_node=self.I,
            edge_type=EdgeType.UNDIRECTED,
        )
        #
        # Factors
        #
        def phi_e(scope_product):
            ""
            ss = set(scope_product)
            if ss == set([("E", True)]):
                return 0.01
            elif ss == set([("E", False)]):
                return 0.99
            else:
                raise ValueError("Unknown scope product")

        self.E_cf = Factor(gid="E_cf", scope_vars=set([self.E]), factor_fn=phi_e)

        def phi_fe(scope_product):
            ""
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
            ""
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

        def phi_a(scope_product):
            ""
            ss = set(scope_product)
            if ss == set([("A", True)]):
                return 0.5
            elif ss == set([("A", False)]):
                return 0.5
            else:
                raise ValueError("Unknown scope product")

        self.A_cf = Factor(gid="A_cf", scope_vars=set([self.A]), factor_fn=phi_a)

        def phi_ab(scope_product):
            ""
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
            ""
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

        def phi_cdf(scope_product):
            ""
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
            gid="CDF_cf", scope_vars=set([self.D, self.C, self.F]), factor_fn=phi_cdf
        )

        def phi_cdb(scope_product):
            ""
            ss = set(scope_product)
            if ss == set([("C", True), ("D", True), ("B", True)]):
                return 16
            elif ss == set([("C", True), ("D", False), ("B", True)]):
                return 1
            elif ss == set([("C", False), ("D", True), ("B", True)]):
                return 4
            elif ss == set([("C", False), ("D", False), ("B", True)]):
                return 1
            elif ss == set([("C", True), ("D", True), ("B", False)]):
                return 2
            elif ss == set([("C", True), ("D", False), ("B", False)]):
                return 1
            elif ss == set([("C", False), ("D", True), ("B", False)]):
                return 1
            elif ss == set([("C", False), ("D", False), ("B", False)]):
                return 1
            else:
                raise ValueError("Unknown scope product")

        self.CDB_cf = Factor(
            gid="CDB_cf", scope_vars=set([self.D, self.C, self.B]), factor_fn=phi_cdb
        )

        def phi_cbe(scope_product):
            ""
            ss = set(scope_product)
            if ss == set([("C", True), ("E", True), ("B", True)]):
                return 5
            elif ss == set([("C", True), ("E", False), ("B", True)]):
                return 2
            elif ss == set([("C", False), ("E", True), ("B", True)]):
                return 1
            elif ss == set([("C", False), ("E", False), ("B", True)]):
                return 1
            elif ss == set([("C", True), ("E", True), ("B", False)]):
                return 3
            elif ss == set([("C", True), ("E", False), ("B", False)]):
                return 1
            elif ss == set([("C", False), ("E", True), ("B", False)]):
                return 1
            elif ss == set([("C", False), ("E", False), ("B", False)]):
                return 1
            else:
                raise ValueError("Unknown scope product")

        self.CBE_cf = Factor(
            gid="CBE_cf", scope_vars=set([self.E, self.C, self.B]), factor_fn=phi_cbe
        )

        def phi_be(scope_product):
            ""
            ss = set(scope_product)
            if ss == set([("B", True), ("E", True)]):
                return 1 / 90
            elif ss == set([("B", False), ("E", True)]):
                return 1 / 11
            elif ss == set([("B", True), ("E", False)]):
                return 1 / 39
            elif ss == set([("B", False), ("E", False)]):
                return 1 / 5
            else:
                raise ValueError("Unknown scope product")

        self.BE_cf = Factor(
            gid="BE_cf", scope_vars=set([self.E, self.B]), factor_fn=phi_be
        )

        self.cowell = LWFChainGraph(
            gid="cowell",
            nodes=set(
                [self.A, self.B, self.C, self.D, self.E, self.F, self.G, self.H, self.I]
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
                    self.BE_cf,
                    self.CBE_cf,
                    self.CDB_cf,
                    self.CDF_cf,
                    self.AC_cf,
                    self.AB_cf,
                    self.A_cf,
                    self.DG_cf,
                    self.EF_cf,
                    self.E_cf,
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
            end_node=self.I,
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
            end_node=self.I,
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
            end_node=self.I,
            edge_type=EdgeType.DIRECTED,
        )
        self.koller = LWFChainGraph(
            gid="koller",
            nodes=set([self.A, self.C, self.D, self.E, self.B, self.I, self.F, self.G]),
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

    def test_id(self):
        ""
        self.assertEqual(self.cowell.id(), "cowell")

    def test_nb_chain_components(self):
        ""
        nb = self.cowell.nb_components
        self.assertEqual(nb, 8)

    def test_ccomponents(self):
        ""
        ccomps_nds = set(
            [set(s).pop() for s in self.cowell.ccomponents if isinstance(s, frozenset)]
        )
        ccomps_undi = [
            s for s in self.cowell.ccomponents if isinstance(s, UndiGraph)
        ].pop()
        self.assertEqual(
            ccomps_nds, set([self.A, self.B, self.C, self.E, self.F, self.D, self.G])
        )
        self.assertEqual(ccomps_undi.nodes(), set([self.H, self.I]))

    def test_get_chain_dag(self):
        ""
        dag_comps = self.cowell.dag_components
        self.assertEqual(len(dag_comps.nodes()), 8)

    def test_parents_of_K(self):
        ""
        ccomps_undi = [
            s for s in enumerate(self.cowell.ccomponents) if isinstance(s[1], UndiGraph)
        ].pop()
        parents_k = self.cowell.parents_of_K(ccomps_undi[0])
        self.assertEqual(parents_k, set([self.B, self.D]))
        ccomps_undi = [
            s for s in enumerate(self.koller.ccomponents) if isinstance(s[1], frozenset)
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
                    frozenset([self.I, frozenset([self.H, self.C, self.E])]),
                ]
            ),
        )

    def test_K(self):
        ""
        ccomps_undi = [
            s for s in enumerate(self.cowell.ccomponents) if isinstance(s[1], UndiGraph)
        ]
        cundi = ccomps_undi[0][1]
        hi = self.cowell.K(ccomps_undi[0][0])
        self.assertEqual(hi.nodes(), set([self.H, self.I]))

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
                frozenset([self.C.id(), self.I.id()]),
                frozenset([self.C.id(), self.H.id()]),
                frozenset([self.D.id(), self.E.id()]),
                frozenset([self.D.id(), self.G.id()]),
                frozenset([self.F.id(), self.G.id()]),
                frozenset([self.E.id(), self.I.id()]),
                frozenset([self.B.id(), self.E.id()]),
                frozenset([self.E.id(), self.H.id()]),
                frozenset([self.H.id(), self.I.id()]),
            ]
        )
        medges = moral.edges()
        ms = set([frozenset([m.start().id(), m.end().id()]) for m in medges])
        # [print(m) for m in ms]

        self.assertEqual(
            ms, koller_moralized,
        )

    def test_cond_prod_by_variable_elimination(self):
        """!
        """
        qs = set([self.B])
        evs = set([("E", True), ("A", True), ("G", False)])
        # moral = self.cowell.moralize()
        moral = self.cowell
        pdb.set_trace()
        p, a = moral.cond_prod_by_variable_elimination(qs, evs)
        # check if it is a valid distribution
        s = 0
        for ps in p.factor_domain():
            pss = set(ps)
            f = round(p.phi_normal(pss), 4)
            s += f
            if set([("A", True)]) == pss:
                self.assertEqual(f, 0.01)
            elif set([("A", False)]) == pss:
                self.assertEqual(f, 0.99)
        self.assertTrue(s, 1.0)


if __name__ == "__main__":
    unittest.main()
