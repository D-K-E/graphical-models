"""!
Test Bayesian Network
"""

from gmodels.bayesian import BayesianNetwork
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.factor import Factor
from gmodels.randomvariable import NumCatRVariable
from uuid import uuid4

import unittest


class BayesianNetworkTest(unittest.TestCase):
    ""

    def setUp(self):
        ""
        idata = {
            "rain": {"outcome-values": [True, False]},
            "sprink": {"outcome-values": [True, False]},
            "wet": {"outcome-values": [True, False]},
        }
        self.rain = NumCatRVariable(
            input_data=idata["rain"],
            node_id="rain",
            distribution=lambda x: 0.2 if x is True else 0.8,
        )
        self.sprink = NumCatRVariable(
            node_id="sprink",
            input_data=idata["sprink"],
            distribution=lambda x: 0.6 if x is True else 0.4,
        )
        self.wet = NumCatRVariable(
            node_id="wet",
            input_data=idata["wet"],
            distribution=lambda x: 0.7 if x is True else 0.3,
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
            ""
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

        self.rain_sprink_f = Factor.from_conditional_vars(
            X_i=self.sprink, Pa_Xi=set([self.rain]), fn=sprink_rain_factor
        )

        def grass_wet_factor(scope_product):
            ""
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

        self.grass_wet_f = Factor.from_conditional_vars(
            X_i=self.wet, Pa_Xi=set([self.rain, self.sprink]), fn=grass_wet_factor
        )

        self.bayes = BayesianNetwork(
            gid="b",
            nodes=set([self.rain, self.sprink, self.wet]),
            edges=set([self.rain_wet, self.rain_sprink, self.sprink_wet]),
            factors=set([self.grass_wet_f, self.rain_sprink_f]),
        )

    def test_id(self):
        ""
        self.assertEqual("b", self.bayes.id())

    def test_conditional_inference(self):
        """!
        Test inference on bayesian network
        """
        query_vars = set([self.wet])
        evidences = set([("sprink", True)])
        vs, alpha = self.bayes.cond_prod_by_variable_elimination(
            query_vars, evidences=evidences
        )
        v = vs.phi_normal(vals)
        a = alpha.phi(vals)
        print(round(v, 5))
        print(round(a, 5))
        print(round(v / a, 5))


if __name__ == "__main__":
    unittest.main()
