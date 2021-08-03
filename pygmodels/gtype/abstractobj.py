"""
Abstract Node of a graph
"""
from abc import ABC, abstractmethod
from collections import namedtuple
from copy import deepcopy
from enum import Enum
from typing import (
    Callable,
    Dict,
    FrozenSet,
    List,
    NewType,
    Optional,
    Set,
    Tuple,
    Union,
)


def type_check_msg(ival, itype, mname: str):
    """"""
    if isinstance(ival, itype) is False:
        itype2 = str(type(ival))
        mes = (
            mname
            + "() method must return "
            + itype.__name__
            + " as type, but it returns "
            + itype2
        )
        raise TypeError(mes)


class AbstractInfo(ABC):
    """"""

    def __init__(self, *args, **kwargs):
        """"""
        self.check_types()

    @abstractmethod
    def id(self) -> str:
        raise NotImplementedError

    def check_types(self) -> bool:
        """"""
        ival = self.id()
        type_check_msg(ival, str, "id")
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
        """"""
        s = self.__str__()
        b = self.__eq__()
        d = self.data()
        type_check_msg(s, str, "__str__")
        type_check_msg(b, bool, "__eq__")
        type_check_msg(d, dict, "data")
        return True


class EdgeType(Enum):
    DIRECTED = 1
    UNDIRECTED = 2


class AbstractNode(AbstractGraphObj):
    """"""


class AbstractEdge(AbstractGraphObj):
    "abstract edge object"

    def __init__(self, *args, **kwargs):
        """"""
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
        """"""
        tv = self.type()
        type_check_msg(tv, EdgeType, "type")

        is_start_b = self.is_start("f")
        type_check_msg(is_start_b, bool, "is_start")

        is_end_b = self.is_end("f")
        type_check_msg(is_end_b, bool, "is_end")

        node_ids = self.node_ids()
        type_check_msg(node_ids, frozenset, "node_ids")
        n = set(node_ids).pop()
        if isinstance(n, str) is False:
            itype = str(type(n))
            mes = (
                "node_ids() method must return frozenset whose members are"
                + "string as type it returns "
                + itype
            )
            raise TypeError(mes)

        ivert = self.is_endvertice("fre")
        type_check_msg(ivert, bool, "is_endvertice")

        sval = self.start()
        type_check_msg(sval, AbstractNode, "start")

        endv = self.end()
        type_check_msg(endv, AbstractNode, "end")
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
    def V(self) -> FrozenSet[AbstractNode]:
        raise NotImplementedError

    @property
    @abstractmethod
    def E(self) -> FrozenSet[AbstractEdge]:
        raise NotImplementedError

    @abstractmethod
    def is_neighbour_of(self, n1: AbstractNode, n2: AbstractNode) -> bool:
        """!
        \todo type checking not done in check types
        """
        raise NotImplementedError

    def check_types(self) -> bool:
        """"""
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
        if vtypes is False:
            mes = (
                "self.V property must return Dict[str, AbstractNode] it fails "
            )
            mes += " for the following test:\n"
            mes += "[isinstance(vid, str) and isinstance(v, AbstractNode) "
            mes += "for vid, v in self.V.items()]"
            raise TypeError(mes)

        if etypes is False:
            mes = (
                "self.E property must return Dict[str, AbstractEdge] it fails "
            )
            mes += " for the following test:\n"
            mes += "[isinstance(vid, str) and isinstance(v, AbstractEdge) "
            mes += "for vid, v in self.E.items()]"
            raise TypeError(mes)


class AbstractTree(AbstractGraph):
    """"""

    def __init__(self, *args, **kwargs):
        self.check_types()

    @property
    @abstractmethod
    def root(self) -> AbstractNode:
        raise NotImplementedError

    def check_types(self) -> bool:
        """"""
        r = self.root
        type_check_msg(r, AbstractNode, "property root")
        return True


class AbstractPath(AbstractGraph):
    """"""

    def __init__(self, *args, **kwargs):
        """"""
        self.check_types()

    @abstractmethod
    def start(self) -> AbstractNode:
        raise NotImplementedError

    @abstractmethod
    def end(self) -> AbstractNode:
        raise NotImplementedError

    @abstractmethod
    def length(self) -> int:
        """"""
        raise NotImplementedError

    @abstractmethod
    def node_list(self) -> List[AbstractNode]:
        """"""
        raise NotImplementedError

    @abstractmethod
    def endvertices(self) -> Tuple[AbstractNode, AbstractNode]:
        """"""
        raise NotImplementedError

    def check_types(self):
        "Check types of methods"
        evs = self.endvertices()
        type_check_msg(evs, tuple, "endvertices")
        if len(evs) != 2:
            mes = "endvertices() method must return a tuple with two members "
            mes += "it returns " + str(len(evs))
            raise ValueError(mes)
        member_check = isinstance(evs[0], AbstractNode) and isinstance(
            evs[1], AbstractNode
        )
        if member_check is False:
            mes = "endvertices() method must return tuple containing only "
            mes += "members which subclass AbstractNode. It contains "
            mes += str(type(evs[0])) + " and " + str(type(evs[1]))
            raise TypeError(mes)

        ns = self.node_list()
        type_check_msg(ns, list, "node_list")
        if not all(isinstance(n, AbstractNode) for n in ns):
            mes = "node_list() method must return list containing only "
            mes += "members which subclass AbstractNode"
            raise TypeError(mes)
        #
        l_path = self.length()
        type_check_msg(l_path, int, "length")


class AbstractUndiGraph(AbstractGraph):
    """"""


class AbstractDiGraph(AbstractGraph):
    """"""
