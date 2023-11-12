"""!
\file boolops.py Operations outputting booleans with numeric categorical
variables 
"""
from pygmodels.randvar.randvarmodel.categorical import NumCatRandomVariable
from pygmodels.value.codomain import CodomainValue
from typing import Any, Callable, FrozenSet, List, Optional, Set, Tuple


class BoolOps:
    """!
    Basic operations outputting booleans that can be applied to categorical
    random variables
    """

    @staticmethod
    def has_evidence(r: NumCatRandomVariable, shouldRaiseError: bool = False) -> bool:
        """!
        \brief Check if any evidence is associated with this random variable

        \throws ValueError We raise a value error if there is no evidence
        associated to random variable.

        \todo Update documentation evidence has its own type now.

        \todo test

        \code{.py}

        >>> nid1 = "rvar1"
        >>> input_data = {
        >>>    "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
        >>>    "grade": {"outcome-values": [0.2, 0.4, 0.6], "evidence": 0.2},
        >>>    "dice": {"outcome-values": [i for i in range(1, 7)], "evidence": 1.0 / 6},
        >>>    "noevidence": {"outcome-values": [i for i in range(1, 5)]}
        >>> }

        >>> def intelligence_dist(intelligence_value: float) -> float:
        >>>    if intelligence_value == 0.1:
        >>>        return 0.7
        >>>    elif intelligence_value == 0.9:
        >>>        return 0.3
        >>>    else:
        >>>        return 0.0

        >>> # intelligence
        >>> intelligence = NumCatRVariable(
        >>>    node_id=nid1,
        >>>    input_data=input_data["intelligence"],
        >>>    marginal_distribution=intelligence_dist,
        >>> )
        >>> intelligence.has_evidence()
        >>> None
        >>> # no evidence
        >>> noev = NumCatRVariable(
        >>>    node_id=nid1,
        >>>    input_data=input_data["noevidence"],
        >>>    marginal_distribution=intelligence_dist,
        >>> )
        >>> noev.has_evidence()
        >>> ValueError

        \endcode
        """
        data = r.data()
        if "evidence" not in data:
            if shouldRaiseError:
                msg = "Evidence " + " could not be found with in"
                msg += " attributed data of this random variable"
                raise ValueError(msg)
            else:
                return False
        return True

    @staticmethod
    def is_numeric(v: object) -> bool:
        """!
        \brief check if v is whether float or int

        \param v any value.

        \todo test

        \code{.py}
        >>> NumCatRVariable.is_numeric("foo")
        >>> False
        >>> NumCatRVariable.is_numeric(1)
        >>> True
        \endcode
        """
        numt = (float, int)
        if isinstance(v, CodomainValue):
            return isinstance(v.value, numt)
        return isinstance(v, numt)
