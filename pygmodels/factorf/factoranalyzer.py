"""!
\file factoranalyzer.py Analyzes factors

The main objective of these functions is to analyze a given factor
or a set of factors.
"""

from typing import Callable, FrozenSet, List, Optional, Set, Tuple, Union

from pygmodels.pgmtype.abstractpgm import AbstractFactor
from pygmodels.pgmtype.factor import BaseFactor, Factor
from pygmodels.pgmtype.randomvariable import NumCatRVariable, NumericValue


class FactorAnalyzer:
    """!
    Analyzes a given factor
    """

    def __init__(self, f):
        """"""
        if isinstance(f, AbstractFactor):
            fac = Factor.from_abstract_factor(f)
        elif isinstance(f, BaseFactor):
            fac = Factor.from_base_factor(f)
        elif isinstance(f, Factor):
            fac = f
        else:
            raise TypeError("argument must inherit from AbstractFactor object")
        self.factor = fac

    @classmethod
    def _compare_prob_value(
        cls,
        f: Factor,
        comp_fn: Callable[[float, float], bool] = lambda phi_s, mx: phi_s > mx,
        comp_v: float = float("-inf"),
    ):
        """"""
        if not isinstance(f, Factor):
            raise TypeError("The object must be of Factor type")

        cval = comp_v
        out_val = None
        for sp in f.factor_domain():
            ss = frozenset(sp)
            phi_s = f.phi(ss)
            if comp_fn(phi_s, cval):
                cval = phi_s
                out_val = ss
        return out_val, cval

    @classmethod
    def _max_prob_value(cls, f: Factor):
        """!
        \brief obtain highest yielding domain value and its associated codomain
        member

        Obtain the highest preference value yielding domain member of this
        factor with its associated value.
        """
        return cls._compare_prob_value(
            f=f, comp_fn=lambda phi_s, mx: phi_s > mx, comp_v=float("-inf")
        )

    @classmethod
    def _min_prob_value(cls, f: Factor):
        """!
        \brief obtain highest yielding domain value and its associated codomain
        member

        Obtain the highest preference value yielding domain member of this
        factor with its associated value.
        """
        return cls._compare_prob_value(
            f=f, comp_fn=lambda phi_s, mx: phi_s < mx, comp_v=float("inf")
        )

    @classmethod
    def cls_max_probability(cls, f: Factor) -> float:
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
        if not isinstance(f, Factor):
            raise TypeError("The object must be of Factor type")

        mval, mprob = cls._max_prob_value(f)
        return mprob

    @classmethod
    def cls_max_value(cls, f: Factor) -> Set[Tuple[str, NumericValue]]:
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
        mval, mrob = cls._max_prob_value(f)
        return mval

    @classmethod
    def cls_min_probability(cls, f: Factor) -> float:
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
        if not isinstance(f, Factor):
            raise TypeError("The object must be of Factor type")

        mval, mprob = cls._min_prob_value(f)
        return mprob

    @classmethod
    def cls_min_value(cls, f: Factor) -> Set[Tuple[str, NumericValue]]:
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
        mval, mrob = cls._min_prob_value(f)
        return mval

    @classmethod
    def cls_normalize(cls, f: Factor, phi_result: float) -> float:
        """!
        \brief Normalize a given factorization result by dividing it to the
        value of partition function value Z

        \param phi_result the preference value to be normalized with partition
        constant

        \return normalized preference value
        """
        return phi_result / f.Z

    def max_value(self):
        """!
        Wrapper of FactorAnalyzer.cls_max_value
        """
        return self.cls_max_value(self.factor)

    def max_probability(self):
        """!
        Wrapper of FactorAnalyzer.cls_max_probability
        """
        return self.cls_max_probability(self.factor)

    def min_value(self):
        """!
        Wrapper of FactorAnalyzer.cls_min_value
        """
        return self.cls_min_value(self.factor)

    def min_probability(self):
        """!
        Wrapper of FactorAnalyzer.cls_min_probability
        """
        return self.cls_min_probability(self.factor)

    def normalize(self, phi_result: float) -> float:
        """!
        Wrapper of FactorAnalyzer.cls_normalize
        """
        return self.cls_normalize(f=self.factor, phi_result=phi_result)
