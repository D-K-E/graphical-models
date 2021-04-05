"""!
\file factor.py

Defining a factor from Koller and Friedman 2009, p. 106-107
"""

from gmodels.gtypes.graphobj import GraphObject
from gmodels.randomvariable import NumCatRVariable, NumericValue

from typing import Set, Callable, Optional, List, Union, Tuple
from itertools import product, combinations
from uuid import uuid4
from pprint import pprint


class Factor(GraphObject):
    """!
    \brief Factor from Koller and Friedman 2009, p. 106-107

    """

    def __init__(
        self,
        gid: str,
        scope_vars: Set[NumCatRVariable],
        factor_fn: Optional[Callable[[Set[Tuple[str, NumCatRVariable]]], float]] = None,
        data={},
    ):
        """!
        \brief Constructor for a factor \f[ \phi(A,B) \f]

        A factor is defined by a set of random variables which constitutes its
        scope and a real valued function. The canonical definition can be found
        in Koller and Friedman 2009, p. 106-107.  During construction, we check
        so that all random variables are positive valued. If no function is
        provided, we instantiate the factor with a marginal joint function.

        \param scope_vars variables that constitue scope of factor.
        \param factor_fn a real valued function

        \code{.py}

        >>> Af = NumCatRVariable(
        >>>         node_id="A", 
        >>>         input_data={"outcome-values": [10, 50]},
        >>>         distribution=lambda x: 0.5,
        >>>      )
        >>> Bf = NumCatRVariable(
        >>>         node_id="B",
        >>>         input_data={"outcome-values": [10, 50]},
        >>>         distribution=lambda x: 0.5,
        >>>     )
        >>> Cf = NumCatRVariable(
        >>>    node_id="C",
        >>>    input_data={"outcome-values": [10, 50]},
        >>>    distribution=lambda x: 0.5,
        >>> )
        >>> Df = NumCatRVariable(
        >>>    node_id="D",
        >>>    input_data={"outcome-values": [10, 50]},
        >>>    distribution=lambda x: 0.5,
        >>> )
           
        >>> def phiAB(scope_product):
        >>>    ""
        >>>    sfs = set(scope_product)
        >>>    if sfs == set([("A", 10), ("B", 10)]):
        >>>        return 30
        >>>    elif sfs == set([("A", 10), ("B", 50)]):
        >>>        return 5
        >>>    elif sfs == set([("A", 50), ("B", 10)]):
        >>>        return 1
        >>>    elif sfs == set([("A", 50), ("B", 50)]):
        >>>        return 10
        >>>    else:
        >>>        raise ValueError("unknown arg")
           
        >>> AB = Factor(gid="AB", 
        >>>         scope_vars=set([self.Af, self.Bf]), 
        >>>         factor_fn=phiAB
        >>>     )

        \endcode

        """
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

    def scope_vars(self, f=lambda x: x) -> Set[NumCatRVariable]:
        """!
        \brief get variables that are inside the scope of this factor

        \param f is a function that transforms the scope of this factor.

        \code

        >>> A = NumCatRVariable("A",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     distribution=lambda x: 0.5)
        >>> fac = Factor(gid=str(uuid4()), scope_vars=set([A]))
        >>> fac.scope_vars(f=lambda x: set([(x,x)]))
        >>> set([(A, A)])

        \endcode
        """
        return f(self.svars)

    @classmethod
    def from_joint_vars(cls, svars: Set[NumCatRVariable]):
        """!
        \brief Make factor from joint variables

        \param svars set of random variables in the scope of the future factor

        We assume that the factor for the given set of random variables would
        be their marginal product.

        \code

        >>> A = NumCatRVariable("A",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     distribution=lambda x: 0.5)
        >>> B = NumCatRVariable("B",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     distribution=lambda x: 0.5)


        >>> fac = Factor.from_joint_vars(svars=set([A, B]))

        \endcode
        """
        return Factor(gid=str(uuid4()), scope_vars=svars)

    @classmethod
    def from_conditional_vars(
        cls,
        X_i: NumCatRVariable,
        Pa_Xi: Set[NumCatRVariable],
        fn: Optional[Callable[[Set[Tuple[str, NumericValue]]], float]] = None,
    ):
        """!
        \brief Make factor from joint variables

        We assume that given random variables are conditionally related. We
        simply assume the following factorization between given variables:
        \f[ P(X_i | Pa_{X_i}) \f] which decomposes as 
        \f[ P(X_i | (X_1, X_2, X_3, \dots, X_j)\f] where 
        \f[{X_1, X_2, \dots, X_j} = Pa_{X_i}\f]

        Basically we take the marginal product of parents and use the bayes
        rule to output the final probability value of the expression. See
        Koller, Friedman 2009, p. 46 - 47 on conditional parametrization and p.
        62 for factorization of conditionally parametrized structures.

        \param X_i main variable
        \param Pa_Xi parent variables of the main variable
        \param fn factor function that defines the factor between parent and child

        \code

        >>> A = NumCatRVariable("A",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     distribution=lambda x: 0.5)

        >>> B = NumCatRVariable("B",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     distribution=lambda x: 0.5)

        >>> C = NumCatRVariable("C",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     distribution=lambda x: 0.5)

        >>> fac = Factor.from_conditional_vars(X_i=A, Pa_Xi=set([B,C]))

        \endcode
        """
        Pa_Xs = 1.0
        for p in Pa_Xi:
            Pa_Xs *= p.P_X_e()

        X_i_PaXi = X_i.P_X_e() * Pa_Xs

        def fx(scope_product: Set[Tuple[str, NumericValue]]) -> float:
            return X_i_PaXi / Pa_Xs

        if fn is None:
            ff = fx
        else:
            ff = fn

        Pa_Xi.add(X_i)
        return Factor(gid=str(uuid4()), scope_vars=Pa_Xi, factor_fn=ff)

    @classmethod
    def fdomain(
        cls,
        D: Set[NumCatRVariable],
        rvar_filter=lambda x: True,
        value_filter=lambda x: True,
        value_transform=lambda x: x,
    ) -> List[Set[Tuple[str, NumericValue]]]:
        """!
        \brief Get factor domain Val(D) D being a set of random variables

        \param D set of random variables
        \param rvar_filter filtering function for random variables
        \param value_filter filtering values from random variables' codomain
        \param value_transform apply a certain transformation to values from random variables' codomain.

        \return list of codomain of random variables

        \code

        >>> A = NumCatRVariable("A",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     distribution=lambda x: 0.5)

        >>> B = NumCatRVariable("B",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     distribution=lambda x: 0.5)

        >>> D = set([A,B])

        >>> fmatches = Factor.fdomain(D=D)
        >>> print(fmatches)

        >>> [set(("A", True), ("A", True)),
        >>>  set(("B", True), ("B", False)),
        >>> ]

        \endcode

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
        \brief Compute scope matches for arbitrary domain
        cartesian product over set of random variables

        \code

        >>> A = NumCatRVariable("A",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     distribution=lambda x: 0.5)

        >>> B = NumCatRVariable("B",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     distribution=lambda x: 0.5)

        >>> D = set([A,B])

        >>> fmatches = Factor.matches(D=D)
        >>> print(fmatches)

        >>> [(("A", True), ("B", True)),
        >>>  (("A", True), ("B", False)),
        >>>  (("A", False), ("B", True)), (("A", False), ("B", False))]

        \endcode
        """
        svars = cls.fdomain(
            D=D,
            rvar_filter=rvar_filter,
            value_filter=value_filter,
            value_transform=value_transform,
        )
        return list(product(*svars))

    def factor_domain(
        self,
        rvar_filter=lambda x: True,
        value_filter=lambda x: True,
        value_transform=lambda x: x,
    ):
        """!
        \brief \see Factor.matches(rvar_filter, value_filter, value_transform)
        For a factor phi(A,B) return factor function's domain values, such as:

        \f[phi(A,B)\f]

         A   |  B
        ---- | ----
         a1  |  b1
         a1  |  b2
         a2  |  b1
         a2  |  b2

        >>> set(("A", a1), ("B", b2)),...
        """
        return list(product(*self.vars_domain()))

    def vars_domain(
        self,
        rvar_filter=lambda x: True,
        value_filter=lambda x: True,
        value_transform=lambda x: x,
    ) -> List[Set[Tuple[str, NumericValue]]]:
        """!
        \brief Get factor domain
        \see Factor.fdomain(D, rvar_filter, value_filter, value_transform)
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
        \brief Given a domain of values obtain scope variables implied
        Obtain random variables from given factor domain.
        Each value in domain comes with an identifier of its random variable.
        From these identifiers, we obtain set of random variables attested in
        factor domain.
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
        \brief check if given id belongs to variable of this scope
        Check if given random variable id is contained in scope of factor.

        \param ids identifier of random variable
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
        \brief obtain a factor value for given scope random variables

        Obtain factor value for given argument

        \code
        >>> A = NumCatRVariable("A",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     distribution=lambda x: 0.5)

        >>> B = NumCatRVariable("B",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     distribution=lambda x: 0.5)

        >>> fac = Factor.from_joint_vars(svars=set([A, B]))
        >>> fac.phi(scope_product=set([("A", True), ("B", True)]))
        >>> 0.25

        \endcode
        """
        return self.factor_fn(scope_product)

    def __call__(self, scope_product: Set[Tuple[str, NumericValue]]) -> float:
        """!
        \brief Make a factor callable to reproduce more function like behavior

        \see Factor.phi(scope_product)
        """
        return self.phi(scope_product)

    def normalize(self, phi_result: float) -> float:
        """!
        \brief Normalize a given factorization result by dividing it to the
        value of partition function value Z
        """
        return phi_result / self.Z

    def phi_normal(self, scope_product: Set[Tuple[str, NumericValue]]) -> float:
        """!
        \brief normalize a given factor value
        """
        return self.normalize(self.phi(scope_product))

    def max_value(self):
        """!
        \brief maximum factor value for this factor
        """
        mx = float("-inf")
        max_val = None
        for sp in self.factor_domain():
            ss = set(sp)
            phi_s = self.phi(ss)
            if phi_s > mx:
                mx = phi_s
                max_val = ss
        return max_val

    def partition_value(self, svars):
        """!
        \brief compute partition value aka normalizing value for the factor
        from Koller, Friedman 2009 p. 105
        """
        scope_matches = list(product(*svars))
        return sum([self.factor_fn(scope_product=sv) for sv in scope_matches])

    def zval(self):
        """!
        \brief compute value of partition function for this factor
        """
        svars = self.vars_domain()
        self.scope_products = list(product(*svars))
        return sum([self.factor_fn(scope_product=sv) for sv in self.factor_domain()])

    def marginal_joint(self, scope_product: Set[Tuple[str, NumericValue]]) -> float:
        """!
        \brief marginal joint function.
        Default factor function when none is provided.
        """
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
        """!
        Check if given parameter is in scope of this factor
        """
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
        \brief Factor product operation from Koller, Friedman 2009, p. 107
        \f[ \psi(X,Y,Z) =  \phi(X,Y) \cdot \phi(Y,Z) \f]
        \f[ \prod_i phi(X_i) \f]

        Point wise product of two different factor functions.
        \param product_fn actual function for computing product. This function
        can be exchanged with another function to compute log-sum for example.

        \param accumulator this function decides how to accumulate resulting product.

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
        smatch = self.factor_domain()
        omatch = other.factor_domain()
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

    def reduced(self, context: Set[Tuple[str, NumericValue]]):
        """!
        \brief reduce factor using given context

        \param context member of factor domain

        Koller, Friedman 2009, p. 111 reduction by value example

        \f[phi(A,B,C)\f]

         A      B      C
        ---- | ---- | ----
         a1  |  b1  |  c1
         a1  |  b1  |  c2
         a2  |  b1  |  c1
         a2  |  b1  |  c2

        reduction C=c1 \f[\phi(A,B,C=c_1)\f]

           A      B      C
          ---- | ---- | ----
           a1  |  b1  |  c1
           a2  |  b1  |  c1

        """
        svars = set()
        for sv in self.scope_vars():
            for kval in context:
                k, value = kval
                if sv.id() == k:
                    sv.reduce_to_value(value)
            svars.add(sv)
        return Factor(gid=str(uuid4()), scope_vars=svars, factor_fn=self.phi)

    def reduced_by_value(self, context: Set[Tuple[str, NumericValue]]):
        """!
        \brief \see Factor.reduced(context)

        \return Factor
        """
        return self.reduced(context)

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

    def reduced_by_vars(
        self,
        assignment_context: Set[NumCatRVariable],
        assignments: Set[Tuple[str, NumericValue]],
    ):
        """!
        Koller, Friedman 2009, p. 111 follows the definition 4.5

        For \f[ U \not \subset Y \f], we define \f[phi[u]\f] to be
        \f[phi[U'=u']\f], where \f[ U' = U \cap Y \f] , and \f[u' = u<U>\f],
        where \f[u<U>\f] denotes the assignment in \f[u\f] to the variables in
        \f[U'\f].

        \return Factor
        """
        return self.reduced(context=assignments)

    def maxout_var(self, Y: NumCatRVariable):
        """!
        max the variable out of factor as per Koller, Friedman 2009, p. 555

        \return Factor
        """
        if Y not in self.scope_vars():
            raise ValueError("argument is not in scope of this factor")

        Y_vals = Y.value_set()
        products = self.factor_domain()
        fn = self.factor_fn

        def psi(scope_product: Set[Tuple[str, NumericValue]]):
            ""
            s = set(scope_product)
            diffs = set([p for p in products if s.issubset(p) is True])
            return max([fn(d) for d in diffs])

        return Factor(
            gid=str(uuid4()),
            scope_vars=self.scope_vars().difference({Y}),
            factor_fn=psi,
        )

    def sumout_var(self, Y: NumCatRVariable):
        """!
        \brief Sum the variable out of factor as per Koller, Friedman 2009, p. 297

        \return Factor
        """
        if Y not in self.scope_vars():
            msg = "Argument " + str(Y)
            msg += " is not in scope of this factor: "
            msg += " ".join(self.scope_vars())
            raise ValueError(msg)

        Y_vals = Y.value_set()
        products = self.factor_domain()
        fn = self.factor_fn

        def psi(scope_product: Set[Tuple[str, NumericValue]]):
            ""
            s = set(scope_product)
            diffs = set([p for p in products if s.issubset(p) is True])
            return sum([fn(d) for d in diffs])

        return Factor(
            gid=str(uuid4()),
            scope_vars=self.scope_vars().difference({Y}),
            factor_fn=psi,
        )

    def sumout_vars(self, Ys: Set[NumCatRVariable]):
        """!
        \brief Sum the variable out of factor as per Koller, Friedman 2009, p. 297

        \return Factor
        """
        if len(Ys) == 0:
            raise ValueError("variables not be an empty set")
        if len(Ys) == 1:
            v = Ys.pop()
            return self.sumout_var(v)
        ylst = list(Ys)
        fac = self.sumout_var(ylst[0])
        for i in range(1, len(ylst)):
            fac = fac.sumout_var(ylst[i])
        return fac
