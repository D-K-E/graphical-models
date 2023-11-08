"""!
\file basefactor.py Basic factor that implements an AbstractFactor
"""

from functools import reduce as freduce
from itertools import combinations, product
from typing import Callable, Optional, Set
from uuid import uuid4

from pygmodels.factor.factortype.abstractfactor import (
    AbstractFactor,
    DomainSliceSet,
    DomainSubset,
    FactorDomain,
    FactorScope,
)
from pygmodels.graph.graphtype.graphobj import GraphObject
from pygmodels.randvar.randvartype.abstractrandvar import (
    AbstractRandomVariable,
)
from pygmodels.randvar.randvarops.baserandvarops import RandomVariableOps
from pygmodels.value.value import NumericValue

from pygmodels.utils import is_type, is_optional_type
from types import FunctionType, LambdaType


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
        is_type(scope_vars, "scope_vars", FactorScope, True)
        is_optional_type(factor_fn, "factor_fn", FunctionType, True)
        for svar in scope_vars:
            vs = RandomVariableOps.values(svar, sampler=lambda x: x)  # .values()
            if any([v < 0 for v in vs]):
                msg = "Scope variables contain a negative value."
                msg += " Negative factors are not allowed"
                raise ValueError(msg)

        ## random variables belonging to this factor
        self.svars = scope_vars

        self.factor_fn = factor_fn

    def __str__(self):
        """"""
        msg = "Factor: " + self.id() + "\n"
        msg += "Scope variables: " + str({s.id(): s for s in self.scope_vars()})
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
        def rvar_filter(x: AbstractRandomVariable) -> bool:
            return True

        def value_filter(x: NumericValue) -> bool:
            return True

        def value_transform(x: NumericValue) -> NumericValue:
            return x

        other_domain = [
            s.value_set(value_filter=value_filter, value_transform=value_transform)
            for s in n.scope_vars()
            if rvar_filter(s)
        ]
        this_domain = [
            s.value_set(value_filter=value_filter, value_transform=value_transform)
            for s in self.scope_vars()
            if rvar_filter(s)
        ]
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
        is_type(f, "f", LambdaType, True)
        return f(self.svars)

    @classmethod
    def from_abstract_factor(cls, f: AbstractFactor):
        """!
        \brief make BaseFactor from an AbstractFactor
        """
        is_type(f, "f", AbstractFactor, True)
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
        is_type(f, "f", FactorScope, True)
        return BaseFactor(gid=str(uuid4()), scope_vars=svars)

    @classmethod
    def from_scope_variables_with_fn(
        cls,
        svars: FactorScope,
        fn: Callable[[DomainSubset], float],
    ):
        """!
        \brief Make a factor from scope variables and a preference function
        """
        is_type(f, "f", FactorScope, True)
        is_type(fn, "fn", FunctionType, True)
        return BaseFactor(gid=str(uuid4()), scope_vars=svars, factor_fn=fn)

    def __call__(self, scope_product: DomainSliceSet) -> float:
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
        is_type(scope_product, "scope_product", DomainSliceSet, True)
        return self.factor_fn(scope_product)

    def partition_value(self, domains: FactorDomain) -> float:
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
        is_type(domains, "domains", FactorDomain, True)
        scope_matches = list(product(*domains))
        return sum([self.phi(scope_product=sv) for sv in scope_matches])
