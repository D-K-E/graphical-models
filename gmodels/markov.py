"""!
Markov network
"""
from gmodels.gtypes.undigraph import UndiGraph
from gmodels.gtypes.edge import Edge
from gmodels.randomvariable import NumCatRVariable
from gmodels.factor import Factor
from gmodels.pgmodel import PGModel
from typing import Set, Optional, Tuple
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
                f = f.reduced_by_value(evidences)
            fs.add(f)
        return MarkovNetwork(
            gid=str(uuid4()), nodes=udi.nodes(), edges=udi.edges(), factors=fs
        )


class ConditionalRandomField(MarkovNetwork):
    """!
    Conditional random field as defined by Koller, Friedman 2009, p. 142-3
    """

    def __init__(
        self,
        gid: str,
        observed_vars: Set[NumCatRVariable],
        target_vars: Set[NumCatRVariable],
        edges: Set[Edge],
        factors: Set[Factor],
        data={},
    ):
        """!
        CRF constructor
        """
        if len(observed_vars.intersection(target_vars)) > 0:
            raise ValueError("Observed and target variables intersect")
        for f in factors:
            if f.scope_vars().issubset(target_vars) is True:
                raise ValueError("Scope of some factors are subset of target variables")
        super().__init__(
            gid=gid,
            nodes=observed_vars.union(target_vars),
            edges=edges,
            data=data,
            factors=factors,
        )
        self.ovars = observed_vars
        self.tvars = target_vars

    @property
    def Y(self):
        return self.tvars

    @property
    def X(self):
        return self.ovars

    @property
    def target_vars(self):
        return self.tvars

    @property
    def observed_vars(self):
        return self.ovars

    @classmethod
    def from_markov_network(cls, mn: MarkovNetwork, targets: Set[NumCatRVariable]):
        ""
        mnodes = mn.nodes()
        if targets.issubset(mnodes) is False:
            raise ValueError("target variables are not a subset of network")
        factors = mn.factors()
        crf_factors = set(
            [f for f in factors if f.scope_vars().issubset(targets) is False]
        )
        return ConditionalRandomField(
            gid=str(uuid4()),
            observed_vars=mnodes.difference(targets),
            target_vars=targets,
            edges=mn.edges(),
            factors=crf_factors,
        )

    def joint_target_observed(self) -> Tuple[Factor, float]:
        """!
        Implements the procedure in definition 4.18
        from Koller, Friedman 2009, p. 143
        """
        return self.get_factor_product(self.factors())

    def Z(self) -> Factor:
        """!
        """
        prod, v = self.joint_target_observed()
        zfac = prod.sumout_vars(self.tvars)
        return zfac

    def conditinal_probability(self):
        """!
        Implements the procedure in definition 4.18
        from Koller, Friedman 2009, p. 143
        """
        Zfac = self.Z()
        P_yx = self.joint_target_observed()

        def phi_cond(scope_product):
            ""
            ss = set(scope_product)
            z_i = Zfac.phi(ss)
            p_yx_i = P_yx.phi(ss)
            return p_yx_i / z_i

        return Factor(gid=str(uuid4()), factor_fn=phi_cond, scope_vars=self.X)
