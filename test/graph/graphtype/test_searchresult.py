"""
\brief searchresult.py tests
"""
import unittest

from pygmodels.graph.graphtype.searchresult import BaseGraphSearchResult
from pygmodels.graph.graphtype.searchresult import BaseGraphDFSResult
from pygmodels.graph.graphtype.searchresult import BaseGraphBFSResult
from pygmodels.graph.graphtype.edge import Edge
from pygmodels.graph.graphtype.node import Node
from pygmodels.utils import is_type
from pygmodels.utils import is_dict_type
from pygmodels.utils import is_all_type


class BaseGraphSearchResultTest(unittest.TestCase):
    """"""

    def setUp(self):
        self.b1_result = BaseGraphSearchResult(
            result_id="foo", search_name="bar", data={}
        )

    def test_base_result(self):
        """"""
        self.assertEqual(self.b1_result.search_name, "bar")


class DfsGraphSearchResultTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        n1 = Node(node_id="n1")
        n2 = Node(node_id="n2")
        e1 = Edge.directed(eid="e1", start_node=n1, end_node=n2)
        self.b2_result = BaseGraphDFSResult(
            props={
                "last-visit-times": dict(n1=1),
                "first-visit-times": dict(n2=2, n1=0),
                "components": dict(comps=set(["foo", "bar"])),
                "cycle-info": dict(cyc=[dict(bar=1)]),
                "nb-component": 1,
                "dfs-trees": dict(foo=dict(bar="baz")),
                "dfs-forest": dict(foo=set([e1])),
            },
            result_id="foo",
            search_name="bar",
            data={},
        )
        self.b3_result = BaseGraphBFSResult(
            props={
                "bfs-tree": dict(n1=n2),
                "path-set": set(["n1"]),
                "top-sort": dict(n1=0, n2=1),
            },
            result_id="foo",
            search_name="bar",
            data={},
        )

    def test_dfs_result_last_visit_times(self):
        """"""
        self.assertTrue(
            is_dict_type(
                self.b2_result.last_visit_times, "last_visit_times", str, int, False
            )
        )

    def test_dfs_result_first_visit_times(self):
        """"""
        self.assertTrue(
            is_dict_type(
                self.b2_result.first_visit_times, "first_visit_times", str, int, False
            )
        )

    def test_dfs_result_components(self):
        """"""
        self.assertTrue(
            is_dict_type(self.b2_result.components, "components", str, set, False)
        )

    def test_dfs_result_cycle_info(self):
        """"""
        self.assertTrue(
            is_dict_type(self.b2_result.cycle_info, "cycle_info", str, list, False)
        )

    def test_dfs_result_nb_component(self):
        """"""
        self.assertTrue(
            is_type(self.b2_result.nb_component, "nb_component", int, False)
        )

    def test_dfs_result_dfs_trees(self):
        """"""
        self.assertTrue(is_dict_type(self.b2_result.trees, "trees", str, dict, False))

    def test_dfs_result_dfs_forest(self):
        """"""
        self.assertTrue(is_dict_type(self.b2_result.forest, "forest", str, set, False))


class BfsGraphSearchResultTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        n1 = Node(node_id="n1")
        n2 = Node(node_id="n2")
        e1 = Edge.directed(eid="e1", start_node=n1, end_node=n2)

        self.b3_result = BaseGraphBFSResult(
            props={
                "bfs-tree": {"n1": {"n2": "n3"}},
                "path-set": set(["n1"]),
                "top-sort": dict(n1=0, n2=1),
            },
            result_id="foo",
            search_name="bar",
            data={},
        )

    def test_bfs_result_tree(self):
        """"""
        self.assertTrue(is_dict_type(self.b3_result.tree, "tree", str, dict, False))

    def test_bfs_result_path_set(self):
        """"""
        self.assertTrue(is_type(self.b3_result.path_set, "path_set", set, False))
        self.assertTrue(is_all_type(self.b3_result.path_set, "path_set", str, False))

    def test_bfs_result_top_sort(self):
        """"""
        self.assertTrue(
            is_dict_type(self.b3_result.top_sort, "top_sort", str, int, False)
        )


if __name__ == "__main__":
    unittest.main()
