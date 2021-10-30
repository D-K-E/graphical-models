"""!
Implementation of a random variable
"""

import math
from random import choice
from typing import Any, Callable, Dict, FrozenSet, List, Set, Tuple
from uuid import uuid4

from pygmodels.gtype.node import Node
from pygmodels.value.codomain import (
    CodomainValue,
    Outcome,
    PossibleOutcomes,
)
from pygmodels.value.value import NumericValue
from pygmodels.value.domain import DomainValue


class RandomVariable(Node):
    """!
    \brief a Random Variable as defined by Koller, Friedman 2009, p. 20

    Citing from Koller, Friedman:
    <blockquote>
    Formally, a random variable, such as Grade, is defined by a function that
    associates with each outcome in \f$\Omega\f$ a value.
    </blockquote>

    It is important to note that domain and codomain of random variables are
    quite ambiguous. The \f$\Omega\f$ in the definition is set of possible
    outcomes, \see PossibleOutcomes object. In the context of probabilistic
    graphical models each random variable is also considered as a \see Node of
    a \see Graph. This object is meant to be a base class for further needs.
    It lacks quite a bit of methods. Hence it can not be used directly in a
    \see PGModel.
    """

    def __init__(
        self,
        node_id: str,
        data: Any,
        f: Callable[[Outcome], CodomainValue] = lambda x: x,
    ):
        """!
        \brief Constructor of a random variable

        \param data The data associated to random variable can be anything
        \param node_id identifier of random variable. Same identifier is used
        as node identifier in a graph.
        \param f a function who takes data or from data, and outputs anything.

        \returns a random variable instance
        """
        super().__init__(node_id=node_id, data=data)

    def p(self, value: Any):
        raise NotImplementedError


class CatRandomVariable(RandomVariable):
    """!
    \brief A discrete/categorical random variable \see RandomVariable
    """

    def __init__(
        self,
        node_id: str,
        input_data: Dict[str, Any],
        f: Callable[[Outcome], CodomainValue] = lambda x: x,
        marginal_distribution: Callable[[CodomainValue], float] = lambda x: 1.0,
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
        RandomVariable .

        A simple data specification is provided for passing evidences and
        input.
        The possible outcomes key holds a set of values belonging to space of
        possible outcomes. If the input data just contains a key as
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
        data = {}
        data.update(input_data)
        if "possible-outcomes" in input_data:
            data["outcome-values"] = frozenset(
                [f(v) for v in input_data["possible-outcomes"].data]
            )
        super().__init__(node_id=node_id, data=data, f=f)
        if "outcome-values" in data:
            psum = sum(list(map(marginal_distribution, data["outcome-values"])))
            if psum > 1 and psum < 0:
                raise ValueError("probability sum bigger than 1 or smaller than 0")
        self.dist = marginal_distribution

    def p(self, value: CodomainValue) -> float:
        """!
        \brief probability of given outcome value as per the associated
        distribution

        \param value a member of \f$\Omega\f$ set of possible outcomes.

        \returns probability value associated to the outcome
        """
        return self.dist(value)

    def marginal(self, value: CodomainValue) -> float:
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

    def values(self):
        """!
        \brief outcome values of the random variable

        \see CatRandomVariable constructor for more explanation about outcome
        values and their relation to random variables. \see
        CatRandomVariable.value_set for a more functional version of this
        function which let's you associate several transformations and filters
        before obtaining outcomes.

        \throws KeyError We raise a key error if there are no values associated
        to this random variable.

        \returns possible outcomes associated to this random variable.

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
        >>> rvar.values()
        >>> frozenset(["A", "F"])

        \endcode
        """
        vdata = self.data()
        if "outcome-values" not in vdata:
            raise KeyError("This random variable has no associated set of values")
        return vdata["outcome-values"]

    def value_set(
        self, value_filter=lambda x: True, value_transform=lambda x: x,
    ) -> FrozenSet[Tuple[str, NumericValue]]:
        """!
        \brief the outcome value set of the random variable.

        \param value_filter function for filtering out values during the
        retrieval.

        \param value_transfom function for transforming values during the
        retrieval

        \returns codomain of random variable, that is possible outcomes
        associated to random variable

        This is basically the codomain of the function associated to random
        variable. Notice that this is completely different from probabilities
        and other statistical discussion.
        We also brand each value with the identifier of this random variable.
        When we are dealing with categorical random variables, this function
        should work, however for continuous codomains it would not really work.

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
        >>> rvar.value_set(
        >>>         value_transform=lambda x: x.lower(),
        >>>         value_filter=lambda x: x != "A"
        >>> )
        >>> frozenset([("myrandomvar","f")])

        \endcode
        """
        sid = self.id()
        return frozenset(
            [
                (sid, value_transform(v))
                for v in self.values()
                if value_filter(v) is True
            ]
        )


class NumCatRVariable(CatRandomVariable):
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

    @staticmethod
    def type_check(other: Any) -> None:
        """!
        \brief simple function for checking whether the other is also a
        NumCatRVariable

        \param other it can be anything

        \throws TypeError if the other is not a NumCatRVariable, we raise a type
        error

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
        >>> NumCatRVariable.type_check("my numeric categorical variable")
        >>> TypeError("other arg must be of type NumCatRVariable, it is str")
        >>> NumCatRVariable.type_check(intelligence)
        >>> None

        \endcode
        """
        if isinstance(other, NumCatRVariable) is False:
            raise TypeError(
                "other arg must be of type NumCatRVariable, it is " + type(other)
            )

    def has_evidence(self) -> None:
        """!
        \brief Check if any evidence is associated with this random variable

        \throws ValueError We raise a value error if there is no evidence
        associated to random variable.

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
        data = self.data()
        if "evidence" not in data:
            msg = "Evidence " + " could not be found with in"
            msg += " attributed data of this random variable"
            raise ValueError(msg)

    def max(self) -> float:
        """!
        \brief maximum marginal value

        We return the highest marginal/probability.

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
        >>>        raise ValueError(
        >>>            "intelligence_value does not belong to possible outcomes"
        >>>        )

        >>> # intelligence
        >>> intelligence = NumCatRVariable(
        >>>    node_id=nid1,
        >>>    input_data=input_data["intelligence"],
        >>>    distribution=intelligence_dist,
        >>> )
        >>> intelligence.max()
        >>> 0.7

        \endcode
        """
        mx, mxv = self.min_max_marginal_with_outcome(is_min=False)
        return mx

    def min(self) -> float:
        """!
        \brief minimum marginal value

        We return the lowest marginal/probability.

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
        >>>        raise ValueError("unknown intelligence event/possible outcome")

        >>> # intelligence
        >>> intelligence = NumCatRVariable(
        >>>    node_id=nid1,
        >>>    input_data=input_data["intelligence"],
        >>>    distribution=intelligence_dist,
        >>> )
        >>> intelligence.min()
        >>> 0.3

        \endcode

        """
        mx, mxv = self.min_max_marginal_with_outcome(is_min=True)
        return mx

    def min_max_marginal_with_outcome(self, is_min: bool) -> Tuple[float, NumericValue]:
        """!
        \brief returns highest/lowest probability with its outcome

        \param is_min flag for specifying whether to return lowest or highest
        probability-outcome pair
        """
        mx = float("inf") if is_min else float("-inf")
        mxv = None
        for v in self.values():
            marginal = self.marginal(v)
            cond = mx > marginal if is_min else mx < marginal
            if cond:
                mx = marginal
                mxv = v
        return mx, mxv

    def max_marginal_value(self) -> NumericValue:
        """!
        \brief highest probability outcome

        Notice that this gives the outcome not the probability

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
        >>>        raise ValueError("unknown intelligence event/possible outcome")

        >>> # intelligence
        >>> intelligence = NumCatRVariable(
        >>>    node_id=nid1,
        >>>    input_data=input_data["intelligence"],
        >>>    distribution=intelligence_dist,
        >>> )
        >>> intelligence.max_marginal_value()
        >>> 0.1

        \endcode
        """
        mx, mxv = self.min_max_marginal_with_outcome(is_min=False)
        return mxv

    def min_marginal_value(self) -> NumericValue:
        """!
        \brief highest probability outcome

        Notice that this gives the outcome not the probability

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
        >>>        raise ValueError("unknown intelligence event/possible outcome")

        >>> # intelligence
        >>> intelligence = NumCatRVariable(
        >>>    node_id=nid1,
        >>>    input_data=input_data["intelligence"],
        >>>    distribution=intelligence_dist,
        >>> )
        >>> intelligence.max_marginal_value()
        >>> 0.1

        \endcode
        """
        mx, mxv = self.min_max_marginal_with_outcome(is_min=True)
        return mxv

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

    @staticmethod
    def is_numeric(v: Any) -> bool:
        """!
        \brief check if v is whether float or int

        \param v any value.

        \code{.py}
        >>> NumCatRVariable.is_numeric("foo")
        >>> False
        >>> NumCatRVariable.is_numeric(1)
        >>> True
        \endcode
        """
        return True if isinstance(v, (float, int)) else False

    def add_evidence(self, evidence_value: NumericValue):
        """!
        \brief add evidence to random variable

        \throws TypeError if the evidence is not a numeric value

        \code{.py}

        >>> nid1 = "rvar1"
        >>> input_data = {
        >>>    "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
        >>>    "noevidence": {"outcome-values": [0.1, 0.9]}
        >>> }

        >>> def intelligence_dist(intelligence_value: float) -> float:
        >>>    if intelligence_value == 0.1:
        >>>        return 0.7
        >>>    elif intelligence_value == 0.9:
        >>>        return 0.3
        >>>    else:
        >>>        return 0.0

        >>> # intelligence
        >>> noev = NumCatRVariable(
        >>>    node_id=nid1,
        >>>    input_data=input_data["noevidence"],
        >>>    marginal_distribution=intelligence_dist,
        >>> )
        >>> noev.add_evidence(0.9)
        >>> # now noev is same as intelligence

        \endcode
        """
        if isinstance(evidence_value, int):
            evidence_value = float(evidence_value)
        if not self.is_numeric(evidence_value):
            raise TypeError("evidence must be a numeric (int, float) value")
        e = {"evidence": evidence_value}
        self.update_data(e)

    def pop_evidence(self):
        """!
        \brief remove evidence from this random variable

        \code{.py}

        >>> nid1 = "rvar1"
        >>> input_data = {
        >>>    "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
        >>>    "noevidence": {"outcome-values": [0.1, 0.9]}
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
        >>> intelligence.pop_evidence()
        >>> # now intelligence is same as noev

        \endcode
        """
        data = self.data()
        if "evidence" in data:
            data.pop("evidence")
        self.update_data(data)

    def reduce_to_value(self, val: NumericValue):
        """!
        \brief reduce outcomes of this random variable to val

        \param val reduction value. The final value to which random variable is
        reduced

        \throws TypeError if the val is not numeric we raise a type error.
        """
        if not self.is_numeric(val):
            raise TypeError("Reduction value must be numeric (int, float)")
        vs = frozenset([v for v in self.values() if v == val])
        vdata = self.data()
        vdata["outcome-values"] = vs
        self.update_data(vdata)

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

    def mk_new_rvar(self, phi: Callable[[float], float]):
        """!
        make a new random variable from given function with same distribution
        """
        return NumCatRVariable(
            node_id=str(uuid4()), f=phi, input_data=self.data(), distribution=self.dist,
        )

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
