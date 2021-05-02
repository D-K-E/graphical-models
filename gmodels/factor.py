"""!
\file factor.py

Defining a factor from Koller and Friedman 2009, p. 106-107
"""

from gmodels.gtypes.graphobj import GraphObject
from gmodels.randomvariable import NumCatRVariable, NumericValue

from typing import Set, Callable, Optional, List, Union, Tuple, FrozenSet
from itertools import product, combinations
from functools import reduce as freduce
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
        \brief Constructor for a factor \f$ \phi(A,B) \f$

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
        >>>         marginal_distribution=lambda x: 0.5,
        >>>      )
        >>> Bf = NumCatRVariable(
        >>>         node_id="B",
        >>>         input_data={"outcome-values": [10, 50]},
        >>>         marginal_distribution=lambda x: 0.5,
        >>>     )
        >>> Cf = NumCatRVariable(
        >>>    node_id="C",
        >>>    input_data={"outcome-values": [10, 50]},
        >>>    marginal_distribution=lambda x: 0.5,
        >>> )
        >>> Df = NumCatRVariable(
        >>>    node_id="D",
        >>>    input_data={"outcome-values": [10, 50]},
        >>>    marginal_distribution=lambda x: 0.5,
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

        ## random variables belonging to this factor
        self.svars = scope_vars

        ## scope variable hash table
        self.domain_table = {s.id(): s for s in self.scope_vars()}

        if factor_fn is None:
            self.factor_fn = self.marginal_joint
        else:
            self.factor_fn = factor_fn

        ## cartesian product of factor domain
        self.scope_products: List[Set[Tuple[str, NumericValue]]] = list(
            product(*self.vars_domain())
        )

        ## constant normalization value
        self.Z = self.partition_value(self.vars_domain())

    def scope_vars(self, f=lambda x: x) -> Set[NumCatRVariable]:
        """!
        \brief get variables that are inside the scope of this factor

        \param f is a function that transforms the scope of this factor.

        \code{.py}

        >>> A = NumCatRVariable("A",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     marginal_distribution=lambda x: 0.5)
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
        >>>                     marginal_distribution=lambda x: 0.5)
        >>> B = NumCatRVariable("B",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     marginal_distribution=lambda x: 0.5)


        >>> fac = Factor.from_joint_vars(svars=set([A, B]))

        \endcode
        """
        return Factor(gid=str(uuid4()), scope_vars=svars)

    @classmethod
    def from_scope_variables_with_fn(
        cls,
        svars: Set[NumCatRVariable],
        fn: Callable[[Set[Tuple[str, NumericValue]]], float],
    ):
        """!
        \brief Make a factor from scope variables and a preference function
        """
        return Factor(gid=str(uuid4()), scope_vars=svars, factor_fn=fn)

    @classmethod
    def fdomain(
        cls,
        D: Set[NumCatRVariable],
        rvar_filter=lambda x: True,
        value_filter=lambda x: True,
        value_transform=lambda x: x,
    ) -> List[FrozenSet[Tuple[str, NumericValue]]]:
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
        >>>                     marginal_distribution=lambda x: 0.5)

        >>> B = NumCatRVariable("B",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     marginal_distribution=lambda x: 0.5)

        >>> D = set([A,B])

        >>> fmatches = Factor.fdomain(D=D)
        >>> print(fmatches)

        >>> [frozenset(("A", True), ("A", True)),
        >>>  frozenset(("B", True), ("B", False)),
        >>> ]

        \endcode

        """
        return [
            s.value_set(value_filter=value_filter, value_transform=value_transform)
            for s in D
            if rvar_filter(s)
        ]

    @classmethod
    def matches(
        cls,
        D: Set[NumCatRVariable],
        rvar_filter=lambda x: True,
        value_filter=lambda x: True,
        value_transform=lambda x: x,
    ) -> List[FrozenSet[Tuple[str, NumericValue]]]:
        """!
        \brief Compute cartesian product over factor domain

        The arguments are there for filtering or manipulating factor domain:
        \see Factor.fdomain

        \code{.py}

        >>> A = NumCatRVariable("A",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     marginal_distribution=lambda x: 0.5)

        >>> B = NumCatRVariable("B",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     marginal_distribution=lambda x: 0.5)

        >>> D = set([A,B])

        >>> fmatches = Factor.matches(D=D)
        >>> print(fmatches)

        >>> [frozenset([("A", True), ("B", True)]),
        >>>  frozenset([("A", True), ("B", False)]),
        >>>  frozenset([("A", False), ("B", True)]), 
        >>>  frozenset([("A", False), ("B", False)])]

        \endcode
        """
        domain_values = cls.fdomain(
            D=D,
            rvar_filter=rvar_filter,
            value_filter=value_filter,
            value_transform=value_transform,
        )
        return [frozenset(s) for s in list(product(*domain_values))]

    def factor_domain(
        self,
        rvar_filter=lambda x: True,
        value_filter=lambda x: True,
        value_transform=lambda x: x,
    ) -> List[FrozenSet[Tuple[str, NumericValue]]]:
        """!
        \brief \see Factor.matches(rvar_filter, value_filter, value_transform)

        For a factor phi(A,B) return factor function's domain values, such as:

        \f$phi(A,B)\f$

         A   |  B
        ---- | ----
         a1  |  b1
         a1  |  b2
         a2  |  b1
         a2  |  b2

        >>> [frozenset(("A", a1), ("B", b2)), ...]
        """
        return self.matches(
            D=self.scope_vars(),
            rvar_filter=rvar_filter,
            value_filter=value_filter,
            value_transform=value_transform,
        )

    def vars_domain(
        self,
        rvar_filter=lambda x: True,
        value_filter=lambda x: True,
        value_transform=lambda x: x,
    ) -> List[FrozenSet[Tuple[str, NumericValue]]]:
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

        \param domain list of arbitrary domain values

        \throw ValueError 
        \parblock

        We raise value error when the argument domain
        value array is not a subset of the domain of the factor, since we have
        no way of obtaining random variable that is not inside the scope of
        this factor.

        \endparblock

        \return set of random variables implied by the given list of domain
        values

        \code{.py}

        >>> Af = NumCatRVariable(
        >>>    node_id="A",
        >>>    input_data={"outcome-values": [10, 50]},
        >>>    marginal_distribution=lambda x: 0.5,
        >>> )
        >>> Bf = NumCatRVariable(
        >>>    node_id="B",
        >>>    input_data={"outcome-values": [10, 50]},
        >>>    marginal_distribution=lambda x: 0.5,
        >>> )
        >>>
        >>> def phiAB(scope_product):
        >>>     ""
        >>>     sfs = set(scope_product)
        >>>     if sfs == set([("A", 10), ("B", 10)]):
        >>>         return 30
        >>>     elif sfs == set([("A", 10), ("B", 50)]):
        >>>       return 5
        >>>   elif sfs == set([("A", 50), ("B", 10)]):
        >>>       return 1
        >>>   elif sfs == set([("A", 50), ("B", 50)]):
        >>>       return 10
        >>>   else:
        >>>      raise ValueError("unknown arg")

        >>> AB = Factor(gid="AB", scope_vars=set([Af, Bf]), factor_fn=phiAB)
        >>> d = AB.domain_scope(domain=[set([("A", 50), ("B", 50)]),
        >>>                             set([("A",10), ("B", 10)])
        >>>                            ])
        >>> set(d) == set([Af, Bf])
        >>> True

        \endcode
        """
        sids = set()
        for vs in domain:
            for vtpl in vs:
                sids.add(vtpl[0])
        # check for values out of domain of this factor
        scope_ids = set([s.id() for s in self.scope_vars()])
        if sids.issubset(scope_ids) is False:
            msg = (
                "Given argument domain include values out of the domain of this factor"
            )
            raise ValueError(msg)
        svars = set([s for s in self.scope_vars() if s.id() in sids])
        return svars

    def has_var(self, ids: str) -> Tuple[bool, Optional[NumCatRVariable]]:
        """!
        \brief check if given id belongs to variable of this scope
        Check if given random variable id is contained in scope of factor.

        \param ids identifier of random variable

        \throw ValueError Value error is raised if there are more than one
        random variable associated to id string

        \return Tuple 
        \parblock

        a tuple whose first element is a boolean flag indicating if
        there is indeed a variable associated to identifier and whose second
        element is either None if the operation has failed or the random
        variable associated to given identifier.

        \endparblock

        """
        if ids in self.domain_table:
            return True, self.domain_table[ids]
        elif ids not in self.domain_table:
            return False, None
        else:
            vs = [s for s in self.svars if s.id() == ids]
            if len(vs) > 1:
                raise ValueError("more than one variable matches the id string")

    def phi(self, scope_product: Set[Tuple[str, NumericValue]]) -> float:
        """!
        \brief obtain a factor value for given scope random variables

        Obtain factor value for given argument

        \param scope_product a row in conditional probability table of factor

        \code
        >>> A = NumCatRVariable("A",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     marginal_distribution=lambda x: 0.5)

        >>> B = NumCatRVariable("B",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     marginal_distribution=lambda x: 0.5)

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
        
        \param phi_result the preference value to be normalized with partition
        constant

        \return normalized preference value
        """
        return phi_result / self.Z

    def phi_normal(self, scope_product: Set[Tuple[str, NumericValue]]) -> float:
        """!
        \brief normalize a given factor value

        \param scope_product a row in conditional probability table of factor

        \return normalized value preference value

        \see Factor.normalize(phi_result), Factor.phi(scope_product)

        """
        return self.normalize(self.phi(scope_product))

    def _max_prob_value(self):
        """!
        \brief obtain highest yielding domain value and its associated codomain
        member

        Obtain the highest preference value yielding domain member of this
        factor with its associated value.
        """
        mx = float("-inf")
        max_val = None
        for sp in self.factor_domain():
            ss = set(sp)
            phi_s = self.phi(ss)
            if phi_s > mx:
                mx = phi_s
                max_val = ss
        return max_val, mx

    def max_probability(self) -> float:
        """!
        \brief maximum preference value for this factor

        \code{.py}

        >>> #
        >>> Bf = NumCatRVariable(
        >>>     node_id="B",
        >>>     input_data={"outcome-values": [10, 50]},
        >>>     marginal_distribution=lambda x: 0.5,
        >>> )
        >>> Cf = NumCatRVariable(
        >>>     node_id="C",
        >>>     input_data={"outcome-values": [10, 50]},
        >>>     marginal_distribution=lambda x: 0.5,
        >>> )
        >>> def phibc(scope_product):
        >>>     ""
        >>>     sfs = set(scope_product)
        >>>     if sfs == set([("B", 10), ("C", 10)]):
        >>>         return 0.5
        >>>     elif sfs == set([("B", 10), ("C", 50)]):
        >>>         return 0.7
        >>>     elif sfs == set([("B", 50), ("C", 10)]):
        >>>         return 0.1
        >>>     elif sfs == set([("B", 50), ("C", 50)]):
        >>>         return 0.2
        >>>     else:
        >>>         raise ValueError("unknown arg")

        >>> bc = Factor(gid="bc", scope_vars=set([Bf, Cf]), factor_fn=phibc)
        >>> mval = self.bc.max_probability()
        >>> print(mval)
        >>> 0.7

        \endcode
        """
        mval, mprob = self._max_prob_value()
        return mprob

    def max_value(self) -> Set[Tuple[str, NumericValue]]:
        """!
        \brief maximum factor value for this factor

        Obtain the highest probability yielding value from the domain of the
        factor. Notice that it does not give a probability value. It outputs
        the value which when evaluated yields the highest probability value.

        \code{.py}

        >>> #
        >>> Bf = NumCatRVariable(
        >>>     node_id="B",
        >>>     input_data={"outcome-values": [10, 50]},
        >>>     marginal_distribution=lambda x: 0.5,
        >>> )
        >>> Cf = NumCatRVariable(
        >>>     node_id="C",
        >>>     input_data={"outcome-values": [10, 50]},
        >>>     marginal_distribution=lambda x: 0.5,
        >>> )
        >>> def phibc(scope_product):
        >>>     ""
        >>>     sfs = set(scope_product)
        >>>     if sfs == set([("B", 10), ("C", 10)]):
        >>>         return 0.5
        >>>     elif sfs == set([("B", 10), ("C", 50)]):
        >>>         return 0.7
        >>>     elif sfs == set([("B", 50), ("C", 10)]):
        >>>         return 0.1
        >>>     elif sfs == set([("B", 50), ("C", 50)]):
        >>>         return 0.2
        >>>     else:
        >>>         raise ValueError("unknown arg")

        >>> bc = Factor(gid="bc", scope_vars=set([Bf, Cf]), factor_fn=phibc)
        >>> mval = self.bc.max_value()
        >>> print(mval)
        >>> {[("B", 10), ("C", 50)]}

        \endcode
        """
        mval, mrob = self._max_prob_value()
        return mval

    def partition_value(self, domains: List[FrozenSet[Tuple[str, NumericValue]]]):
        """!
        \brief compute partition value aka normalizing value for the factor
        from Koller, Friedman 2009 p. 105
        For example given the following factors:

        \f[ P(a,b,c,d) = \frac{1}{Z} \phi_1(a,b) \cdot \phi_2(b,c) \cdot
        \phi_3(c, d) \cdot \phi_4(d, a) \f]

        The Z constant is the normalizing value also known as *partition
        function*. It is defined as the following:
        \f[Z = \sum_{a,b,c,d} \phi_1(a,b) \cdot \phi_2(b,c) \cdot
        \phi_3(c, d) \cdot \phi_4(d, a) \f]

        We basically sum every possible output for the joint distribution of
        given random variables.

        \param domains list of domain set of the involved random variables.

        \code{.py}

        >>> input_data = {
        >>>    "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
        >>>    "grade": {"outcome-values": [0.2, 0.4, 0.6], "evidence": 0.2},
        >>>    "dice": {"outcome-values": [i for i in range(1, 7)], "evidence": 1.0 / 6},
        >>>    "fdice": {"outcome-values": [i for i in range(1, 7)]},
        >>> }
        >>> 
        >>> intelligence = NumCatRVariable(
        >>>     node_id="int",
        >>>     input_data=input_data["intelligence"],
        >>>     marginal_distribution=intelligence_dist,
        >>> )
        >>> 
        >>> grade = NumCatRVariable(
        >>>     node_id=nid2, input_data=input_data["grade"],
        >>>     marginal_distribution=grade_dist
        >>> )
        >>> 
        >>> dice = NumCatRVariable(
        >>>    node_id=nid3, input_data=input_data["dice"],
        >>>    marginal_distribution=fair_dice_dist
        >>> )
        >>> 
        >>> f = Factor(
        >>>    gid="f", scope_vars=set([grade, dice, intelligence])
        >>> )
        >>> 
        >>> pval = f.partition_value(f.vars_domain())
        >>> print(pval)
        >>> 1.0

        \endcode

        """
        scope_matches = list(product(*domains))
        return sum([self.factor_fn(scope_product=sv) for sv in scope_matches])

    def zval(self) -> float:
        """!
        \brief compute value of partition function for this factor

        \see Factor.partition_value(domains)
        """
        domains = self.vars_domain()
        self.scope_products = list(product(*domains))
        return sum([self.factor_fn(scope_product=sv) for sv in self.factor_domain()])

    def marginal_joint(self, scope_product: Set[Tuple[str, NumericValue]]) -> float:
        """!
        \brief marginal joint function.
        Default factor function when none is provided.

        \param scope_product a row in conditional probability table of factor

        \throw ValueError A value error is raised when there is an unknown
        random variable with an identifier 

        \return preference value for a given scope_product
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

    def in_scope(self, v: Union[NumCatRVariable, str]) -> bool:
        """!
        \brief Check if given parameter is in scope of this factor

        \param v either an identifier of a random variable or the random
        variable itself.

        \throw TypeError type error is raised if the given argument is
        neither a random variable nor a string identifier.

        \return a boolean flag which indicates if the argument is in scope or
        not.
        """
        if isinstance(v, NumCatRVariable):
            return v.id() in self.domain_table
        elif isinstance(v, str):
            return v in self.domain_table
        else:
            raise TypeError("argument must be NumCatRVariable or its id")

    def product(
        self,
        other,
        product_fn=lambda x, y: x * y,
        accumulator=lambda added, accumulated: added * accumulated,
    ) -> Tuple[GraphObject, float]:
        """!
        \brief Factor product operation from Koller, Friedman 2009, p. 107
        \f$ \psi(X,Y,Z) =  \phi(X,Y) \cdot \phi(Y,Z) \f$
        \f$ \prod_i phi(X_i) \f$

        Point wise product of two different factor functions.

        \param product_fn actual function for computing product. This function
        can be exchanged with another function to compute log-sum for example.

        \param accumulator this function decides how to accumulate resulting product.
        \param product_fn
        \parblock

        product function. Default case is that it multiplies
        its two arguments. In case of a floating precision problem it can be
        changed into summation.

        \endparblock

        \return tuple whose first element is the resulting factor and second
        element is the accumulated product.
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

    def reduced(self, assignments: Set[Tuple[str, NumericValue]]):
        """!
        \brief reduce factor using given context

        \param assignments values that are assigned to random variables of this
        factor.

        \return Factor whose conditional probability table rows are shrink to
        rows that contain assignment values.

        Koller, Friedman 2009, p. 111 reduction by value example

        \f$phi(A,B,C)\f$

         A      B      C
        ---- | ---- | ----
         a1  |  b1  |  c1
         a1  |  b1  |  c2
         a2  |  b1  |  c1
         a2  |  b1  |  c2

        reduction C=c1 \f$\phi(A,B,C=c_1)\f$

           A      B      C
          ---- | ---- | ----
           a1  |  b1  |  c1
           a2  |  b1  |  c1

        """
        svars = set()
        for sv in self.scope_vars():
            for kval in assignments:
                k, value = kval
                if sv.id() == k:
                    sv.reduce_to_value(value)
            svars.add(sv)
        return Factor(gid=str(uuid4()), scope_vars=svars, factor_fn=self.phi)

    def reduced_by_value(self, assignments: Set[Tuple[str, NumericValue]]):
        """!
        \brief \see Factor.reduced(context)

        \return Factor
        """
        return self.reduced(assignments)

    def filter_assignments(
        self, assignments: Set[Tuple[str, NumericValue]], context: Set[NumCatRVariable]
    ) -> Set[Tuple[str, NumericValue]]:
        """!
        \brief filter out assignments that do not belong to context domain
        
        Scans the given set of assignements/evidences and removes those that do
        not belong to the context.

        \param context set of random variables that are relevant to current
        computation

        \param assignments evidences with respect to the value of a certain
        random variable in scope of the context.

        \return set of valid assignments
        """
        assignment_d = {a[0]: a[1] for a in assignments}
        context_ids = set([c.id() for c in context])
        for a in assignment_d.copy().keys():
            if a not in context_ids:
                assignment_d.pop(a)
        return set([(k, v) for k, v in assignment_d.items()])

    def reduced_by_vars(
        self, assignments: Set[Tuple[str, NumericValue]],
    ):
        """!
        Koller, Friedman 2009, p. 111 follows the definition 4.5

        For \f$ U \not \subset Y \f$, we define \f$phi[u]\f$ to be
        \f$phi[U'=u']\f$, where \f$ U' = U \cap Y \f$ , and \f$u' = u<U>\f$,
        where \f$u<U>\f$ denotes the assignment in \f$u\f$ to the variables in
        \f$U'\f$.

        \return Factor
        """
        return self.reduced(assignments=assignments)

    def maxout_var(self, Y: NumCatRVariable):
        """!
        \brief max the variable out of factor as per Koller, Friedman 2009, p. 555

        Maxing out a variable, or factor maximization is defined by Koller,
        Friedman as:
        <blockquote>
        Let X be a set of variables, and Y \f$ \not \in \f$ X, a random
        variable. Let \f$ \phi(X, Y) \f$ be a factor. We define the factor
        maximization of Y in \f$ \phi \f$ to be factor \f$ \psi \f$ over X such
        that: \f$ \psi(X) = max_{Y}\phi(X, Y) \f$
        </blockquote>

        \param Y random variable who is going to be maxed out.

        \throw ValueError If the argument is not in scope of this factor, we
        throw a value error

        \return Factor
        """
        if not self.in_scope(Y):
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

        Summing out, or factor marginalization, is defined as the following by
        Koller, Friedman:

        <blockquote>

        Let X be a set of variables and Y \f$\not \in \f$ X a variable. Let
        \f$\phi(X, Y)\f] be a factor. We define the factor marginalization of Y
        in phi, denoted \f$ \sum_Y \phi \f$, to be a factor psi over X such
        that: \f$ \psi(X) = \sum_Y \phi(X,Y) \f$

        </blockquote>


        \param Y the variable that we are going to sum out.

        \throw ValueError We raise a value error if the argument is not in
        the scope of this factor

        \return Factor
        """
        if not self.in_scope(Y):
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

        \see Factor.sumout_var(Y)

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
