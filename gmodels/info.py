"""
info objects
"""
from abstractobj import AbstractInfo, EdgeType, NodePosition

from typing import Tuple, Optional


class EdgeInfo(AbstractInfo):
    "edge info object"

    def __init__(self, edge_id: str, etype: EdgeType):
        self.edge_id = edge_id
        self.etype = etype

    def id(self) -> str:
        return self.edge_id

    def type(self) -> EdgeType:
        return self.etype


class SNodeInfo(AbstractInfo):
    "single node info object"

    def __init__(self, node_id: str, position: NodePosition):
        self.node_id = node_id
        self.pos = position

    def id(self) -> str:
        return self.node_id

    def position(self) -> NodePosition:
        return self.pos


class NodeInfo:
    ""

    def __init__(self, first: SNodeInfo = None, second: SNodeInfo = None):
        self.infos: Tuple[Optional[SNodeInfo], Optional[SNodeInfo]] = (
            first,
            second,
        )

    def first(self) -> SNodeInfo:
        if self.infos[0] is None:
            raise ValueError("first node info is none")
        return self.infos[0]

    def second(self) -> SNodeInfo:
        if self.infos[1] is None:
            raise ValueError("second node info is none")
        return self.infos[1]
