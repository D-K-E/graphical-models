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
            factors=None,
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
        self.AF_k = Edge(
            edge_id="AF",
            start_node=self.A,
            end_node=self.F,
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
                    self.AF_k,
                    self.FG_k,
                    self.HI_k,
                    self.CD_k,
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
            [s for s in self.cowell.ccomponents if isinstance(s, NumCatRVariable)]
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
        [print(p) for p in parents_k]

    # self.assertEqual(parents_k, set([
    #    ]))


if __name__ == "__main__":
    unittest.main()
