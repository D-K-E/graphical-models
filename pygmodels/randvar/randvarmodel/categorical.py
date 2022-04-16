"""!
\file categorical.py Categorical random variable
"""

import math
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from uuid import uuid4

from pygmodels.randvar.randvartype.abstractrandvar import AssociatedValueSet
from pygmodels.randvar.randvartype.baserandvar import BaseRandomVariable
from pygmodels.value.codomain import CodomainValue, Outcome
from pygmodels.value.domain import DomainValue, Domain
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

    def image(self, sampler=lambda x: x) -> AssociatedValueSet:
        """!
        Image of the random variable's function
        """
        return BaseRandomVariable.image(self, sampler=sampler)


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

    def marginal_over(self, evidence_value: float, other) -> float:
        """!
        \brief Compute marginal distribution over other random variable given
        evidence with respect to current random variable.

        Implements the following from Biagini and Campanino 2016, p. 35:
        \f$ \sum_{j=1}^n p(x_i) p(y_j) = p(x_i) \sum_{j=1}^n p(y_j) \f$

        \code{.py}
        >>> input_data = {
        >>>    "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
        >>>    "grade": {"outcome-values": [0.2, 0.4, 0.6], "evidence": 0.2},
        >>>    "dice": {"outcome-values": [i for i in range(1, 7)], "evidence": 1.0 / 6},
        >>> }

        >>> def grade_dist(grade_value: float):
        >>>     if grade_value == 0.2:
        >>>         return 0.25
        >>>     elif grade_value == 0.4:
        >>>         return 0.37
        >>>     elif grade_value == 0.6:
        >>>         return 0.38
        >>>     else:
        >>>         raise ValueError("unknown grade value")

        >>> def fair_dice_dist(dice_value: float):
        >>>     if dice_value in [i for i in range(1, 7)]:
        >>>         return 1.0 / 6.0
        >>>     else:
        >>>         raise ValueError("dice value")


        >>> nid2 = "rvar2"
        >>> grade = NumCatRVariable(
        >>>    node_id=nid2, input_data=input_data["grade"], distribution=grade_dist
        >>> )
        >>> nid3 = "rvar3"
        >>> dice = NumCatRVariable(
        >>>    node_id=nid3, input_data=input_data["dice"], distribution=fair_dice_dist
        >>> )
        >>> grade.marginal_over(0.2, dice)
        >>> 0.875

        \endcode
        """
        self.type_check(other)
        marginal = self.marginal(evidence_value)
        return other.p_x_fn(phi=lambda x: x * marginal)

    def marginal_over_evidence_key(self, other):
        """!
        Compute marginal using evidence key.
        This means that the evidence is encoded to data associated to
        random variable

        \code{.py}
        >>> input_data = {
        >>>    "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
        >>>    "grade": {"outcome-values": [0.2, 0.4, 0.6], "evidence": 0.2},
        >>>    "dice": {"outcome-values": [i for i in range(1, 7)], "evidence": 1.0 / 6},
        >>> }

        >>> def grade_dist(grade_value: float):
        >>>     if grade_value == 0.2:
        >>>         return 0.25
        >>>     elif grade_value == 0.4:
        >>>         return 0.37
        >>>     elif grade_value == 0.6:
        >>>         return 0.38
        >>>     else:
        >>>         raise ValueError("unknown grade value")

        >>> def fair_dice_dist(dice_value: float):
        >>>     if dice_value in [i for i in range(1, 7)]:
        >>>         return 1.0 / 6.0
        >>>     else:
        >>>         raise ValueError("dice value")


        >>> nid2 = "rvar2"
        >>> grade = NumCatRVariable(
        >>>    node_id=nid2, input_data=input_data["grade"], distribution=grade_dist
        >>> )
        >>> nid3 = "rvar3"
        >>> dice = NumCatRVariable(
        >>>    node_id=nid3, input_data=input_data["dice"], distribution=fair_dice_dist
        >>> )
        >>> grade.marginal_over_evidence_key(dice)
        >>> 0.875

        \endcode
        """
        self.has_evidence()
        data = self.data()
        evidence_value = data["evidence"]
        return self.marginal_over(evidence_value, other)

    def expected_value(self) -> float:
        """!
        \brief Expected value of random variable
        from Koller, Friedman 2009, p. 31

        Implements the following formula:
        \f$ \sum_{i=1}^n x_i p(x_i) \f$

        \code{.py}
        >>> input_data = {
        >>>    "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
        >>>    "grade": {"outcome-values": [0.2, 0.4, 0.6], "evidence": 0.2},
        >>>    "dice": {"outcome-values": [i for i in range(1, 7)], "evidence": 1.0 / 6},
        >>> }

        >>> def fair_dice_dist(dice_value: float):
        >>>     if dice_value in [i for i in range(1, 7)]:
        >>>         return 1.0 / 6.0
        >>>     else:
        >>>         raise ValueError("dice value unknown")

        >>> nid3 = "rvar3"
        >>> dice = NumCatRVariable(
        >>>    node_id=nid3, input_data=input_data["dice"], distribution=fair_dice_dist
        >>> )
        >>> dice.expected_value()
        >>> 3.5

        \endcode
        """
        return sum([value * self.p(value) for value in self.values()])

    def P_X_e(self):
        """!
        \brief evaluate probability with given random variable's evidence if it is
        given.

        We output the expected value if there is no evidence associated to
        random variable

        \code{.py}
        >>> input_data = {
        >>>    "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
        >>>    "grade": {"outcome-values": [0.2, 0.4, 0.6], "evidence": 0.2},
        >>>    "dice": {"outcome-values": [i for i in range(1, 7)], "evidence": 1.0 / 6},
        >>> }

        >>> def grade_dist(grade_value: float):
        >>>     if grade_value == 0.2:
        >>>         return 0.25
        >>>     elif grade_value == 0.4:
        >>>         return 0.37
        >>>     elif grade_value == 0.6:
        >>>         return 0.38
        >>>     else:
        >>>         raise ValueError("unknown grade value")

        >>> nid2 = "rvar2"
        >>> grade = NumCatRVariable(
        >>>    node_id=nid2, input_data=input_data["grade"], distribution=grade_dist
        >>> )
        >>> grade.P_X_e()
        >>> 0.25

        \endcode
        """
        if "evidence" in self.data():
            return self.marginal(self.data()["evidence"])
        return self.expected_value()

    def max_marginal_e(self):
        """!
        evaluate max probability with given random variable's evidence if it is
        present.

        \code{.py}
        >>> input_data = {
        >>>    "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
        >>>    "grade": {"outcome-values": [0.2, 0.4, 0.6], "evidence": 0.2},
        >>>    "dice": {"outcome-values": [i for i in range(1, 7)], "evidence": 1.0 / 6},
        >>> }

        >>> def grade_dist(grade_value: float):
        >>>     if grade_value == 0.2:
        >>>         return 0.25
        >>>     elif grade_value == 0.4:
        >>>         return 0.37
        >>>     elif grade_value == 0.6:
        >>>         return 0.38
        >>>     else:
        >>>         raise ValueError("unknown grade value")

        >>> nid2 = "rvar2"
        >>> grade = NumCatRVariable(
        >>>    node_id=nid2, input_data=input_data["grade"], distribution=grade_dist
        >>> )
        >>> grade.max_marginal_e()
        >>> 0.25

        \endcode
        """
        if "evidence" in self.data():
            return self.marginal(self.data()["evidence"])
        return self.max()

    def min_marginal_e(self):
        """!
        \brief evaluate min probability with given random variable's evidence
        if it is present.

        \code{.py}
        >>> input_data = {
        >>>    "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
        >>>    "grade": {"outcome-values": [0.2, 0.4, 0.6], "evidence": 0.2},
        >>>    "dice": {"outcome-values": [i for i in range(1, 7)], "evidence": 1.0 / 6},
        >>> }

        >>> def grade_dist(grade_value: float):
        >>>     if grade_value == 0.2:
        >>>         return 0.25
        >>>     elif grade_value == 0.4:
        >>>         return 0.37
        >>>     elif grade_value == 0.6:
        >>>         return 0.38
        >>>     else:
        >>>         raise ValueError("unknown grade value")

        >>> nid2 = "rvar2"
        >>> grade = NumCatRVariable(
        >>>    node_id=nid2, input_data=input_data["grade"], distribution=grade_dist
        >>> )
        >>> grade.min_marginal_e()
        >>> 0.25

        \endcode

        """
        if "evidence" in self.data():
            return self.marginal(self.data()["evidence"])
        return self.min()

    def p_x_fn(self, phi: Callable[[float], float]):
        """!
        probability of a function applied to random variable
        from Biagini, Campanino, 2016, p. 11
        implements:
        \f$\sum_{i=1}^n \phi(x_i) p(x_i) \f$
        """
        return sum(self.apply(lambda x: phi(x) * self.p(x)))

    def apply(self, phi: Callable[[NumericValue], NumericValue]):
        """!
        \brief apply function phi to possible outcomes of the random variable
        """
        return [phi(v) for v in self.values()]

    def apply_to_marginals(self, phi: Callable[[float], float]) -> List[float]:
        """!
        \brief apply function phi to marginals of the random variable
        """
        return self.apply(lambda x: phi(self.marginal(x)))

    def expected_apply(self, phi: Callable[[NumericValue], NumericValue]):
        """!"""
        return self.p_x_fn(phi)

    def variance(self):
        """!
        Koller, Friedman 2009, p. 33
        \f$ E[X^2] - (E[X])^2 \f$
        """
        E_X2 = self.expected_apply(phi=lambda x: x * x)
        return E_X2 - (self.expected_value() ** 2)

    def standard_deviation(self):
        """!
        standard deviation Koller, Friedman 2009, p. 33
        """
        return math.sqrt(self.variance())

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

    def joint(self, v):
        """!
        Joint distribution of two random variables
        from Biagini and Campanino 2016 p. 35

        """
        self.type_check(v)
        return self.P_X_e() * v.P_X_e()

    def max_joint(self, v):
        """!
        max joint probability
        """
        self.type_check(v)
        return self.max_marginal_e() * v.max_marginal_e()

    def conditional(self, other):
        """!
        Conditional probability distribution (Bayes rule)
        from Koller and Friedman
        """
        self.type_check(other)
        return self.joint(other) / other.P_X_e()

    def max_conditional(self, other):
        """!"""
        self.type_check(other)
        joint = self.max_joint(other)
        return max([v for v in other.apply_to_marginals(lambda x: joint / x)])
