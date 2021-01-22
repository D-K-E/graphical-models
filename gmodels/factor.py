"""!
Defining a factor from Koller and Friedman 2009, p. 106-107
"""

from gmodels.gtypes.graphobj import GraphObject
from gmodels.randomvariable import NumCatRVariable, NumericValue

from typing import Set, Callable, Optional, List, Union, Tuple
from itertools import product, combinations
from uuid import uuid4
from pprint import pprint


class Factor(GraphObject):
    ""

    def __init__(
        self,
        gid: str,
        scope_vars: Set[NumCatRVariable],
        factor_fn: Optional[Callable[[Set[Tuple[str, NumCatRVariable]]], float]] = None,
        data={},
    ):
        ""
        # check all values are positive
        super().__init__(oid=gid, odata=data)
        for svar in scope_vars:
            vs = svar.values()
            if any([v < 0 for v in vs]):
                msg = "Scope variables contain a negative value."
                msg += " Negative factors are not allowed"
                raise ValueError(msg)

        self.svars = scope_vars
        if factor_fn is None:
            self.factor_fn = self.marginal_joint
        else:
            self.factor_fn = factor_fn

        self.scope_matches: Set[Tuple[str, NumCatRVariable]] = set()

        self.Zval = self.zval()

    def scope_vars(self, f=lambda x: x):
        return f(self.svars)

    def domain(
        self,
        rvar_filter=lambda x: True,
        value_filter=lambda x, y: True,
        value_transform=lambda x: x,
    ) -> List[Set[Tuple[str, NumericValue]]]:
        """!
        Get factor domain
        """
        return [
            set(
                [
                    value_transform((s.id(), v))
                    for v in s.values()
                    if value_filter(s.id(), v) is True
                ]
            )
            for s in self.svars
            if rvar_filter(s) is True
        ]

    def has_var(self, ids: str) -> Tuple[bool, Optional[NumCatRVariable]]:
        ""
        vs = [s for s in self.svars if s.id() == ids]
        if len(vs) == 0:
            return False, None
        elif len(vs) == 1:
            return True, vs[0]
        else:
            raise ValueError("more than one variable matches the id string")

    def phi(self, svars: Set[Tuple[str, NumericValue]]) -> float:
        """!
        obtain a factor value for given scope random variables
        """
        return self.factor_fn(svars=svars)

    def normalize(self, phi_result: float) -> float:
        """!
        Normalize a given factorization result by dividing it to the value of
        partition function value Z
        """
        return phi_result / self.Zval

    def phi_normal(self, svars: Set[Tuple[str, NumericValue]]) -> float:
        return self.normalize(self.phi(svars))

    def partition_value(self, svars):
        """!
        compute partition value aka normalizing value for the factor
        from Koller, Friedman 2009 p. 105
        """
        scope_matches = list(product(*svars))
        return sum([self.factor_fn(svars=sv) for sv in scope_matches])

    def zval(self):
        ""
        svars = self.domain()
        self.scope_matches = list(product(*svars))
        return sum([self.factor_fn(svars=sv) for sv in self.scope_matches])

    def marginal_joint(self, svars: Set[Tuple[str, NumericValue]]) -> float:
        ""
        p = 1.0
        for sv in svars:
            var_id = sv[0]
            var_value = sv[1]
            hasv, var = self.has_var(var_id)
            if hasv is False:
                raise ValueError("Unknown variable id among arguments: " + var_id)
            p *= var.marginal(var_value)
        return p

    def in_scope(self, v: Union[NumCatRVariable, str]):
        if isinstance(v, NumCatRVariable):
            return v in self.svars
        elif isinstance(v, str):
            isin, val = self.has_var(v)
            return isin
        else:
            raise TypeError("argument must be NumCatRVariable or its id")

    def product(self, other) -> float:
        """!
        Factor product operation
        from Koller, Friedman 2009, p. 107
        \f \psi(X,Y,Z) =  \phi(X,Y) \cdot \phi(Y,Z) \f
        \f \prod_i phi(X_i) \f
        """
        if not isinstance(other, Factor):
            raise TypeError("other needs to be a factor")
        #
        svar = self.scope_vars()
        ovar = other.scope_vars()
        var_inter = svar.intersection(ovar)
        if len(var_inter) > 1:
            raise ValueError("factor intersecting more than 1 variable")
        #
        var_inter = list(var_inter)[0]
        smatch = self.scope_matches
        omatch = other.scope_matches
        var_column = set([(var_inter.id(), v) for v in var_inter.values()])
        prod = 1.0
        for colv in var_column:
            for o in omatch:
                for s in smatch:
                    if colv in s and colv in o:
                        multi = self.factor_fn(s) * other.factor_fn(o)
                        prod *= multi
        return prod

    def reduce_by_value(self, context: Set[Tuple[str, NumericValue]]):
        """!
        Koller, Friedman 2009, p. 111
        """
        svars = [
            set([(s.id(), v) for v in s.values() if (s.id(), v) in context])
            for s in self.svars
        ]
        self.scope_matches = list(product(*svars))
        self.Z = self.partition_value(svars)

    def reduce_by_vars(self, context: Set[NumCatRVariable]):
        """!
        Koller, Friedman 2009, p. 111
        """
        svars = [
            set([(s.id(), v) for v in s.values()])
            for s in self.svars.intersection(context)
        ]
        self.scope_matches = list(product(*svars))
        self.Z = self.partition_value(svars)

    def sumout_var(self, Y: NumCatRVariable):
        """!
        Sum the variable out of factor as per Koller, Friedman 2009, p. 297
        """
        if Y not in self.scope_vars():
            raise ValueError("argument is not in scope of this factor")

        Y_vals = set([(Y.id(), v) for v in Y.values()])
