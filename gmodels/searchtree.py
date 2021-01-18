"""!
and/or search tree implementation
"""
from gmodels.gtypes.tree import Tree
from gmodels.gtypes.edge import Edge
from gmodels.randomvariable import ANDNode, ORNode
from gmodels.pgmodel import PGModel
from uuid import uuid4


class OrTree(Tree):
    """!
    Or search tree from pgmodel
    """

    def __init__(self, pmodel: PGModel):
        self.model = pmodel
        (self.mst, self.edge_order) = self.model.find_minimum_spanning_tree(
            weight_fn=lambda x: x.data()["factor"] if "factor" in x.data() else 1
        )
        es = set()
        for e in self.mst.edges():
            n = e.start()
            ndata = n.data()
            if "evidence" in ndata:
                es.add(e)
            else:
                values = ndata["outcome-values"]
                for v in values:
                    marg = n.marginal(v)
                    ne = Edge(
                        edge_id=str(uuid4()),
                        edge_type=e.type(),
                        data={"weight": marg},
                        start_node=n,
                        end_node=e.end(),
                    )
                    es.add(ne)
        #
        super().__init__(gid=str(uuid4()), edges=es)


class AndOrTree(Tree):
    """!
    And/Or search tree from pgmodel
    """

    def __init__(self, pmodel: PGModel):
        ""
        self.model = pmodel
        self.mprops = self.model.props
