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
        factors: Set[Factor],
        data={},
    ):
        """!
        Markov Random Field
        """
        super().__init__(gid=gid, nodes=nodes, edges=edges, data=data, factors=factors)

    @classmethod
    def from_undigraph(cls, udi: UndiGraph):
        ""
        fs: Set[Factor] = set()
        maximal_cliques = udi.find_maximal_cliques()
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
        return MarkovNetwork(
            gid=str(uuid4()), nodes=udi.nodes(), edges=udi.edges(), factors=fs
        )
