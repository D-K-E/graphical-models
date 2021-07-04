"""!
\file node.py

\ingroup graphgroup nodegroup

\see \link graphgroup Graph Object \endlink nodegroup edgegroup

For more theoretical explanation \see nodegroup

"""
from typing import Dict, Set, Tuple, Optional
from gmodels.gtype.graphobj import GraphObject
from gmodels.gtype.abstractobj import AbstractNode
from abc import ABC, abstractmethod


class Node(AbstractNode, GraphObject):
    """!
    \brief Node A simple node in a graph

    Description
    ==============
    A node in a graph object. It serves as a generic base class for all
    types of graphs. It does not know its edges.
    """

    def __init__(self, node_id: str, data={}):
        "constructor for a node"
        super().__init__(oid=node_id, odata=data)

    def __eq__(self, n):
        """!
        \brief check for equality of a given object with this one

        Description
        ============

        First we control the instance of the given argument. If the given
        argument is of the same instance, we check further, if not we return
        False. In the case of having a same instance, we check their ids. If
        they have the same id we return true, if not false.

        \param n argument object of which we test for equality
        \return True/False
        """
        if isinstance(n, Node):
            return self.id() == n.id()
        return False

    def __str__(self) -> str:
        """!
        \brief obtain string representation of Node object

        Description
        ============
        We call the id method, with data method. Transform them to string.
        Then concatanate them using '--'.

        \return string
        """
        return (
            self.id()
            + "--"
            + "::".join([str(k) + "-" + str(v) for k, v in self.data().items()])
        )

    def __hash__(self):
        """!
        \brief Obtain hash value from string representation of Node

        Description
        ============
        First we obtain the string representation of Node. Then we call hash on
        it.

        \return int
        """
        return hash(self.__str__())


"""!
\defgroup nodegroup Node documentation

\section desc_sect Description

A node in graph as in graph theory. It can hold any data. It inherits graph
object. We can transform them into strings. We can obtain their hash value from
the string representation. The equality check is performed using id and types.

"""
