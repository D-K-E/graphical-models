"""!
\file factor.py

Defining a factor from Koller and Friedman 2009, p. 106-107
"""

from functools import reduce as freduce
from itertools import combinations, product
from pprint import pprint
from typing import Callable, FrozenSet, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pygmodels.factor.factorf.factorops import FactorBoolOps, FactorOps
from pygmodels.factor.ftype.abstractfactor import (
    AbstractFactor,
    DomainSliceSet,
    DomainSubset,
    FactorDomain,
    FactorScope,
)
from pygmodels.factor.ftype.basefactor import BaseFactor
from pygmodels.graph.gtype.graphobj import GraphObject
from pygmodels.pgm.pgmtype.randomvariable import NumCatRVariable
from pygmodels.value.value import NumericValue


class Factor(BaseFactor):
    """!
    \brief Factor from Koller and Friedman 2009, p. 106-107

    """

    def __init__(
        self,
        gid: str,
        scope_vars: Set[NumCatRVariable],
        factor_fn: Optional[
            Callable[[Set[Tuple[str, NumCatRVariable]]], float]
        ] = None,
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

        super().__init__(
            gid=gid, scope_vars=scope_vars, factor_fn=factor_fn, data=data
        )

        ## scope variable hash table
        self.domain_table = {s.id(): s for s in self.scope_vars()}

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

    def __call__(self, scope_product: Set[Tuple[str, NumericValue]]) -> float:
        """!
        \brief Make a factor callable to reproduce more function like behavior

        \see Factor.phi(scope_product)
        """
        return self.phi(scope_product)

    def marginal_joint(
        self, scope_product: Set[Tuple[str, NumericValue]]
    ) -> float:
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
            hasv, var = FactorOps.find_var(self, var_id)
            if hasv is False:
                raise ValueError(
                    "Unknown variable id among arguments: " + var_id
                )
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
