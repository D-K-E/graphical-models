"""!
Test Bayesian Network
"""

import pdb
import unittest
from uuid import uuid4

from pygmodels.gmodel.digraph import DiGraph
from pygmodels.gtype.edge import Edge, EdgeType
from pygmodels.pgmodel.bayesian import BayesianNetwork
from pygmodels.factor.factor import Factor
from pygmodels.factor.factorf.factorops import FactorOps
from pygmodels.pgmtype.randomvariable import NumCatRVariable


class BayesianNetworkTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        idata = {
            "rain": {"outcome-values": [True, False]},
            "sprink": {"outcome-values": [True, False]},
            "wet": {"outcome-values": [True, False]},
            "road": {"outcome-values": [True, False]},
            "winter": {"outcome-values": [True, False]},
            "earthquake": {"outcome-values": [True, False]},
            "burglary": {"outcome-values": [True, False]},
            "alarm": {"outcome-values": [True, False]},
        }
        self.rain = NumCatRVariable(
            input_data=idata["rain"],
            node_id="rain",
            marginal_distribution=lambda x: 0.2 if x is True else 0.8,
        )
        self.sprink = NumCatRVariable(
            node_id="sprink",
            input_data=idata["sprink"],
            marginal_distribution=lambda x: 0.6 if x is True else 0.4,
        )
        self.wet = NumCatRVariable(
            node_id="wet",
            input_data=idata["wet"],
            marginal_distribution=lambda x: 0.7 if x is True else 0.3,
        )
        self.rain_wet = Edge(
            edge_id="rain_wet",
            start_node=self.rain,
            end_node=self.wet,
            edge_type=EdgeType.DIRECTED,
        )
        self.rain_sprink = Edge(
            edge_id="rain_sprink",
            start_node=self.rain,
            end_node=self.sprink,
            edge_type=EdgeType.DIRECTED,
        )
        self.sprink_wet = Edge(
            edge_id="sprink_wet",
            start_node=self.sprink,
            end_node=self.wet,
            edge_type=EdgeType.DIRECTED,
        )

        def sprink_rain_factor(scope_product):
            """"""
            sfs = set(scope_product)
            if sfs == set([("rain", True), ("sprink", True)]):
                return 0.01
            elif sfs == set([("rain", True), ("sprink", False)]):
                return 0.99
            elif sfs == set([("rain", False), ("sprink", True)]):
                return 0.4
            elif sfs == set([("rain", False), ("sprink", False)]):
                return 0.6
            else:
                raise ValueError("unknown product")

        self.rain_sprink_f = Factor.from_scope_variables_with_fn(
            svars=set([self.rain, self.sprink]), fn=sprink_rain_factor
        )

        def grass_wet_factor(scope_product):
            """"""
            sfs = set(scope_product)
            if sfs == set([("rain", False), ("sprink", False), ("wet", True)]):
                return 0.0
            elif sfs == set([("rain", False), ("sprink", False), ("wet", False)]):
                return 1.0
            elif sfs == set([("rain", False), ("sprink", True), ("wet", True)]):
                return 0.8
            elif sfs == set([("rain", False), ("sprink", True), ("wet", False)]):
                return 0.2
            elif sfs == set([("rain", True), ("sprink", False), ("wet", True)]):
                return 0.9
            elif sfs == set([("rain", True), ("sprink", False), ("wet", False)]):
                return 0.1
            elif sfs == set([("rain", True), ("sprink", True), ("wet", True)]):
                return 0.99
            elif sfs == set([("rain", True), ("sprink", True), ("wet", False)]):
                return 0.01
            else:
                raise ValueError("unknown product")

        self.grass_wet_f = Factor.from_scope_variables_with_fn(
            svars=set([self.rain, self.sprink, self.wet]), fn=grass_wet_factor
        )

        self.bayes = BayesianNetwork(
            gid="b",
            nodes=set([self.rain, self.sprink, self.wet]),
            edges=set([self.rain_wet, self.rain_sprink, self.sprink_wet]),
            factors=set([self.grass_wet_f, self.rain_sprink_f]),
        )
        #
        # Darwiche 2009, p. 30
        #
        #  Earthquake  Burglary
        #         \    /
        #          \  /
        #         Alarm
        #
        self.EarthquakeN = NumCatRVariable(
            input_data=idata["earthquake"],
            node_id="EarthquakeN",
            marginal_distribution=lambda x: 0.1 if x is True else 0.9,
        )
        self.BurglaryN = NumCatRVariable(
            input_data=idata["burglary"],
            node_id="BurglaryN",
            marginal_distribution=lambda x: 0.2 if x is True else 0.8,
        )
        self.AlarmN = NumCatRVariable(
            input_data=idata["alarm"],
            node_id="AlarmN",
            marginal_distribution=lambda x: 0.2442 if x is True else 0.7558,
        )
        self.burglar_alarm = Edge(
            edge_id="burglar_alarm",
            start_node=self.BurglaryN,
            end_node=self.AlarmN,
            edge_type=EdgeType.DIRECTED,
        )
        self.earthquake_alarm = Edge(
            edge_id="earthquake_alarm",
            start_node=self.EarthquakeN,
            end_node=self.AlarmN,
            edge_type=EdgeType.DIRECTED,
        )

        idata = {"outcome-values": [True, False]}

        self.C = NumCatRVariable(
            node_id="C", input_data=idata, marginal_distribution=lambda x: 0.5
        )
        self.E = NumCatRVariable(
            node_id="E", input_data=idata, marginal_distribution=lambda x: 0.5
        )
        self.F = NumCatRVariable(
            node_id="F", input_data=idata, marginal_distribution=lambda x: 0.5
        )
        self.D = NumCatRVariable(
            node_id="D", input_data=idata, marginal_distribution=lambda x: 0.5
        )
        self.CE = Edge(
            edge_id="CE",
            start_node=self.C,
            end_node=self.E,
            edge_type=EdgeType.DIRECTED,
        )
        self.ED = Edge(
            edge_id="ED",
            start_node=self.E,
            end_node=self.D,
            edge_type=EdgeType.DIRECTED,
        )
        self.EF = Edge(
            edge_id="EF",
            start_node=self.E,
            end_node=self.F,
            edge_type=EdgeType.DIRECTED,
        )

        def phi_c(scope_product):
            ss = set(scope_product)
            if ss == set([("C", True)]):
                return 0.8
            elif ss == set([("C", False)]):
                return 0.2
            else:
                raise ValueError("scope product unknown")

        def phi_ec(scope_product):
            ss = set(scope_product)
            if ss == set([("C", True), ("E", True)]):
                return 0.9
            elif ss == set([("C", True), ("E", False)]):
                return 0.1
            elif ss == set([("C", False), ("E", True)]):
                return 0.7
            elif ss == set([("C", False), ("E", False)]):
                return 0.3
            else:
                raise ValueError("scope product unknown")

        def phi_fe(scope_product):
            ss = set(scope_product)
            if ss == set([("E", True), ("F", True)]):
                return 0.9
            elif ss == set([("E", True), ("F", False)]):
                return 0.1
            elif ss == set([("E", False), ("F", True)]):
                return 0.5
            elif ss == set([("E", False), ("F", False)]):
                return 0.5
            else:
                raise ValueError("scope product unknown")

        def phi_de(scope_product):
            ss = set(scope_product)
            if ss == set([("E", True), ("D", True)]):
                return 0.7
            elif ss == set([("E", True), ("D", False)]):
                return 0.3
            elif ss == set([("E", False), ("D", True)]):
                return 0.4
            elif ss == set([("E", False), ("D", False)]):
                return 0.6
            else:
                raise ValueError("scope product unknown")

        self.CE_f = Factor(
            gid="CE_f", scope_vars=set([self.C, self.E]), factor_fn=phi_ec
        )
        self.C_f = Factor(gid="C_f", scope_vars=set([self.C]), factor_fn=phi_c)
        self.FE_f = Factor(
            gid="FE_f", scope_vars=set([self.F, self.E]), factor_fn=phi_fe
        )
        self.DE_f = Factor(
            gid="DE_f", scope_vars=set([self.D, self.E]), factor_fn=phi_de
        )
        self.bayes_n = BayesianNetwork(
            gid="ba",
            nodes=set([self.C, self.E, self.D, self.F]),
            edges=set([self.EF, self.CE, self.ED]),
            factors=set([self.C_f, self.DE_f, self.CE_f, self.FE_f]),
        )

    def test_id(self):
        """"""
        self.assertEqual("b", self.bayes.id())

    def test_conditional_inference(self):
        """!
        Test inference on bayesian network
        """
        query_vars = set([self.E])
        evidences = set([("F", True)])
        probs, alpha = self.bayes_n.cond_prod_by_variable_elimination(
            query_vars, evidences=evidences
        )
        for ps in FactorOps.cartesian(probs):
            pss = set(ps)
            ff = round(probs.phi(pss), 4)
            if set([("E", True)]) == pss:
                self.assertEqual(ff, 0.774)

    def test_from_digraph_with_factors(self):
        """!
        Values from Darwiche 2009, p. 132, figure 6.4
        """
        A = NumCatRVariable(
            "A",
            input_data={"outcome-values": [True, False]},
            marginal_distribution=lambda x: 0.6 if x else 0.4,
        )
        B = NumCatRVariable(
            "B",
            input_data={"outcome-values": [True, False]},
            marginal_distribution=lambda x: 0.62 if x else 0.38,
        )
        C = NumCatRVariable(
            "C",
            input_data={"outcome-values": [True, False]},
            marginal_distribution=lambda x: 0.624 if x else 0.376,
        )
        AB_Edge = Edge(
            edge_id="ab_edge", start_node=A, end_node=B, edge_type=EdgeType.DIRECTED,
        )
        BC_Edge = Edge(
            edge_id="bc_edge", start_node=B, end_node=C, edge_type=EdgeType.DIRECTED,
        )

        def phi_a(scope_product):
            """"""
            ss = set(scope_product)
            if ss == set([("A", True)]):
                return 0.6
            elif ss == set([("A", False)]):
                return 0.4
            else:
                raise ValueError("unknown argument")

        def phi_ab(scope_product):
            ss = set(scope_product)
            if ss == set([("A", True), ("B", True)]):
                return 0.9
            elif ss == set([("A", True), ("B", False)]):
                return 0.1
            elif ss == set([("A", False), ("B", True)]):
                return 0.2
            elif ss == set([("A", False), ("B", False)]):
                return 0.8
            else:
                raise ValueError("unknown argument")

        def phi_bc(scope_product):
            ss = set(scope_product)
            if ss == set([("C", True), ("B", True)]):
                return 0.3
            elif ss == set([("C", True), ("B", False)]):
                return 0.5
            elif ss == set([("C", False), ("B", True)]):
                return 0.7
            elif ss == set([("C", False), ("B", False)]):
                return 0.5
            else:
                raise ValueError("unknown argument")

        A_f = Factor(gid="A_f", scope_vars=set([A]), factor_fn=phi_a)
        AB_f = Factor(gid="AB_f", scope_vars=set([A, B]), factor_fn=phi_ab)
        BC_f = Factor(gid="BC_f", scope_vars=set([C, B]), factor_fn=phi_bc)
        dig = DiGraph(gid="temp", nodes=set([A, B, C]), edges=set([AB_Edge, BC_Edge]))
        factors = set([A_f, AB_f, BC_f])
        bn = BayesianNetwork(
            gid="temp",
            nodes=set([A, B, C]),
            edges=set([AB_Edge, BC_Edge]),
            factors=set([A_f, AB_f, BC_f]),
        )
        q = set([B])
        evidence = set([])
        foo, a = bn.cond_prod_by_variable_elimination(queries=q, evidences=evidence)
        bayes = BayesianNetwork.from_digraph(dig, factors)
        foo2, a2 = bayes.cond_prod_by_variable_elimination(
            queries=q, evidences=evidence
        )
        f1 = set([("B", False)])
        self.assertEqual(foo.phi(f1), foo2.phi(f1))
        f1 = set([("B", True)])
        self.assertEqual(foo.phi(f1), foo2.phi(f1))

    @unittest.skip("Factor.from_conditional_vars not yet implemented")
    def test_deduce_factors_from_digraph(self):
        """"""
        pass


if __name__ == "__main__":
    unittest.main()
