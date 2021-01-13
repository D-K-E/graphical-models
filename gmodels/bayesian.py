"""!
Bayesian Network model
"""

from gmodels.gtypes.digraph import DiGraph
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.randomvariable import NumCatRVariable
from typing import Callable, Set, Any, List
import math
from uuid import uuid4


class BayesianNetwork(DiGraph):
    """!
    bayesian network implementation
    """

    def __init__(
        self, gid: str, nodes: Set[NumCatRVariable], edges: Set[Edge], data={}
    ):
        ""
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges)

    #
    def cond2(self, X: NumCatRVariable, Y: NumCatRVariable) -> float:
        """!
        get joint probability distribution: Koller, Friedman 2009, p. 31
        p(X|Y) = P(Y, X) / P(Y)
        """
        return Y.joint(X) / Y.P_X()

    def cond3(
        self, X: NumCatRVariable, Y: NumCatRVariable, Z: NumCatRVariable
    ) -> float:
        """!
        get joint probability distribution: Koller, Friedman 2009, p. 24
        p(X, Y | Z) = P(X | Z) P(Y | Z)
        """
        return self.cond2(X, Z) * self.cond2(Y, Z)

    def cond(self, X: NumCatRVariable) -> float:
        """!
        conditional distribution
        \f P(X) = \prod P(X | Pa(X)) \f
        """
        p = 1.0
