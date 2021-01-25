"""!
Bayesian Network model
"""

from gmodels.gtypes.digraph import DiGraph
from gmodels.gtypes.edge import Edge
from gmodels.randomvariable import NumCatRVariable
from gmodels.factor import Factor
from gmodels.pgmodel import PGModel
from typing import Set
import math
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
        factors: Optional[Set[Factor]] = None,
        data={},
    ):
        ""
        DiGraph.__init__(gid=gid, data=data, nodes=nodes, edges=edges)
        if factors is None:
            fs: Set[Factor] = set()
            for X_i in self.nodes():
                evidences = set()
                if "evidence" in X_i.data():
                    evidences.add((X_i.id(), X_i.data()["evidence"]))
                for n in self.parents_of(X_i):
                    if "evidence" in n.data():
                        evidences.add((n.id(), n.data()["evidence"]))
                f = Factor.from_conditional_vars(X_i=X_i, Pa_Xi=self.parents_of(X_i))
                if len(evidences) != 0:
                    f.reduced_by_value(evidences)
                fs.add(f)
            Fs = fs
        else:
            Fs = factors
        PGModel.__init__(gid=gid, data=data, nodes=nodes, edges=edges, factors=Fs)
