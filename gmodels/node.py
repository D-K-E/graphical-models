"""
Node in a graph
"""
from typing import Dict, Set, Tuple, Optional
from abstractobj import AbstractNode, AbstractEdge, EdgeType
from abstractobj import NodePosition
from info import EdgeInfo
from graphobj import GraphObject


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
