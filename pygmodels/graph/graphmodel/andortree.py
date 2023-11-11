"""!
and/or search tree implementation
"""
from copy import deepcopy
from uuid import uuid4

from gmodels.graphtypes.edge import Edge, EdgeType
from gmodels.graphtypes.path import Path
from gmodels.graphtypes.tree import Tree
from gmodels.pgmtypes.pgmodel import PGModel
from gmodels.pgmtypes.randomvariable import ANDNode, NumCatRVariable, ORNode


class OrTree(Tree):
    """!
    Or search tree from pgmodel
    """

    def __init__(self, pmodel: PGModel):
        self.model = pmodel
        (self.mst, self.edge_order) = self.model.find_minimum_spanning_tree(
            weight_fn=lambda x: x.data()["factor"]
            if "factor" in x.data()
            else 1
        )
        # expand mst to cover values
        es = set()
        for e in self.mst.edges():
            n = e.start()
            ndata = n.data()
            if "evidence" in ndata:
                es.add(e)
            else:
                values = ndata["outcome-values"]
                for v in values:
                    ncp = deepcopy(n)
                    ncp.add_evidence(v)
                    ne = Edge(
                        edge_id=str(uuid4()),
                        edge_type=e.type(),
                        start_node=ncp,
                        end_node=e.end(),
                    )
                    es.add(ne)
        #
        super().__init__(gid=str(uuid4()), edges=es)

    def highest_probability_path(self, leaf: NumCatRVariable) -> Path:
        """!
        find the highest probability yielding path between the root node and
        the leaf.
        """
        start = self.root_node()
        end = leaf

        def costfn(e: Edge, parent_cost: float):
            """"""
            return self.model.factor(e) + parent_cost

        return self.extract_path_info(
            end=end, start=start, costfn=costfn, is_min=False
        )

    def most_likely_instants(self):
        """!
        Search paths between the root node and leaves.
        We assume that the evidence is already incorporated into
        nodes. By maximizing the cost function we ensure that we end up with
        highest marginals for each random variable
        """
        leave_paths = []
        for leaf in self.leaves():
            info = self.highest_probability_path(leaf)
            leave_paths.append(info)
        leave_paths.sort(key=lambda x: x["cost"], reverse=True)
        return leave_paths


class AndOrTree(Tree):
    """!
    And/Or search tree from pgmodel
    """

    def __init__(self, pmodel: PGModel):
        """"""
        self.model = pmodel
        self.mprops = self.model.props
