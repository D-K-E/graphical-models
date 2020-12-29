"""
Node in a graph
"""
from typing import Dict, Set, Tuple, Optional
from gmodels.abstractobj import AbstractNode, AbstractEdge, EdgeType
from gmodels.abstractobj import NodePosition
from gmodels.info import EdgeInfo
from gmodels.graphobj import GraphObject


class Node(AbstractNode, GraphObject):
    "A simple node in a graph"

    def __init__(
        self,
        node_id: str,
        data={},
        edge_infos: Dict[str, Tuple[EdgeType, NodePosition]] = None,
    ):
        "constructor for a node"
        super().__init__(oid=node_id, odata=data)
        self.edge_info: Optional[
            Dict[str, Tuple[EdgeType, NodePosition]]
        ] = edge_infos  # {edge_id: edge type}

    def __eq__(self, n):
        if isinstance(n, Node):
            return self.id() == n.id()
        return False

    def __str__(self):
        ""
        return self.id() + "--" + str(self.data()) + "--" + str(self.info())

    def __hash__(self):
        return hash(self.__str__())

    def is_incident(self, info: EdgeInfo) -> bool:
        "node is incident with edge"
        eid = info.id()
        return eid in self.edges

    def nb_edges(self):
        return len(self.edges)

    def has_edges(self):
        return self.nb_edges() > 0

    def info(self) -> Dict[str, Tuple[EdgeType, NodePosition]]:
        if self.edge_info is None:
            raise ValueError("edge info for the node: " + self.id() + " is None")
        return self.edge_info

    def edge_ids(self) -> Set[str]:
        return set(list(self.info().keys()))

    def position_in(self, edge_id: str) -> NodePosition:
        ""
        edge_info = self.info()
        info = edge_info[edge_id]
        return info[1]
