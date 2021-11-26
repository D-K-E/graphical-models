"""!
Graph search result
"""
from typing import Callable, Dict, List, Optional, Set, Tuple, Union

from pygmodels.graph.gtype.abstractobj import (
    AbstractEdge,
    AbstractGraph,
    AbstractNode,
    AbstractSearchResult,
)
from pygmodels.graph.gtype.graphobj import GraphObject


class BaseGraphSearchResult(GraphObject, AbstractSearchResult):
    """"""

    def __init__(
        self, result_id: str, search_name: str, data: dict, *args, **kwargs
    ):
        """"""
        super().__init__(oid=result_id, odata=data)

        if search_name is None:
            raise ValueError("No search name is associated to this result")
        self._search_name = search_name

    @property
    def search_name(self) -> str:
        "Search method name"
        if self._search_name is None:
            raise ValueError("No search name is associated to this result")
        return self._search_name

    def __eq__(self, n):
        """"""
        if isinstance(n, BaseGraphSearchResult):
            return self.id() == n.id()
        return False

    def __str__(self) -> str:
        """"""
        return "BaseGraphSearchResult: " + self.id() + " " + self.search_name

    def __hash__(self):
        return hash(self.id())


class BaseGraphDFSResult(BaseGraphSearchResult):
    """"""

    def __init__(
        self,
        props: dict,
        result_id: str,
        search_name: str,
        data: dict,
        *args,
        **kwargs
    ):
        """"""
        super().__init__(
            result_id=result_id,
            search_name=search_name,
            data=data,
            *args,
            **kwargs
        )
        self.props = props

    @property
    def last_visit_times(self):
        return self.props["last-visit-times"]

    @property
    def first_visit_times(self):
        return self.props["first-visit-times"]

    @property
    def components(self):
        return self.props["components"]

    @property
    def cycle_info(self):
        return self.props["cycle-info"]

    @property
    def nb_component(self):
        return self.props["nb-component"]

    @property
    def trees(self) -> dict:
        return self.props["dfs-trees"]

    @property
    def forest(self):
        return self.props["dfs-forest"]


class BaseGraphBFSResult(BaseGraphSearchResult):
    def __init__(
        self,
        props: dict,
        result_id: str,
        search_name: str,
        data: dict,
        *args,
        **kwargs
    ):
        """"""
        super().__init__(
            result_id=result_id,
            search_name=search_name,
            data=data,
            *args,
            **kwargs
        )
        self.props = props

    @property
    def tree(self):
        return self.props["bfs-tree"]

    @property
    def path_set(self):
        return self.props["path-set"]

    @property
    def top_sort(self):
        return self.props["top-sort"]
