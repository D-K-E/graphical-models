"""!
Graph search result
"""
from typing import Callable, Dict, List, Optional, Set, Tuple, Union

from pygmodels.graph.graphtype.abstractobj import (
    AbstractEdge,
    AbstractGraph,
    AbstractNode,
    AbstractSearchResult,
)
from pygmodels.graph.graphtype.graphobj import GraphObject
from pygmodels.utils import is_type
from pygmodels.utils import is_optional_type


class BaseGraphSearchResult(GraphObject, AbstractSearchResult):
    """"""

    def __init__(self, result_id: str, search_name: str, data: Optional[dict]):
        """"""
        super().__init__(oid=result_id, odata=data)
        is_optional_type(search_name, "search_name", str, True)
        self._search_name = search_name

    @property
    def search_name(self) -> str:
        "Search method name"
        if self._search_name is None:
            raise ValueError("No search name is associated to this result")
        return self._search_name

    def __eq__(self, n) -> bool:
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

    def __init__(self, props: dict, result_id: str, search_name: str, data: dict):
        """"""
        super().__init__(result_id=result_id, search_name=search_name, data=data)
        is_type(props, "props", dict, True)
        self.props = props

    @property
    def last_visit_times(self) -> Dict[str, int]:
        return self.props["last-visit-times"]

    @property
    def first_visit_times(self) -> Dict[str, int]:
        return self.props["first-visit-times"]

    @property
    def components(self) -> Dict[str, Set[str]]:
        """"""
        return self.props["components"]

    @property
    def cycle_info(self) -> Dict[str, List[Dict[str, Union[str, int]]]]:
        """"""
        return self.props["cycle-info"]

    @property
    def nb_component(self) -> int:
        return self.props["nb-component"]

    @property
    def trees(self) -> Dict[str, Dict[str, str]]:
        return self.props["dfs-trees"]

    @property
    def forest(self) -> Dict[str, Set[AbstractEdge]]:
        return self.props["dfs-forest"]


class BaseGraphBFSResult(BaseGraphSearchResult):
    """"""

    def __init__(self, props: dict, result_id: str, search_name: str, data: dict):
        """"""
        super().__init__(result_id=result_id, search_name=search_name, data=data)
        is_type(props, "props", dict, True)
        self.props = props

    @property
    def tree(self) -> Dict[str, Dict[str, str]]:
        """"""
        return self.props["bfs-tree"]

    @property
    def path_set(self) -> Set[str]:
        """"""
        return self.props["path-set"]

    @property
    def top_sort(self) -> Dict[str, int]:
        """"""
        return self.props["top-sort"]
