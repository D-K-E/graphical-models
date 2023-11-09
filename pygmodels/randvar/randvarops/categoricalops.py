"""!
\file categoricalops.py Contains categorical random variable operations
"""

import math
from typing import Any, Callable, FrozenSet, List, Optional, Set, Tuple

from pygmodels.randvar.randvarmodel.categorical import (
    CatRandomVariable,
    NumCatRandomVariable,
)
from pygmodels.randvar.randvarops.numeric.boolops import BoolOps
from pygmodels.randvar.randvarops.baserandvarops import RandomVariableOps
from pygmodels.randvar.randvartype.abstractrandvar import (
    AbstractEvidence,
    AbstractRandomVariable,
)
from pygmodels.utils import is_type
from pygmodels.value.codomain import CodomainValue
from pygmodels.value.value import NumericValue


class NumericOps:
    """!
    Operations that apply to categorical random variables that output numeric
    values
    """

    @staticmethod
    def p_x_fn(
        r: CatRandomVariable,
        phi: Callable[[CodomainValue], NumericValue],
        sampler=lambda x: x,
    ) -> NumericValue:
        """!
        probability of a function applied to random variable
        from Biagini, Campanino, 2016, p. 11
        implements:
        \f$\sum_{i=1}^n \phi(x_i) p(x_i) \f$

        """
        outphi = phi
        return sum(
            RandomVariableOps.apply(
                r=r, phi=lambda x: outphi(x) * r.p(x), sampler=sampler
            )
        )

    @staticmethod
    def apply_to_marginals(
        r: CatRandomVariable, phi: Callable[[NumericValue], NumericValue]
    ) -> List[NumericValue]:
        """!
        \brief apply function phi to marginals of the random variable

        """
        outphi = phi
        rvar = r
        return RandomVariableOps.apply(rvar, phi=lambda x: outphi(rvar.p(x)))

    @staticmethod
    def expected_apply(
        r: CatRandomVariable, phi: Callable[[NumericValue], NumericValue]
    ) -> NumericValue:

        """!
        """
        return NumericOps.p_x_fn(r, phi)

    @staticmethod
    def reduce_to_value(r: CatRandomVariable, val: CodomainValue):
        """!
        \brief reduce outcomes of this random variable to val

        \param val reduction value. The final value to which random variable is
        reduced

        \throws TypeError if the val is not numeric we raise a type error.
        """
        if not BoolOps.is_numeric(val):
            raise TypeError("Reduction value must be numeric (int, float)")
        vs = frozenset([v for v in r.image() if v.value == val.value])
        r._outs = vs
        return r
