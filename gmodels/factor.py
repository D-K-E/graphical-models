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

        self.scope_products: List[Set[Tuple[str, NumericValue]]] = []

        self.Z = self.zval()

    def scope_vars(self, f=lambda x: x):
        return f(self.svars)

    @classmethod
    def fdomain(
        cls,
        D: Set[NumCatRVariable],
        rvar_filter=lambda x: True,
        value_filter=lambda x: True,
        value_transform=lambda x: x,
    ) -> List[Set[Tuple[str, NumericValue]]]:
        """!
        Get factor domain Val(D) D being a set of random variables
        """
        return [
            s.value_set(value_filter=value_filter, value_transform=value_transform)
            for s in D
            if rvar_filter(s) is True
        ]

    @classmethod
    def matches(
        cls,
        D: Set[NumCatRVariable],
        rvar_filter=lambda x: True,
        value_filter=lambda x: True,
        value_transform=lambda x: x,
    ):
        """!
        Compute scope matches for arbitrary domain
        """
        svars = cls.fdomain(
            D=D,
            rvar_filter=rvar_filter,
            value_filter=value_filter,
            value_transform=value_transform,
        )
        return list(product(*svars))

    def domain(
        self,
        rvar_filter=lambda x: True,
        value_filter=lambda x: True,
        value_transform=lambda x: x,
    ) -> List[Set[Tuple[str, NumericValue]]]:
        """!
        Get factor domain
        """
        return self.fdomain(
            D=self.scope_vars(),
            rvar_filter=rvar_filter,
            value_filter=value_filter,
            value_transform=value_transform,
        )

    def domain_scope(
        self, domain: List[Set[Tuple[str, NumericValue]]]
    ) -> Set[NumCatRVariable]:
        """!
        Given a domain of values obtain scope variables implied
        """
        sids = {}
        for vs in domain:
            for vtpl in vs:
                sids[vtpl[0]] = vtpl[1]
        # check for values out of domain of this factor
        scope_ids = set([s.id() for s in self.scope_vars()])
        if set(sids.keys()).issubset(scope_ids) is False:
            msg = (
                "Given argument domain include values out of the domain of this factor"
            )
            raise ValueError(msg)
        svars = set()
        for s in self.scope_vars():
            if s.id() in sids:
                svars.add(s)
        return svars

    def has_var(self, ids: str) -> Tuple[bool, Optional[NumCatRVariable]]:
        """!
        check if given id belongs to variable of this scope
        """
        vs = [s for s in self.svars if s.id() == ids]
        if len(vs) == 0:
            return False, None
        elif len(vs) == 1:
            return True, vs[0]
        else:
            raise ValueError("more than one variable matches the id string")

    def phi(self, scope_product: Set[Tuple[str, NumericValue]]) -> float:
        """!
        obtain a factor value for given scope random variables
        """
        return self.factor_fn(scope_product)

    def normalize(self, phi_result: float) -> float:
        """!
        Normalize a given factorization result by dividing it to the value of
        partition function value Z
        """
        return phi_result / self.Z

    def phi_normal(self, scope_product: Set[Tuple[str, NumericValue]]) -> float:
        return self.normalize(self.phi(scope_product))

    def partition_value(self, svars):
        """!
        compute partition value aka normalizing value for the factor
        from Koller, Friedman 2009 p. 105
        """
        scope_matches = list(product(*svars))
        return sum([self.factor_fn(scope_product=sv) for sv in scope_matches])

    def zval(self):
        ""
        svars = self.domain()
        self.scope_products = list(product(*svars))
        return sum([self.factor_fn(scope_product=sv) for sv in self.scope_products])

    def marginal_joint(self, scope_product: Set[Tuple[str, NumericValue]]) -> float:
        ""
        p = 1.0
        for sv in scope_product:
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

    def product(
        self,
        other,
        product_fn=lambda x, y: x * y,
        accumulator=lambda added, accumulated: added * accumulated,
    ):
        """!
        Factor product operation
        from Koller, Friedman 2009, p. 107
        \f \psi(X,Y,Z) =  \phi(X,Y) \cdot \phi(Y,Z) \f
        \f \prod_i phi(X_i) \f

        \return Factor
        """
        if not isinstance(other, Factor):
            raise TypeError("other needs to be a factor")
        #
        svar = self.scope_vars()
        ovar = other.scope_vars()
        var_inter = svar.intersection(ovar)
        var_inter = list(var_inter)
        vsets = [v.value_set() for v in var_inter]
        inter_products = list(product(*vsets))
        smatch = self.scope_products
        omatch = other.scope_products
        prod = 1.0
        common_match = set()
        for iproduct in inter_products:
            for o in omatch:
                for s in smatch:
                    ss = set(s)
                    ost = set(o)
                    prod_s = set(iproduct)
                    if prod_s.issubset(ss) and prod_s.issubset(ost):
                        common = ss.union(ost)
                        multi = product_fn(self.factor_fn(ss), other.factor_fn(ost))
                        common_match.add((multi, tuple(common)))
                        prod = accumulator(multi, prod)

        def fx(scope_product: Set[Tuple[str, NumericValue]]):
            ""
            for multip, match in common_match:
                if set(match) == set(scope_product):
                    return multip

        f = Factor(gid=str(uuid4()), scope_vars=svar.union(ovar), factor_fn=fx)
        return f, prod

    def reduced_by_value(self, context: Set[Tuple[str, NumericValue]]):
        """!
        Koller, Friedman 2009, p. 111
        reduction by value example
        phi(A,B,C)                                     phi(A,B,C=c1)
        +======+======+======+                    +======+======+======+
        | a1   | b1   |  c1  |                    | a1   | b1   |  c1  |
        +======+======+======+                    +======+======+======+
        | a1   | b1   |  c2  |  reduction C=c1    | a2   | b1   |  c1  |
        +======+======+======+ ---------------->  +======+======+======+
        | a2   | b1   |  c1  |
        +======+======+======+
        | a2   | b1   |  c2  |
        +======+======+======+
        """
        svars = []
        for s in self.scope_products:
            ss = set(s)
            if context.issubset(ss):
                svars.append(ss)

        self.scope_products = svars
        self.Z = sum([self.factor_fn(s) for s in self.scope_products])

    def filter_assignments(
        self, assignments: Set[Tuple[str, NumericValue]], context: Set[NumCatRVariable]
    ):
        """!
        filter out assignments that do not belong to context domain
        """
        assignment_d = {a[0]: a[1] for a in assignments}
        context_ids = set([c.id() for c in context])
        for a in assignment_d.copy().keys():
            if a not in context_ids:
                assignment_d.pop(a)
        return set([(k, v) for k, v in assignment_d.items()])

    def reduce_by_vars(
        self,
        assignment_context: Set[NumCatRVariable],
        assignments: Set[Tuple[str, NumericValue]],
    ):
        """!
        Koller, Friedman 2009, p. 111 follows the definition 4.5
        For \f U \not \subset Y \f, we define phi[u] to be phi[U'=u'], where 
        \f U' = U \cap Y \f , and u' = u<U>, where u<U> denotes the assignment
        in u to the variables in U'.
        """
        svars = []
        cdomain = self.fdomain(assignment_context)
        if any(assignments.issubset(c) for c in cdomain) is False:
            raise ValueError("assignments do not belong to domain of context")
        if assignment_context.issubset(self.scope_vars()) is True:
            self.reduced_by_value(assignments)
            return
        U_x = self.scope_vars().intersection(assignment_context)
        u_x = self.filter_assignments(assignments=assignments, context=U_x)
        for s in self.matches(D=U_x):
            ss = set(s)
            if u_x.issubset(ss) is True:
                svars.append(ss)
        self.scope_products = svars
        self.Z = sum([self.factor_fn(s) for s in self.scope_products])

    def sumout_var(self, Y: NumCatRVariable):
        """!
        Sum the variable out of factor as per Koller, Friedman 2009, p. 297
        which creates a new factor
        """
        if Y not in self.scope_vars():
            raise ValueError("argument is not in scope of this factor")

        Y_vals = Y.value_set()
        products = self.scope_products
        fn = self.factor_fn

        def psi(scope_product: Set[Tuple[str, NumericValue]]):
            ""
            s = set(scope_product)
            if len(s.intersection(Y_vals)) > 0:
                scope_diff = s.difference(Y_vals)
                diffs = set([p for p in products if scope_diff.issubset(p) is True])
                return sum([fn(d) for d in diffs])
            else:
                return fn(s)

        return Factor(gid=str(uuid4()), scope_vars=self.scope_vars(), factor_fn=psi)

    def maxout_var(self, Y: NumCatRVariable):
        """!
        max the variable out of factor as per Koller, Friedman 2009, p. 555
        which creates a new factor
        """
        if Y not in self.scope_vars():
            raise ValueError("argument is not in scope of this factor")

        Y_vals = Y.value_set()
        products = self.scope_products
        fn = self.factor_fn

        def psi(scope_product: Set[Tuple[str, NumericValue]]):
            ""
            s = set(scope_product)
            if len(s.intersection(Y_vals)) > 0:
                scope_diff = s.difference(Y_vals)
                diffs = set([p for p in products if scope_diff.issubset(p) is True])
                return max([fn(d) for d in diffs])
            else:
                return fn(s)

        return Factor(gid=str(uuid4()), scope_vars=self.scope_vars(), factor_fn=psi)

    def sumout_vars(self, Ys: Set[NumCatRVariable]):
        """!
        Sum the variable out of factor as per Koller, Friedman 2009, p. 297
        which creates a new factor
        """
        if len(Ys) < 2:
            raise ValueError("number of variables must be more than 1")
        ylst = list(Ys)
        fac = self.sumout_var(ylst[0])
        for i in range(1, len(ylst)):
            fac = fac.sumout_var(ylst[i])
        return fac
