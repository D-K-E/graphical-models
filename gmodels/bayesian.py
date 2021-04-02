"""!
Bayesian Network model
"""

from gmodels.gtypes.digraph import DiGraph
from gmodels.gtypes.edge import Edge
from gmodels.randomvariable import NumCatRVariable
from gmodels.factor import Factor
from gmodels.pgmodel import PGModel
from typing import Set
from uuid import uuid4


class BayesianNetwork(PGModel, DiGraph):
    """!
    bayesian network implementation
    """

    def __init__(
        self,
        gid: str,
        nodes: Set[NumCatRVariable],
        edges: Set[Edge],
        factors: Set[Factor],
        data={},
    ):
        ""
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges, factors=factors)

    @classmethod
    def from_digraph(cls, dig: DiGraph):
        """!
        \brief Construct a BayesianNetwork from a directed graph

        We assume that edges encode an independence structure of the system.
        Hence we deduce factors from them. If there is any evidence associated
        with a random variable, we apply them to reduce factors.

        \param dig A Directed Graph whose nodes are random variables

        \return BayesianNetwork 

        \code{.py}

        >>> myDiGraph = DiGraph()

        \endcode
        """
        fs: Set[Factor] = set()
        for X_i in dig.nodes():
            evidences = set()
            if "evidence" in X_i.data():
                evidences.add((X_i.id(), X_i.data()["evidence"]))
            for n in dig.parents_of(X_i):
                if "evidence" in n.data():
                    evidences.add((n.id(), n.data()["evidence"]))
            f = Factor.from_conditional_vars(X_i=X_i, Pa_Xi=dig.parents_of(X_i))
            if len(evidences) != 0:
                f = f.reduced_by_value(evidences)
            fs.add(f)
        #
        return BayesianNetwork(
            gid=str(uuid4()), nodes=dig.nodes(), edges=dig.edges(), factors=fs
        )
