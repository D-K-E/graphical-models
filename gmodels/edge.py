"""
Edge in a graph
"""
from typing import Set
from abstractobj import AbstractNode, AbstractEdge, EdgeType
from info import NodeInfo, EdgeInfo
from graphobj import GraphObject


class Edge(AbstractEdge, GraphObject):
    "Simple edge in a graph"

    def __init__(
        self,
        edge_id: str,
        edge_type: EdgeType = EdgeType.UNDIRECTED,
        data={},
        node_info: NodeInfo = None,
    ):
        "simple edge constructor"
        super().__init__(oid=edge_id, odata=data)
        self.etype = edge_type
        self.node_info = node_info

    def info(self) -> NodeInfo:
        return self.node_info

    def node_ids(self) -> Set[str]:
        ""
        ids = set()
        info = self.info()
        ids.add(info.first().id())
        ids.add(info.second().id())
        return ids

    def edge_info(self) -> EdgeInfo:
        "extract edge info from edge"
        return EdgeInfo(edge_id=self.id(), etype=self.type())

    def is_endvertice(self, n: AbstractNode) -> bool:
        "check if node is an end vertex"
        info = self.info()
        return info.first().id() == n.id() or info.second().id() == n.id()
