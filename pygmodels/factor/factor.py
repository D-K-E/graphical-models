"""!
\file factor.py

Defining a factor from Koller and Friedman 2009, p. 106-107
"""

from functools import reduce as freduce
from itertools import combinations, product
from pprint import pprint
from typing import Callable, FrozenSet, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pygmodels.gtype.graphobj import GraphObject
from pygmodels.pgmtype.randomvariable import NumCatRVariable
from pygmodels.value.value import NumericValue
from pygmodels.factor.ftype.abstractfactor import AbstractFactor
from pygmodels.factor.ftype.abstractfactor import FactorScope
from pygmodels.factor.ftype.abstractfactor import FactorDomain
from pygmodels.factor.ftype.abstractfactor import DomainSliceSet
from pygmodels.factor.ftype.abstractfactor import DomainSubset


class BaseFactor(AbstractFactor, GraphObject):
    """"""

    def __init__(
        self,
        gid: str,
        scope_vars: FactorScope,
        factor_fn: Optional[Callable[[DomainSliceSet], NumericValue]] = None,
        data={},
    ):
        """"""
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

        self.factor_fn = factor_fn

        ## cartesian product of factor domain
        self.scope_products: List[Set[Tuple[str, NumericValue]]] = list(
            product(*self.vars_domain())
        )

        ## constant normalization value
        self.Z = self.partition_value(self.vars_domain())

    def __str__(self):
        """"""
        msg = "Factor: " + self.id() + "\n"
        msg += "Scope variables: " + str(self.domain_table)
        msg += "Factor function: " + str(self.factor_fn)
        return msg

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, n: AbstractFactor):
        """!
        Check factor equality based on their domain and codomain values

        \warning this function works for categorical/discrete factors. For
        continuous domain factors, this won't work.

        \todo Adapt to continuous factors as well.
        """
        if not isinstance(n, AbstractFactor):
            return False
        #
        other_domain = n.vars_domain()
        this_domain = self.vars_domain()
        if other_domain != this_domain:
            return False
        #
        for dval in product(*other_domain):
            other_phi = n.phi(dval)
            this_phi = self.phi(dval)
            if this_phi != other_phi:
                return False
        return True

    def is_same(self, n: AbstractFactor):
        """!
        Check if two objects are same using identifier.
        """
        if not isinstance(n, AbstractFactor):
            return False
        return self.id() == n.id()

    def scope_vars(self, f=lambda x: x) -> FactorScope:
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

    def vars_domain(
        self,
        rvar_filter: Callable[[NumCatRVariable], bool] = lambda x: True,
        value_filter: Callable[[NumericValue], bool] = lambda x: True,
        value_transform: Callable[[NumericValue], NumericValue] = lambda x: x,
    ) -> FactorDomain:
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

    @classmethod
    def from_abstract_factor(cls, f: AbstractFactor):
        """!
        \brief make BaseFactor from an AbstractFactor
        """
        svar = f.scope_vars()
        fn = f.phi
        return BaseFactor(gid=f.id(), data=f.data(), factor_fn=fn, scope_vars=svar)

    @classmethod
    def from_joint_vars(cls, svars: FactorScope):
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
        cls, svars: FactorScope, fn: Callable[[DomainSubset], float],
    ):
        """!
        \brief Make a factor from scope variables and a preference function
        """
        return BaseFactor(gid=str(uuid4()), scope_vars=svars, factor_fn=fn)

    @classmethod
    def fdomain(
        cls,
        D: Set[NumCatRVariable],
        rvar_filter: Callable[[NumCatRVariable], bool] = lambda x: True,
        value_filter: Callable[[NumericValue], bool] = lambda x: True,
        value_transform: Callable[[NumericValue], NumericValue] = lambda x: x,
    ) -> FactorDomain:
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

    def phi(self, scope_product: DomainSliceSet) -> float:
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

    def phi_normal(self, scope_product: DomainSliceSet) -> float:
        """!
        \brief normalize a given factor value

        \param scope_product a row in conditional probability table of factor

        \return normalized value preference value

        \see Factor.normalize(phi_result), Factor.phi(scope_product)

        """
        return self.phi(scope_product) / self.Z

    def partition_value(self, domains: FactorDomain):
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
        return sum([self.phi(scope_product=sv) for sv in scope_matches])


class Factor(BaseFactor):
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

        if factor_fn is None:
            factor_fn = self.marginal_joint

        # check all values are positive
        super().__init__(gid=gid, scope_vars=scope_vars, factor_fn=factor_fn, data=data)

    @classmethod
    def from_abstract_factor(cls, f: AbstractFactor):
        """"""
        bfac = BaseFactor.from_abstract_factor(f)
        return cls.from_base_factor(bfac)

    @classmethod
    def from_base_factor(cls, bfac: BaseFactor):
        """!
        Construct normal factor from base factor
        """
        return Factor(
            gid=bfac.id(),
            scope_vars=bfac.scope_vars(),
            factor_fn=bfac.factor_fn,
            data=bfac.data(),
        )

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
        bfac = BaseFactor.from_joint_vars(svars)
        return cls.from_base_factor(bfac)

    @classmethod
    def from_scope_variables_with_fn(
        cls,
        svars: Set[NumCatRVariable],
        fn: Callable[[Set[Tuple[str, NumericValue]]], float],
    ):
        """!
        \brief Make a factor from scope variables and a preference function
        """
        bfac = BaseFactor.from_scope_variables_with_fn(svars, fn)
        return cls.from_base_factor(bfac)

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

    def __call__(self, scope_product: Set[Tuple[str, NumericValue]]) -> float:
        """!
        \brief Make a factor callable to reproduce more function like behavior

        \see Factor.phi(scope_product)
        """
        return self.phi(scope_product)

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

    def __contains__(self, v: Union[NumCatRVariable, str]) -> bool:
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
