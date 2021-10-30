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

from pygmodels.factor.ftype.basefactor import BaseFactor
from pygmodels.factor.factorf.factorops import FactorOps


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
        domains = FactorOps.factor_domain(self, D=self.scope_vars())
        self.scope_products = list(product(*domains))
        return sum([self.phi(scope_product=sv) for sv in FactorOps.cartesian(self)])

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
