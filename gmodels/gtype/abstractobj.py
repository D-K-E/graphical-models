"""
Abstract Node of a graph
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, NewType, Callable, Set
from typing import Union, FrozenSet
from enum import Enum
from collections import namedtuple
from copy import deepcopy


class AbstractInfo(ABC):
    ""

    def __init__(self, *args, **kwargs):
        ""
        self.check_types()

    @abstractmethod
    def id(self) -> str:
        raise NotImplementedError

    def check_types(self) -> bool:
        ""
        ival = self.id()
        if isinstance(ival, str) is False:
            itype = str(type(ival))
            mes = "id() method must return str as type it returns " + itype
            raise TypeError(mes)
        return True


class AbstractGraphObj(AbstractInfo):
    "Abstract graph object"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_types()

    @abstractmethod
    def data(self) -> Dict:
        raise NotImplementedError

    @abstractmethod
    def copy(self):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, n) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError

    def check_types(self) -> bool:
        ""
        s = self.__str__()
        b = self.__eq__()
        d = self.data()
        if isinstance(s, str) is False:
            itype = str(type(s))
            mes = "__str__() method must return str as type it returns " + itype
            raise TypeError(mes)
        if isinstance(b, bool) is False:
            itype = str(type(b))
            mes = "__eq__() method must return bool as type it returns " + itype
            raise TypeError(mes)
        if isinstance(d, dict) is False:
            itype = str(type(d))
            mes = "data() method must return dict as type it returns " + itype
            raise TypeError(mes)
        return True


class EdgeType(Enum):
    DIRECTED = 1
    UNDIRECTED = 2


class AbstractNode(AbstractGraphObj):
    ""


class AbstractEdge(AbstractGraphObj):
    "abstract edge object"

    def __init__(self, *args, **kwargs):
        ""
        super().__init__(*args, **kwargs)
        self.check_types()

    @abstractmethod
    def type(self) -> EdgeType:
        raise NotImplementedError

    @abstractmethod
    def is_start(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_end(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_endvertice(self, n: Union[AbstractNode, str]) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_other(self, n: Union[AbstractNode, str]) -> AbstractNode:
        """!
        \todo Type checking is not done
        """
        raise NotImplementedError

    @abstractmethod
    def node_ids(self) -> FrozenSet[str]:
        raise NotImplementedError

    @abstractmethod
    def start(self) -> AbstractNode:
        raise NotImplementedError

    @abstractmethod
    def end(self) -> AbstractNode:
        raise NotImplementedError

    def check_types(self) -> bool:
        ""
        tv = self.type()
        is_start_b = self.is_start("f")
        is_end_b = self.is_end("f")
        node_ids = self.node_ids()
        sval = self.start()
        endv = self.end()
        ivert = self.is_endvertice("fre")
        if isinstance(tv, EdgeType) is False:
            itype = str(type(tv))
            mes = "type() method must return EdgeType as type it returns " + itype
            raise TypeError(mes)
        if isinstance(is_start_b, bool) is False:
            itype = str(type(is_start_b))
            mes = "is_start() method must return bool as type it returns " + itype
            raise TypeError(mes)
        if isinstance(is_end_b, bool) is False:
            itype = str(type(is_end_b))
            mes = "is_end() method must return bool as type it returns " + itype
            raise TypeError(mes)
        if isinstance(node_ids, frozenset) is False:
            itype = str(type(node_ids))
            mes = "node_ids() method must return frozenset as type it returns " + itype
            raise TypeError(mes)
        n = set(node_ids).pop()
        if isinstance(n, str) is False:
            itype = str(type(n))
            mes = (
                "node_ids() method must return frozenset whose members are"
                + "string as type it returns "
                + itype
            )
            raise TypeError(mes)

        if isinstance(ivert, bool) is False:
            itype = str(type(ivert))
            mes = "is_end() method must return bool as type it returns " + itype
            raise TypeError(mes)

        if isinstance(sval, AbstractNode) is False:
            itype = str(type(sval))
            mes = "start() method must return bool as type it returns " + itype
            raise TypeError(mes)

        if isinstance(endv, AbstractNode) is False:
            itype = str(type(endv))
            mes = "start() method must return bool as type it returns " + itype
            raise TypeError(mes)
        return True


class AbstractGraph(AbstractGraphObj):
    """!
    \brief Abstract Graph interface
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_types()

    @property
    @abstractmethod
    def V(self) -> Dict[str, AbstractNode]:
        raise NotImplementedError

    @property
    @abstractmethod
    def E(self) -> Dict[str, AbstractEdge]:
        raise NotImplementedError

    @abstractmethod
    def is_trivial(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def order(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def is_neighbour_of(self, n1: AbstractNode, n2: AbstractNode) -> bool:
        """!
        \todo type checking not done in check types
        """
        raise NotImplementedError

    def check_types(self) -> bool:
        ""
        vtypes = all(
            [
                isinstance(vid, str) and isinstance(v, AbstractNode)
                for vid, v in self.V.items()
            ]
        )
        etypes = all(
            [
                isinstance(vid, str) and isinstance(v, AbstractEdge)
                for vid, v in self.E.items()
            ]
        )
        itriv = self.is_trivial()
        iorder = self.order()
        if vtypes is False:
            mes = "self.V property must return Dict[str, AbstractNode] it fails "
            mes += " for the following test:\n"
            mes += "[isinstance(vid, str) and isinstance(v, AbstractNode) "
            mes += "for vid, v in self.V.items()]"
            raise TypeError(mes)

        if etypes is False:
            mes = "self.E property must return Dict[str, AbstractEdge] it fails "
            mes += " for the following test:\n"
            mes += "[isinstance(vid, str) and isinstance(v, AbstractEdge) "
            mes += "for vid, v in self.E.items()]"
            raise TypeError(mes)

        if isinstance(itriv, bool) is False:
            itype = str(type(itriv))
            mes = "is_trivial() method must return bool as type it returns " + itype
            raise TypeError(mes)

        if isinstance(iorder, int) is False:
            itype = str(type(iorder))
            mes = "order() method must return int as type it returns " + itype
            raise TypeError(mes)
