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

    def __str__(self):
        return self.id() + "--" + str(self.type())

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, e):
        if isinstance(e, EdgeInfo):
            return self.type() == e.type() and self.id() == e.id()
        return False


class SNodeInfo(AbstractInfo):
    "single node info object"

    def __init__(self, node_id: str, position: NodePosition):
        self.node_id = node_id
        self.pos = position

    def id(self) -> str:
        return self.node_id

    def position(self) -> NodePosition:
        return self.pos

    def __eq__(self, s):
        if isinstance(s, SNodeInfo):
            return s.id() == self.id() and s.position() == self.position()
        return False

    def __hash__(self):
        return hash(self.__str__())

    def __str__(self):
        return self.id() + "--" + str(self.position())


class NodeInfo:
    ""

    def __init__(self, first: SNodeInfo = None, second: SNodeInfo = None):
        self.infos: Tuple[Optional[SNodeInfo], Optional[SNodeInfo]] = (
            first,
            second,
        )

    def __eq__(self, n):
        if isinstance(n, NodeInfo):
            cond1 = self.first() == n.first() or self.first() == n.second()
            cond2 = self.second() == n.first() or self.second() == n.second()
            return cond1 and cond2
        return False

    def __hash__(self):
        return hash(str(self.first()) + str(self.second()))

    def first(self) -> SNodeInfo:
        if self.infos[0] is None:
            raise ValueError("first node info is none")
        return self.infos[0]

    def second(self) -> SNodeInfo:
        if self.infos[1] is None:
            raise ValueError("second node info is none")
        return self.infos[1]

    def set_to_null(self, s: Optional[SNodeInfo]):
        "set value to null"
        if s is None:
            return
        infos: List[Optional[SNodeInfo], Optional[SNodeInfo]] = list(self.infos)
        if self.first_null() is None:
            infos[0] = s
        else:
            infos[1] = s
        self.infos = (infos[0], infos[1])

    def __is_null(self, index: int) -> bool:
        return self.infos[index] is None

    def first_null(self):
        return self.__is_null(0)

    def second_null(self):
        return self.__is_null(1)

    def null_pos(self) -> int:
        if self.first_null() and self.second_null():
            return 2
        elif self.first_null():
            return 0
        elif self.second_null():
            return 1
        else:
            return -1
