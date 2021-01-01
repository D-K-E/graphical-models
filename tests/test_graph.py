"""!
Test general Graph object
"""
from gmodels.graph import Graph
from gmodels.node import Node
from gmodels.edge import Edge, EdgeType
import unittest


class GraphTest(unittest.TestCase):
    ""

    def setUp(self):
        self.n1 = Node("n1", {})
        self.n2 = Node("n2", {})
        self.n3 = Node("n3", {})
        self.n4 = Node("n4", {})
        self.e1 = Edge(
            "e1", start_node=self.n1, end_node=self.n2, edge_type=EdgeType.UNDIRECTED
        )
        self.e2 = Edge(
            "e2", start_node=self.n2, end_node=self.n3, edge_type=EdgeType.UNDIRECTED
        )
        self.e3 = Edge(
            "e3", start_node=self.n3, end_node=self.n4, edge_type=EdgeType.UNDIRECTED
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

    def test_id(self):
        return self.assertEqual(self.graph.id(), "g1")

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
        self.assertEqual(self.graph_2.is_connected(), True)

    def test_is_adjacent_of(self):
        self.assertTrue(self.graph_2.is_adjacent_of(self.e2, self.e3))

    def test_is_neighbour_of_true(self):
        isneighbor = self.graph_2.is_neighbour_of(self.n2, self.n3)
        self.assertTrue(isneighbor)

    def test_is_neighbour_of_false(self):
        isneighbor = self.graph_2.is_neighbour_of(self.n2, self.n2)
        self.assertFalse(isneighbor)

    def test_is_node_independant_of(self):
        self.assertTrue(self.graph_2.is_node_independant_of(self.n1, self.n3))

    def test_is_neighbours_of(self):
        ndes = set([n.id() for n in self.graph_2.neighbours_of(self.n2)])
        self.assertEqual(ndes, set([self.n1.id(), self.n3.id()]))

    def test_edges_of(self):
        ""
        edges = self.graph.edges_of(self.n2)
        self.assertEqual(edges, set([self.e1, self.e2]))

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

    def test_vertex_by_id(self):
        n = self.graph.vertex_by_id("n1")
        self.assertEqual(n, self.n1)

    def test_edge_by_id(self):
        e = self.graph.edge_by_id("e1")
        self.assertEqual(e, self.e1)

    def test_edge_by_vertices(self):
        e = self.graph.edge_by_vertices(self.n2, self.n3)
        self.assertEqual(e, self.e2)

    def test_edge_by_vertices_n(self):
        check = False
        try:
            e = self.graph.edge_by_vertices(self.n1, self.n3)
        except ValueError:
            check = True
        self.assertTrue(check)

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


if __name__ == "__main__":
    unittest.main()
