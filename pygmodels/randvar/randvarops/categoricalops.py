"""!
\file categoricalops.py Contains categorical random variable operations
"""

from typing import Any, Callable, FrozenSet, List, Optional, Set, Tuple

from pygmodels.randvar.randvarmodel.categorical import (
    CatRandomVariable,
    NumCatRandomVariable,
)
from pygmodels.randvar.randvartype.abstractrandvar import (
    AbstractRandomVariable,
    AssociatedValueSet,
    PossibleOutcomes,
)
from pygmodels.value.codomain import CodomainValue
from pygmodels.value.value import NumericValue


class CatRandomVariableOps:
    """!
    Basic operations that can be applied to categorical random variables
    """

    @staticmethod
    def values(r: CatRandomVariable) -> AssociatedValueSet:
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
        return r.image

    @staticmethod
    def value_set(
        r: CatRandomVariable,
        value_filter=lambda x: True,
        value_transform=lambda x: x,
    ) -> FrozenSet[Tuple[str, CodomainValue]]:
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
        sid = r.id()
        return frozenset(
            [
                (sid, value_transform(v))
                for v in CatRandomVariableOps.values(r)
                if value_filter(v) is True
            ]
        )

    @staticmethod
    def p_x_fn(
        r: CatRandomVariable, phi: Callable[[CodomainValue], NumericValue]
    ) -> NumericValue:
        """!
        probability of a function applied to random variable
        from Biagini, Campanino, 2016, p. 11
        implements:
        \f$\sum_{i=1}^n \phi(x_i) p(x_i) \f$
        """
        return sum(CatRandomVariableOps.apply(lambda x: phi(x) * r.p(x)))

    @staticmethod
    def apply(
        r: CatRandomVariable, phi: Callable[[CodomainValue], Any]
    ) -> List[Any]:
        """!
        \brief apply function phi to possible outcomes of the random variable
        """
        return [phi(v) for v in CatRandomVariableOps.values(r)]

    @staticmethod
    def apply_to_marginals(
        r: CatRandomVariable, phi: Callable[[NumericValue], NumericValue]
    ) -> List[NumericValue]:
        """!
        \brief apply function phi to marginals of the random variable
        """
        return CatRandomVariableOps.apply(lambda x: phi(r.marginal(x)))

    @staticmethod
    def expected_apply(
        r: CatRandomVariable, phi: Callable[[NumericValue], NumericValue]
    ) -> NumericValue:

        """!"""
        return CatRandomVariableOps.p_x_fn(r, phi)


class NumCatRandomVariableOps:
    """!
    Numeric Categorical Random Variable operations
    """

    @staticmethod
    def add_evidence(
        r: NumCatRandomVariable, evidence_value: CodomainValue
    ) -> NumCatRandomVariable:
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
        if not NumCatRandomVariableBoolOps.is_numeric(evidence_value):
            raise TypeError("evidence must be a numeric (int, float) value")
        e = {"evidence": evidence_value}
        r.update_data(e)
        return r

    @staticmethod
    def pop_evidence(r: NumCatRandomVariable) -> NumCatRandomVariable:
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
        data = r.data()
        if "evidence" in data:
            data.pop("evidence")
        r.update_data(data)
        return r

    @staticmethod
    def reduce_to_value(r: NumCatRandomVariable, val: NumericValue):
        """!
        \brief reduce outcomes of this random variable to val

        \param val reduction value. The final value to which random variable is
        reduced

        \throws TypeError if the val is not numeric we raise a type error.
        """
        if not NumCatRandomVariableBoolOps.is_numeric(val):
            raise TypeError("Reduction value must be numeric (int, float)")
        vs = frozenset([v for v in CatRandomVariableOps.values(r) if v == val])
        r._inputs = vs
        return r


class NumCatRandomVariableBoolOps:
    """!
    Basic operations outputting booleans that can be applied to categorical
    random variables
    """

    @staticmethod
    def type_check(
        r: NumCatRandomVariable, other: Any, shouldRaiseError: bool = False
    ) -> bool:
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
        if isinstance(other, NumCatRandomVariable) is False:
            if shouldRaiseError:
                raise TypeError(
                    "other arg must be of type NumCatRVariable, it is "
                    + type(other)
                )
            return False
        return True

    @staticmethod
    def has_evidence(
        r: NumCatRandomVariable, shouldRaiseError: bool = False
    ) -> bool:
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


class NumCatRandomVariableNumericOps:
    """!
    Basic operations outputting numeric values that can be applied to categorical
    random variables
    """

    @staticmethod
    def max(r: NumCatRandomVariable) -> NumericValue:
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
        mx, mxv = NumCatRandomVariableNumericOps.min_max_marginal_with_outcome(
            r, is_min=False
        )
        return mx

    @staticmethod
    def min(r: NumCatRandomVariable) -> NumericValue:
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
        mx, mxv = NumCatRandomVariableNumericOps.min_max_marginal_with_outcome(
            r, is_min=True
        )
        return mx

    @staticmethod
    def min_max_marginal_with_outcome(
        r: NumCatRandomVariable, is_min: bool
    ) -> Tuple[float, NumericValue]:
        """!
        \brief returns highest/lowest probability with its outcome

        \param is_min flag for specifying whether to return lowest or highest
        probability-outcome pair
        """
        mx = float("inf") if is_min else float("-inf")
        mxv = None
        for v in CatRandomVariableOps.values(r):
            marginal = r.marginal(v)
            cond = mx > marginal if is_min else mx < marginal
            if cond:
                mx = marginal
                mxv = v
        return mx, mxv

    @staticmethod
    def max_marginal_value(r: NumCatRandomVariable) -> NumericValue:
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
        mx, mxv = NumCatRandomVariableNumericOps.min_max_marginal_with_outcome(
            r, is_min=False
        )
        return mxv

    @staticmethod
    def min_marginal_value(r: NumCatRandomVariable) -> NumericValue:
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
        mx, mxv = NumCatRandomVariableNumericOps.min_max_marginal_with_outcome(
            r, is_min=True
        )
        return mxv

    @staticmethod
    def marginal_over(
        r: NumCatRandomVariable,
        evidence_value: NumericValue,
        other: AbstractRandomVariable,
    ) -> NumericValue:
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
        NumCatRandomVariableBoolOps.type_check(other, shouldRaiseError=True)
        marginal = r.marginal(evidence_value)
        return CatRandomVariableOps.p_x_fn(other, phi=lambda x: x * marginal)

    def marginal_over_evidence_key(
        r: NumCatRandomVariable, other: AbstractRandomVariable
    ) -> NumericValue:
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
        NumCatRandomVariableBoolOps.has_evidence(r, shouldRaiseError=True)
        data = r.data()
        evidence_value = data["evidence"]
        return NumCatRandomVariableNumericOps.marginal_over(
            r, evidence_value, other
        )

    def expected_value(r: NumCatRandomVariable) -> NumericValue:
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
        return sum(
            [value * r.p(value) for value in CatRandomVariableOps.values(r)]
        )

    def P_X_e(r: NumCatRandomVariable) -> NumericValue:
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
        if "evidence" in r.data():
            return r.marginal(r.data()["evidence"])
        return NumCatRandomVariableNumericOps.expected_value(r)

    def max_marginal_e(r: NumCatRandomVariable) -> NumericValue:
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
        if "evidence" in r.data():
            return r.marginal(r.data()["evidence"])
        return NumCatRandomVariableNumericOps.max(r)

    def min_marginal_e(r: NumCatRandomVariable) -> NumericValue:
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
        if "evidence" in r.data():
            return r.marginal(r.data()["evidence"])
        return NumCatRandomVariableNumericOps.min(r)
