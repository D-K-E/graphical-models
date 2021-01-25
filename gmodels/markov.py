"""!
Markov network
"""
from gmodels.gtypes.undigraph import UndiGraph
from gmodels.gtypes.edge import Edge
from gmodels.randomvariable import NumCatRVariable
from gmodels.factor import Factor
from gmodels.pgmodel import PGModel
from typing import Set, Optional
from uuid import uuid4


class MarkovNetwork(PGModel, UndiGraph):
    def __init__(
        self,
        gid: str,
        nodes: Set[NumCatRVariable],
        edges: Set[Edge],
        factors: Optional[Set[Factor]] = None,
        data={},
    ):
        """!
        Markov Random Field
        """
        UndiGraph.__init__(gid=gid, nodes=nodes, edges=edges, data=data)
        maximal_cliques = self.find_maximal_cliques()
        if factors is None:
            fs: Set[Factor] = set()
            for clique in maximal_cliques:
                evidences = set()
                for n in clique:
                    edata = n.data()
                    if "evidence" in edata:
                        evidences.add((n.id(), edata["evidence"]))
                f = Factor(gid=str(uuid4()), scope_vars=clique)
                if len(evidences) != 0:
                    f.reduced_by_value(evidences)
                fs.add(f)
            Fs = fs
        else:
            Fs = factors
        PGModel.__init__(gid=gid, data=data, nodes=nodes, edges=edges, factors=Fs)
