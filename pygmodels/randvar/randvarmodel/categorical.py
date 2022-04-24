"""!
\file categorical.py Categorical random variable
"""

import math
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from uuid import uuid4

from pygmodels.randvar.randvartype.abstractrandvar import AssociatedValueSet
from pygmodels.randvar.randvartype.baserandvar import BaseRandomVariable
from pygmodels.value.codomain import CodomainValue, Outcome
from pygmodels.value.domain import Domain, DomainValue
from pygmodels.value.value import NumericValue


class CatRandomVariable(BaseRandomVariable):
    """!
    \brief A discrete/categorical random variable \see RandomVariable
    """

    def __init__(
        self,
        randvar_id: str,
        randvar_name: Optional[str] = None,
        data: Optional[dict] = None,
        input_data: Optional[Domain] = None,
        f: Callable[[DomainValue], CodomainValue] = lambda x: x,
        marginal_distribution: Callable[
            [CodomainValue], float
        ] = lambda x: 1.0,
    ):
        """!
        \brief Constructor for categorical/discrete random variable

        \param marginal_distribution a function that takes in a value from
        codomain of the random variable and outputs a value in the range [0,1].
        Notice that is not a local distribution, it should be the marginal
        distribution that is independent of local structure.

        \throws ValueError We raise a value error if the probability values
        associated to outcomes add up to a value bigger than one.

        For other parameters and the definition of a random variable \see
        BaseRandomVariable .

        A simple data specification is provided for passing evidences and
        input. The possible outcomes key holds a set of values belonging to
        space of possible outcomes. If the input data just contains a key as
        'possible-outcomes', we suppose that it contains a PossibleOutcomes
        object which represents the space of all possible outcomes of the
        measurable event set associated to random variable.

        The function associated to our random variable transforms the set of
        possible outcomes to values as per its definition in Koller, Friedman,
        2009, p. 20. Lastly we check whether obtained, or associated
        outcome-values satisfy the probability rule by checking if the
        probabilities associated to these values add up to one.

        \code{.py}

        >>> students = PossibleOutcomes(frozenset(["student_1", "student_2"]))
        >>> grade_f = lambda x: "F" if x == "student_1" else "A"
        >>> grade_distribution = lambda x: 0.1 if x == "F" else 0.9
        >>> indata = {"possible-outcomes": students}
        >>> rvar = CatRandomVariable(
        >>>    input_data=indata,
        >>>    node_id="myrandomvar",
        >>>    f=grade_f,
        >>>    marginal_distribution=grade_distribution
        >>> )

        \endcode
        """
        super().__init__(
            randvar_id=randvar_id,
            randvar_name=randvar_name,
            data=data,
            input_data=input_data,
            f=f,
            marginal_distribution=marginal_distribution,
        )

    def marginal(self, value: CodomainValue) -> NumericValue:
        """!
        \brief marginal distribution that is the probability of an outcome

        from Biagini, Campanino, 2016, p. 35
        <blockquote>
        Marginal distribution of X is the function: \f$p_1(x_i) = P(X=x_i)\f$
        </blockquote>

        \see CatRandomVariable.p

        \returns probability value associated to value
        """
        return self.p(value)

    def image(self) -> AssociatedValueSet:
        """!
        Image of the random variable's function
        """
        return BaseRandomVariable.image(self, sampler=lambda x: x)


class NumCatRandomVariable(CatRandomVariable):
    """!
    \brief Numerical categorical random variable object

    This is mostly the same as \see CatRandomVariable. The main difference is that
    the function associated to random variable produces a numeric value as an
    outcome
    """

    def __init__(
        self,
        node_id: str,
        input_data: Dict[str, Outcome],
        f: Callable[[Outcome], NumericValue] = lambda x: x,
        marginal_distribution: Callable[[NumericValue], float] = lambda x: 1.0,
    ):
        """!
        \brief constructor for Numeric Categorical Random Variable

        \see CatRandomVariable for explanation of parameters.
        The numeric categorical random variable is just as it says, a numeric
        categorical random variable. The outcome values of this random variable
        is numeric, that is it can be integer or float. For facilitating
        operations we treat everything as float.

        \code{.py}
        >>> nid1 = "rvar1"
        >>> input_data = {
        >>>    "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
        >>>    "grade": {"outcome-values": [0.2, 0.4, 0.6], "evidence": 0.2},
        >>>    "dice": {"outcome-values": [i for i in range(1, 7)], "evidence": 1.0 / 6},
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
        \endcode

        """
        super().__init__(
            node_id=node_id,
            input_data=input_data,
            f=f,
            marginal_distribution=marginal_distribution,
        )

    def apply(self, phi: Callable[[NumericValue], NumericValue]):
        """!
        \brief apply function phi to possible outcomes of the random variable
        """
        return [phi(v) for v in self.values()]

    # def mk_new_rvar(self, phi: Callable[[float], float]):
    #     """!
    #     make a new random variable from given function with same distribution
    #     """
    #     return NumCatRVariable(
    #         node_id=str(uuid4()),
    #         f=phi,
    #         input_data=self.data(),
    #         distribution=self.dist,
    #     )
