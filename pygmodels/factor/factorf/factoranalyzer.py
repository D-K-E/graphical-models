"""!
\file factoranalyzer.py Analyzes factors

The main objective of these functions is to analyze a given factor
or a set of factors.
"""

from typing import Callable, FrozenSet, List, Optional, Set, Tuple, Union

from pygmodels.factor.factorf.factorops import FactorOps
from pygmodels.factor.ftype.abstractfactor import AbstractFactor
from pygmodels.pgmtype.randomvariable import NumCatRVariable, NumericValue
from pygmodels.value.value import FiniteVSet, OrderedFiniteVSet

ProbabilityValue = NumericValue


class FactorAnalyzer:
    """!
    Analyzes a given factor
    """

    @staticmethod
    def _compare_prob_value(
        f: AbstractFactor,
        comp_fn: Callable[[float, float], bool] = lambda phi_s, mx: phi_s > mx,
        comp_v: float = float("-inf"),
    ) -> Tuple[Set[OrderedFiniteVSet], ProbabilityValue]:
        """"""
        if not isinstance(f, AbstractFactor):
            raise TypeError("The object must be of Factor type")

        cval = comp_v
        out_val = None
        for sp in FactorOps.cartesian(f):
            ss = frozenset(sp)
            phi_s = f.phi(ss)
            if comp_fn(phi_s, cval):
                cval = phi_s
                out_val = ss
        return out_val, cval

    @staticmethod
    def _max_prob_value(
        f: AbstractFactor,
    ) -> Tuple[Set[OrderedFiniteVSet], ProbabilityValue]:
        """!
        \brief obtain highest yielding domain value and its associated codomain
        member

        Obtain the highest preference value yielding domain member of this
        factor with its associated value.
        """
        return FactorAnalyzer._compare_prob_value(
            f=f, comp_fn=lambda phi_s, mx: phi_s > mx, comp_v=float("-inf")
        )

    @staticmethod
    def _min_prob_value(
        f: AbstractFactor,
    ) -> Tuple[Set[OrderedFiniteVSet], ProbabilityValue]:
        """!
        \brief obtain highest yielding domain value and its associated codomain
        member

        Obtain the highest preference value yielding domain member of this
        factor with its associated value.
        """
        return FactorAnalyzer._compare_prob_value(
            f=f, comp_fn=lambda phi_s, mx: phi_s < mx, comp_v=float("inf")
        )

    @staticmethod
    def max_probability(f: AbstractFactor) -> ProbabilityValue:
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
        if not isinstance(f, AbstractFactor):
            raise TypeError("The object must be of Factor type")

        mval, mprob = FactorAnalyzer._max_prob_value(f)
        return mprob

    @staticmethod
    def max_value(f: AbstractFactor) -> Set[OrderedFiniteVSet]:
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
        mval, mrob = FactorAnalyzer._max_prob_value(f)
        return mval

    @staticmethod
    def min_probability(f: AbstractFactor) -> ProbabilityValue:
        """!
        \brief minimum preference value for this factor

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
        >>> mval = self.bc.min_probability()
        >>> print(mval)
        >>> 0.1

        \endcode
        """
        if not isinstance(f, AbstractFactor):
            raise TypeError("The object must be of Factor type")

        mval, mprob = FactorAnalyzer._min_prob_value(f)
        return mprob

    @staticmethod
    def min_value(f: AbstractFactor) -> Set[OrderedFiniteVSet]:
        """!
        \brief minimum factor value for this factor

        Obtain the lowest probability yielding value from the domain of the
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
        >>> mval = self.bc.min_value()
        >>> print(mval)
        >>> {[("B", 50), ("C", 10)]}

        \endcode
        """
        mval, mrob = FactorAnalyzer._min_prob_value(f)
        return mval

    @staticmethod
    def normalize(f: AbstractFactor, phi_result: float) -> float:
        """!
        \brief Normalize a given factorization result by dividing it to the
        value of partition function value Z

        \param phi_result the preference value to be normalized with partition
        constant

        \return normalized preference value
        """
        fdomain = FactorOps.factor_domain(f)
        Z = FactorOps.partition_value(fdomain)

        return phi_result / Z
