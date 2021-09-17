"""!
Test general Graph object
"""
import cProfile
import unittest

# profiler related
from pstats import Stats

from pygmodels.gmodel.graph import Graph
from pygmodels.graphf.bgraphops import BaseGraphOps
from pygmodels.graphf.bgraphops import BaseGraphNodeOps
from pygmodels.graphf.bgraphops import BaseGraphEdgeOps
from pygmodels.graphf.bgraphops import BaseGraphBoolOps
from pygmodels.graphf.graphanalyzer import BaseGraphAnalyzer
from pygmodels.graphf.graphanalyzer import BaseGraphBoolAnalyzer
from pygmodels.graphf.graphanalyzer import BaseGraphNumericAnalyzer
from pygmodels.graphf.graphops import BaseGraphAlgOps, BaseGraphSetOps
from pygmodels.gtype.edge import Edge, EdgeType
from pygmodels.gtype.node import Node


class GraphTest(unittest.TestCase):
    """"""

    def setUp(self):
        self.verbose = False
        self.n1 = Node("n1", {})
        self.n2 = Node("n2", {})
        self.n3 = Node("n3", {})
        self.n4 = Node("n4", {})
        self.n5 = Node("n5", {})
        self.e1 = Edge(
            "e1", start_node=self.n1, end_node=self.n2, edge_type=EdgeType.UNDIRECTED,
        )
        self.e2 = Edge(
            "e2", start_node=self.n2, end_node=self.n3, edge_type=EdgeType.UNDIRECTED,
        )
        self.e3 = Edge(
            "e3", start_node=self.n3, end_node=self.n4, edge_type=EdgeType.UNDIRECTED,
        )
        self.e4 = Edge(
            "e4", start_node=self.n1, end_node=self.n4, edge_type=EdgeType.UNDIRECTED,
        )

        self.graph = Graph(
            "g1",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e1, self.e2]),
        )
        self.graph_2 = Graph(
            "g2",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e1, self.e2, self.e3]),
        )
        #
        self.a = Node("a", {})  # b
        self.b = Node("b", {})  # c
        self.f = Node("f", {})  # d
        self.e = Node("e", {})  # e
        self.ae = Edge(
            "ae", start_node=self.a, end_node=self.e, edge_type=EdgeType.UNDIRECTED,
        )
        self.ab = Edge(
            "ab", start_node=self.a, end_node=self.b, edge_type=EdgeType.UNDIRECTED,
        )
        self.af = Edge(
            "af", start_node=self.a, end_node=self.f, edge_type=EdgeType.UNDIRECTED,
        )
        self.be = Edge(
            "be", start_node=self.b, end_node=self.e, edge_type=EdgeType.UNDIRECTED,
        )
        self.ef = Edge(
            "ef", start_node=self.e, end_node=self.f, edge_type=EdgeType.UNDIRECTED,
        )

        # undirected graph
        self.ugraph1 = Graph(
            "ug1",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.a, self.b, self.e, self.f]),
            edges=set(
                [
                    self.ae,
                    # self.ab,
                    self.af,
                    # self.be,
                    self.ef,
                ]
            ),
        )
        # ugraph1:
        #   +-----+
        #  /       \
        # a    b    e
        #  \       /
        #   +-----f

        self.ugraph2 = Graph(
            "ug2",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.a, self.b, self.e, self.f]),
            edges=set([self.ae, self.ab, self.af, self.be, self.ef,]),
        )
        # ugraph2 :
        #   +-----+
        #  /       \
        # a -- b -- e
        #  \       /
        #   +-----f

        self.ugraph3 = Graph(
            "ug3",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.a, self.b, self.e, self.f]),
            edges=set(
                [
                    self.ab,
                    # self.af,
                    self.be,
                ]
            ),
        )
        # ugraph3 :
        #
        #
        # a -- b -- e
        #  \
        #   +-----f

        self.ugraph4 = Graph(
            "ug4",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set(
                [self.a, self.b, self.e, self.f, self.n1, self.n2, self.n3, self.n4,]
            ),
            edges=set(
                [
                    self.ab,
                    self.af,
                    self.ae,
                    self.be,
                    self.ef,
                    self.e1,
                    self.e2,
                    self.e3,
                    self.e4,
                ]
            ),
        )
        # ugraph 4
        #   +-----+     n1 -- n2 -- n3 -- n4
        #  /       \     \                /
        # a -- b -- e     +--------------+
        #  \       /
        #   +-----f

        # make some directed edges
        self.bb = Node("bb", {})
        self.cc = Node("cc", {})
        self.dd = Node("dd", {})
        self.ee = Node("ee", {})

        self.bb_cc = Edge(
            "bb_cc", start_node=self.bb, end_node=self.cc, edge_type=EdgeType.DIRECTED,
        )
        self.cc_dd = Edge(
            "cc_dd", start_node=self.cc, end_node=self.dd, edge_type=EdgeType.DIRECTED,
        )
        self.dd_ee = Edge(
            "dd_ee", start_node=self.dd, end_node=self.ee, edge_type=EdgeType.DIRECTED,
        )
        self.ee_bb = Edge(
            "ee_bb", start_node=self.ee, end_node=self.bb, edge_type=EdgeType.DIRECTED,
        )
        self.bb_dd = Edge(
            "bb_dd", start_node=self.bb, end_node=self.dd, edge_type=EdgeType.DIRECTED,
        )
        self.dgraph = Graph(
            "g1",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.bb, self.cc, self.dd, self.ee]),
            edges=set([self.bb_cc, self.cc_dd, self.dd_ee, self.ee_bb, self.bb_dd]),
        )

        # initialize profiler
        self.prof = cProfile.Profile()
        self.prof.enable()
        # print("\n<<<<--------")

    def tearDown(self):
        """ """
        p = Stats(self.prof)
        p.sort_stats("cumtime")
        if self.verbose is True:
            p.dump_stats("profiles/test_graph.py.prof")
            p.print_stats()
        p.strip_dirs()
        # p.print_stats()
        # print("\n--------->>>")

    def test_id(self):
        return self.assertEqual(self.graph.id(), "g1")

    def test_from_edgeset(self):
        """"""
        eset = set([self.e1, self.e2, self.e3, self.e4])
        g = Graph.from_edgeset(eset)
        self.assertEqual(set(g.V), set([self.n1, self.n2, self.n3, self.n4]))
        self.assertEqual(BaseGraphEdgeOps.edges(g), eset)

   
    def test_adjmat_int(self):
        """"""
        mat = self.ugraph1.to_adjmat()
        self.assertEqual(
            mat,
            {
                ("b", "b"): 0,
                ("b", "e"): 0,
                ("b", "f"): 0,
                ("b", "a"): 0,
                ("e", "b"): 0,
                ("e", "e"): 0,
                ("e", "f"): 1,
                ("e", "a"): 1,
                ("f", "b"): 0,
                ("f", "e"): 1,
                ("f", "f"): 0,
                ("f", "a"): 1,
                ("a", "b"): 0,
                ("a", "e"): 1,
                ("a", "f"): 1,
                ("a", "a"): 0,
            },
        )

    def test_adjmat_bool(self):
        """"""
        mat = self.ugraph1.to_adjmat(vtype=bool)
        self.assertEqual(
            mat,
            {
                ("b", "b"): False,
                ("b", "e"): False,
                ("b", "f"): False,
                ("b", "a"): False,
                ("e", "b"): False,
                ("e", "e"): False,
                ("e", "f"): True,
                ("e", "a"): True,
                ("f", "b"): False,
                ("f", "e"): True,
                ("f", "f"): False,
                ("f", "a"): True,
                ("a", "b"): False,
                ("a", "e"): True,
                ("a", "f"): True,
                ("a", "a"): False,
            },
        )

    def test_transitive_closure_mat(self):
        """"""
        mat = self.ugraph1.transitive_closure_matrix()
        self.assertEqual(
            mat,
            {
                ("a", "b"): True,
                ("a", "e"): True,
                ("a", "f"): True,
                ("b", "a"): False,
                ("b", "e"): False,
                ("b", "f"): False,
                ("e", "a"): True,
                ("e", "b"): True,
                ("e", "f"): True,
                ("f", "a"): True,
                ("f", "b"): True,
                ("f", "e"): True,
            },
        )

    def test_equal(self):
        n1 = Node("n1", {})
        n2 = Node("n2", {})
        n3 = Node("n3", {})
        n4 = Node("n4", {})
        e1 = Edge("e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED)
        e2 = Edge("e2", start_node=n2, end_node=n3, edge_type=EdgeType.UNDIRECTED)
        graph = Graph("g1", data={}, nodes=set([n1, n2, n3, n4]), edges=set([e1, e2]))
        self.assertEqual(graph, self.graph)

    def test_is_connected_false(self):
        """"""
        self.assertEqual(self.graph.is_connected(), False)

    def test_is_connected_true(self):
        """"""
        self.assertTrue(self.graph_2.is_connected())

    def test_is_neighbour_of_true(self):
        isneighbor = self.graph_2.is_neighbour_of(self.n2, self.n3)
        self.assertTrue(isneighbor)

    def test_is_neighbour_of_false(self):
        isneighbor = self.graph_2.is_neighbour_of(self.n2, self.n2)
        self.assertFalse(isneighbor)

    def test_neighbours_of(self):
        ndes = set(
            [n.id() for n in BaseGraphNodeOps.neighbours_of(self.graph_2, self.n2)]
        )
        self.assertEqual(ndes, set([self.n1.id(), self.n3.id()]))

    def test_nb_neighbours_of(self):
        ndes = BaseGraphNumericAnalyzer.nb_neighbours_of(self.graph_2, self.n2)
        self.assertEqual(ndes, 2)

    def test__add__n(self):
        """"""
        n = Node("n646", {})
        g = self.graph + n
        self.assertEqual(set(g.V), set([self.n1, self.n2, self.n3, self.n4, n]))

    def test__add__e(self):
        """"""
        n = Node("n646", {})
        e = Edge("e8", start_node=self.n1, end_node=n, edge_type=EdgeType.UNDIRECTED)
        g = self.graph + e
        self.assertEqual(set(g.E), set([e, self.e1, self.e2]))

    def test__add__g(self):
        """"""
        n = Node("n646", {})
        n1 = Node("n647", {})
        n2 = Node("n648", {})
        e = Edge("e8", start_node=self.n1, end_node=n, edge_type=EdgeType.UNDIRECTED)
        gg = Graph(gid="temp", data={}, nodes=set([n, n1, n2]), edges=set([e]))
        g = self.graph + gg
        self.assertEqual(
            set(g.V), set([self.n1, self.n2, self.n3, self.n4, n, n1, n2]),
        )
        self.assertEqual(set(g.E), set([e, self.e1, self.e2]))

    def test__sub__n(self):
        """"""
        n = Node("n646", {})
        g = self.graph - n
        self.assertEqual(set(g.V), set([self.n1, self.n2, self.n3, self.n4]))

    def test__sub__e(self):
        """"""
        n = Node("n646", {})
        e = Edge("e8", start_node=self.n1, end_node=n, edge_type=EdgeType.UNDIRECTED)
        g = self.graph - e
        self.assertEqual(set(g.E), set([self.e1, self.e2]))

    def test__sub__g(self):
        """"""
        n = Node("n646", {})
        n1 = Node("n647", {})
        n2 = Node("n648", {})
        e = Edge("e8", start_node=self.n1, end_node=n, edge_type=EdgeType.UNDIRECTED)
        gg = Graph(
            gid="temp", data={}, nodes=set([n, n1, n2]), edges=set([e, self.e1]),
        )
        g = self.graph - gg
        self.assertEqual(set(g.E), set([]))
        self.assertEqual(set(g.V), set([self.n3, self.n4]))

    def test_visit_graph_dfs_nb_component(self):
        "test visit graph dfs function"
        com = self.ugraph1.graph_props.nb_component
        com2 = self.ugraph2.graph_props.nb_component
        self.assertEqual(com, 2)
        self.assertEqual(com2, 1)

    def test_get_components(self):
        """"""
        comps = self.ugraph4.get_components()
        cs = list(comps)
        cs0ns = set(cs[0].V)
        cs0es = set(cs[0].E)
        #
        cs1ns = set(cs[1].V)
        cs1es = set(cs[1].E)
        #
        # compare graphs
        # first component
        u2nodes = set([self.a, self.b, self.e, self.f])
        u2edges = set([self.ab, self.af, self.ae, self.be, self.ef])

        # second component
        g2node = set([self.n1, self.n2, self.n3, self.n4])
        g2edge = set([self.e1, self.e2, self.e3, self.e4])
        #
        cond1 = u2nodes == cs0ns or u2nodes == cs1ns
        #
        cond2 = g2node == cs0ns or g2node == cs1ns
        #
        cond3 = u2edges == cs0es or u2edges == cs1es
        cond4 = g2edge == cs0es or g2edge == cs1es
        self.assertTrue(cond1)
        self.assertTrue(cond2)
        self.assertTrue(cond3)
        self.assertTrue(cond4)

    def test_visit_graph_dfs_cycles_false(self):
        "test visit graph dfs function"
        c3 = BaseGraphBoolAnalyzer.has_cycles(self.ugraph3)
        self.assertFalse(c3)

    def test_visit_graph_dfs_cycles_true(self):
        "test visit graph dfs function"
        c3 = BaseGraphBoolAnalyzer.has_cycles(self.ugraph2)
        self.assertTrue(c3)


def suite():
    """"""
    s = unittest.TestSuite()
    s.addTest(GraphTest("Graph Object Tests", verbosity=2))
    return s


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    # runner.run(suite())
    unittest.main()
