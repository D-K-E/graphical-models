"""!
Test general Graph object
"""
from gmodels.gtypes.graph import Graph
from gmodels.gtypes.node import Node
from gmodels.gtypes.edge import Edge, EdgeType
import unittest
import pprint


class GraphTest(unittest.TestCase):
    ""

    def setUp(self):
        self.n1 = Node("n1", {})
        self.n2 = Node("n2", {})
        self.n3 = Node("n3", {})
        self.n4 = Node("n4", {})
        self.n5 = Node("n5", {})
        self.e1 = Edge(
            "e1", start_node=self.n1, end_node=self.n2, edge_type=EdgeType.UNDIRECTED
        )
        self.e2 = Edge(
            "e2", start_node=self.n2, end_node=self.n3, edge_type=EdgeType.UNDIRECTED
        )
        self.e3 = Edge(
            "e3", start_node=self.n3, end_node=self.n4, edge_type=EdgeType.UNDIRECTED
        )
        self.e4 = Edge(
            "e4", start_node=self.n1, end_node=self.n4, edge_type=EdgeType.UNDIRECTED
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
            "ae", start_node=self.a, end_node=self.e, edge_type=EdgeType.UNDIRECTED
        )
        self.ab = Edge(
            "ab", start_node=self.a, end_node=self.b, edge_type=EdgeType.UNDIRECTED
        )
        self.af = Edge(
            "af", start_node=self.a, end_node=self.f, edge_type=EdgeType.UNDIRECTED
        )
        self.be = Edge(
            "be", start_node=self.b, end_node=self.e, edge_type=EdgeType.UNDIRECTED
        )
        self.ef = Edge(
            "ef", start_node=self.e, end_node=self.f, edge_type=EdgeType.UNDIRECTED
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
            nodes=self.ugraph2.nodes().union(self.graph_2.nodes()),
            edges=self.ugraph2.edges().union(self.graph_2.edges()),
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
            "bb_cc", start_node=self.bb, end_node=self.cc, edge_type=EdgeType.DIRECTED
        )
        self.cc_dd = Edge(
            "cc_dd", start_node=self.cc, end_node=self.dd, edge_type=EdgeType.DIRECTED
        )
        self.dd_ee = Edge(
            "dd_ee", start_node=self.dd, end_node=self.ee, edge_type=EdgeType.DIRECTED
        )
        self.ee_bb = Edge(
            "ee_bb", start_node=self.ee, end_node=self.bb, edge_type=EdgeType.DIRECTED
        )
        self.bb_dd = Edge(
            "bb_dd", start_node=self.bb, end_node=self.dd, edge_type=EdgeType.DIRECTED
        )
        self.dgraph = Graph(
            "g1",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.bb, self.cc, self.dd, self.ee]),
            edges=set([self.bb_cc, self.cc_dd, self.dd_ee, self.ee_bb, self.bb_dd]),
        )

    def test_id(self):
        return self.assertEqual(self.graph.id(), "g1")

    def test_from_edgeset(self):
        ""
        eset = set([self.e1, self.e2, self.e3, self.e4])
        g = Graph.from_edgeset(eset)
        self.assertEqual(g.nodes(), set([self.n1, self.n2, self.n3, self.n4]))
        self.assertEqual(g.edges(), eset)

    def test_has_self_loop(self):
        ""
        n1 = Node("n1", {})
        n2 = Node("n2", {})
        e1 = Edge("e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED)
        e2 = Edge("e2", start_node=n1, end_node=n1, edge_type=EdgeType.UNDIRECTED)
        g1 = Graph("graph", nodes=set([n1, n2]), edges=set([e1, e2]))
        g2 = Graph("graph", nodes=set([n1, n2]), edges=set([e1]))
        self.assertTrue(g1.has_self_loop())
        self.assertFalse(g2.has_self_loop())

    def test_is_node_incident(self):
        ""
        n1 = Node("n1", {})
        n2 = Node("n2", {})
        e1 = Edge("e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED)
        e2 = Edge("e2", start_node=n1, end_node=n1, edge_type=EdgeType.UNDIRECTED)
        self.assertTrue(Graph.is_node_incident(n1, e1))
        self.assertFalse(Graph.is_node_incident(n2, e2))

    def test_adjmat_int(self):
        ""
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
        ""
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
        ""
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

    def test_mk_gdata(self):
        mdata = self.graph.gdata
        gdata = {"n4": [], "n1": ["e1"], "n3": ["e2"], "n2": ["e1", "e2"]}
        for k, vs in mdata.copy().items():
            self.assertEqual(k in mdata, k in gdata)
            for v in vs:
                self.assertEqual(v in mdata[k], v in gdata[k])

    def test_V(self):
        ""
        V = self.graph.V
        nodes = {"n1": self.n1, "n2": self.n2, "n3": self.n3, "n4": self.n4}
        for nid, node in nodes.copy().items():
            self.assertEqual(nid in V, nid in nodes)
            self.assertEqual(V[nid], nodes[nid])

    def test_E(self):
        ""
        E = self.graph.E

        edges = {"e1": self.e1, "e2": self.e2}
        for eid, edge in edges.copy().items():
            self.assertEqual(eid in E, eid in edges)
            self.assertEqual(E[eid], edges[eid])

    def test_is_connected_false(self):
        ""
        self.assertEqual(self.graph.is_connected(), False)

    def test_is_connected_true(self):
        ""
        self.assertTrue(self.graph_2.is_connected())

    def test_is_adjacent_of(self):
        self.assertTrue(self.graph_2.is_adjacent_of(self.e2, self.e3))

    def test_is_neighbour_of_true(self):
        isneighbor = self.graph_2.is_neighbour_of(self.n2, self.n3)
        self.assertTrue(isneighbor)

    def test_is_neighbour_of_false(self):
        isneighbor = self.graph_2.is_neighbour_of(self.n2, self.n2)
        self.assertFalse(isneighbor)

    def test_is_node_independant_of(self):
        self.assertTrue(self.graph_2.is_node_independent_of(self.n1, self.n3))

    def test_neighbours_of(self):
        ndes = set([n.id() for n in self.graph_2.neighbours_of(self.n2)])
        self.assertEqual(ndes, set([self.n1.id(), self.n3.id()]))

    def test_nb_neighbours_of(self):
        ndes = self.graph_2.nb_neighbours_of(self.n2)
        self.assertEqual(ndes, 2)

    def test_is_stable(self):
        ""
        self.assertTrue(self.ugraph4.is_stable(set([self.a, self.n3, self.n1])))

    def test_edges_of(self):
        ""
        edges = self.graph.edges_of(self.n2)
        self.assertEqual(edges, set([self.e1, self.e2]))

    def test_outgoing_edges_of(self):
        ""
        edges = self.graph.outgoing_edges_of(self.n2)
        self.assertEqual(edges, set([self.e2]))

    def test_incoming_edges_of(self):
        ""
        edges = self.graph.incoming_edges_of(self.n2)
        self.assertEqual(edges, set([self.e1]))

    def test_is_in_true(self):
        ""
        b = self.graph.is_in(self.n2)
        self.assertTrue(b)

    def test_is_in_false(self):
        ""
        n = Node("n86", {})
        b = self.graph.is_in(n)
        self.assertFalse(b)

    def test_order(self):
        ""
        b = self.graph.order()
        self.assertEqual(b, 4)

    def test_nb_edges(self):
        ""
        b = self.graph.nb_edges()
        self.assertEqual(b, 2)

    def test_is_trivial(self):
        ""
        b = self.graph.is_trivial()
        self.assertFalse(b)

    def test_is_trivial(self):
        ""
        n = Node("n646", {})
        e = Edge("e8", start_node=self.n1, end_node=n, edge_type=EdgeType.UNDIRECTED)
        check = False
        try:
            gg = Graph(gid="temp", data={}, nodes=set([n]), edges=set([e]))
        except ValueError:
            check = True

        self.assertTrue(check)

    def test_vertex_by_id(self):
        n = self.graph.vertex_by_id("n1")
        self.assertEqual(n, self.n1)

    def test_edge_by_id(self):
        e = self.graph.edge_by_id("e1")
        self.assertEqual(e, self.e1)

    def test_edge_by_vertices(self):
        e = self.graph.edge_by_vertices(self.n2, self.n3)
        self.assertEqual(e, set([self.e2]))

    def test_edge_by_vertices_n(self):
        check = False
        try:
            e = self.graph.edge_by_vertices(self.n1, self.n3)
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_edges_by_end(self):
        ""
        n1 = Node("n1", {})
        n2 = Node("n2", {})
        e1 = Edge("e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED)
        e2 = Edge("e2", start_node=n1, end_node=n1, edge_type=EdgeType.UNDIRECTED)
        g = Graph("g", nodes=set([n1, n2]), edges=set([e1, e2]))
        self.assertEqual(g.edges_by_end(n2), set([e1]))

    def test_vertices_of(self):
        ""
        vertices = self.graph.vertices_of(self.e2)
        self.assertEqual(vertices, (self.n2, self.n3))

    def test_intersection_v(self):
        n = Node("n646", {})

        vset = self.graph.intersection(set([self.n1, n]))
        self.assertEqual(vset, set([self.n1]))

    def test_intersection_e(self):
        n = Node("n646", {})
        e = Edge("e8", start_node=self.n1, end_node=n, edge_type=EdgeType.UNDIRECTED)
        eset = self.graph.intersection(set([self.e1, e]))
        self.assertEqual(eset, set([self.e1]))

    def test_union_v(self):
        n = Node("n646", {})
        e = Edge("e8", start_node=self.n1, end_node=n, edge_type=EdgeType.UNDIRECTED)
        vset = self.graph.union(set([n]))
        self.assertEqual(vset, set([self.n1, self.n2, self.n3, self.n4, n]))

    def test_union_e(self):
        n = Node("n646", {})
        e = Edge("e8", start_node=self.n1, end_node=n, edge_type=EdgeType.UNDIRECTED)
        eset = self.graph.union(set([e]))
        self.assertEqual(eset, set([e, self.e1, self.e2]))

    def test_contains_n(self):
        ""
        nodes = set([self.n2, self.n3])
        contains = self.graph.contains(nodes)
        self.assertTrue(contains)

    def test_contains_e(self):
        ""
        es = set([self.e1, self.e2])
        contains = self.graph.contains(es)
        self.assertTrue(contains)

    def test_contains_g(self):
        ""
        es = set([self.e1])
        g = Graph(gid="temp", data={}, nodes=set([self.n1, self.n2, self.n3]), edges=es)
        contains = self.graph.contains(es)
        self.assertTrue(contains)

    def test_subtract_n(self):
        ""
        gs = self.graph.subtract_node(self.n2)
        nodes = gs.nodes()
        self.assertEqual(nodes, set([self.n1, self.n3, self.n4]))

    def test_subtract_e(self):
        ""
        gs = self.graph.subtract_edge(self.e2)
        edges = gs.edges()
        self.assertEqual(edges, set([self.e1]))

    def test_add_edge(self):
        ""
        g = self.graph.add_edge(self.e3)
        #
        self.assertEqual(self.graph.nodes(), g.nodes())
        self.assertEqual(self.graph_2.edges(), g.edges())

    def test_max_degree(self):
        ""
        md = self.graph.max_degree()
        self.assertEqual(md, 2)

    def test_max_degree_vs(self):
        ""
        mds = self.graph.max_degree_vs()
        self.assertEqual(mds, set([self.n2]))

    def test_min_degree(self):
        ""
        md = self.graph.min_degree()
        self.assertEqual(md, 0)

    def test_min_degree_vs(self):
        ""
        mds = self.graph.min_degree_vs()
        self.assertEqual(mds, set([self.n4]))

    def test_average_degree(self):
        ""
        adeg = self.graph.average_degree()
        self.assertEqual(adeg, 1)

    def test_edge_vertex_ratio(self):
        deg = self.graph.edge_vertex_ratio()
        self.assertEqual(0.5, deg)

    def test_ev_ratio_from_average_degree(self):
        deg = self.graph.ev_ratio_from_average_degree(5)
        self.assertEqual(2.5, deg)

    def test_ev_ratio(self):
        deg = self.graph.ev_ratio()
        self.assertEqual(0.5, deg)

    def test__add__n(self):
        ""
        n = Node("n646", {})
        g = self.graph + n
        self.assertEqual(g.nodes(), set([self.n1, self.n2, self.n3, self.n4, n]))

    def test__add__e(self):
        ""
        n = Node("n646", {})
        e = Edge("e8", start_node=self.n1, end_node=n, edge_type=EdgeType.UNDIRECTED)
        g = self.graph + e
        self.assertEqual(g.edges(), set([e, self.e1, self.e2]))

    def test__add__g(self):
        ""
        n = Node("n646", {})
        n1 = Node("n647", {})
        n2 = Node("n648", {})
        e = Edge("e8", start_node=self.n1, end_node=n, edge_type=EdgeType.UNDIRECTED)
        gg = Graph(gid="temp", data={}, nodes=set([n, n1, n2]), edges=set([e]))
        g = self.graph + gg
        self.assertEqual(g.edges(), set([e, self.e1, self.e2]))
        self.assertEqual(
            g.nodes(), set([self.n1, self.n2, self.n3, self.n4, n, n1, n2])
        )

    def test__sub__n(self):
        ""
        n = Node("n646", {})
        g = self.graph - n
        self.assertEqual(g.nodes(), set([self.n1, self.n2, self.n3, self.n4]))

    def test__sub__e(self):
        ""
        n = Node("n646", {})
        e = Edge("e8", start_node=self.n1, end_node=n, edge_type=EdgeType.UNDIRECTED)
        g = self.graph - e
        self.assertEqual(g.edges(), set([self.e1, self.e2]))

    def test__sub__g(self):
        ""
        n = Node("n646", {})
        n1 = Node("n647", {})
        n2 = Node("n648", {})
        e = Edge("e8", start_node=self.n1, end_node=n, edge_type=EdgeType.UNDIRECTED)
        gg = Graph(gid="temp", data={}, nodes=set([n, n1, n2]), edges=set([e, self.e1]))
        g = self.graph - gg
        self.assertEqual(g.edges(), set([]))
        self.assertEqual(g.nodes(), set([self.n3, self.n4]))

    def test_visit_graph_dfs_nb_component(self):
        "test visit graph dfs function"
        com = self.ugraph1.props["nb-component"]
        com2 = self.ugraph2.props["nb-component"]
        self.assertEqual(com, 2)
        self.assertEqual(com2, 1)

    def test_get_components(self):
        ""
        comps = self.ugraph4.get_components()
        cs = list(comps)
        cs0ns = cs[0].nodes()
        cs0es = cs[0].edges()
        cs1ns = cs[1].nodes()
        cs1es = cs[1].edges()
        cond1 = self.ugraph2.nodes() == cs0ns or self.ugraph2.nodes() == cs1ns
        cond2 = self.graph_2.nodes() == cs0ns or self.graph_2.nodes() == cs1ns
        cond3 = self.ugraph2.edges() == cs0es or self.ugraph2.edges() == cs1es
        cond4 = self.graph_2.edges() == cs0es or self.graph_2.edges() == cs1es
        self.assertTrue(cond1)
        self.assertTrue(cond2)
        self.assertTrue(cond3)
        self.assertTrue(cond4)

    def test_visit_graph_dfs_cycles_false(self):
        "test visit graph dfs function"
        c3 = self.ugraph3.has_cycles()
        self.assertFalse(c3)

    def test_visit_graph_dfs_cycles_true(self):
        "test visit graph dfs function"
        c3 = self.ugraph2.has_cycles()
        self.assertTrue(c3)


if __name__ == "__main__":
    unittest.main()
