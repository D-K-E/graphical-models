"""!
Implementation of a random variable
"""

from gmodels.gtypes.node import Node
from typing import Callable, Set, Any, List, Dict, FrozenSet, Tuple
import math
from uuid import uuid4
from random import choice

Outcome = Any
Value = Any
NumericValue = float


class PossibleOutcomes:
    """!
    \brief set of possible outcomes from Koller, Friedman 2009, p. 15, 20

    This is simply a frozenset. We assume that possible outcomes contained in
    this object are measurable.
    """

    def __init__(self, omega: FrozenSet[Outcome]):
        self.data = omega


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
        self, node_id: str, data: Any, f: Callable[[Outcome], Value] = lambda x: x,
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

    def p_x(self, value: Any):
        raise NotImplementedError


class CatRandomVariable(RandomVariable):
    """!
    a discrete random variable
    """

    def __init__(
        self,
        node_id: str,
        input_data: Dict[str, Any],
        f: Callable[[Outcome], Value] = lambda x: x,
        distribution: Callable[[Value], float] = lambda x: 1.0,
    ):
        """!
        \brief Constructor for categorical/discrete random variable

        \param distribution a function that takes in a value from codomain of
        the random variable and outputs a value in the range [0,1].

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
        >>>    distribution=grade_distribution
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
            psum = sum(list(map(distribution, data["outcome-values"])))
            if psum > 1 and psum < 0:
                raise ValueError("probability sum bigger than 1 or smaller than 0")
        self.dist = distribution

    def p_x(self, value: Value) -> float:
        """!
        \brief probability of given outcome value as per the associated
        distribution

        \param value a member of \f$\Omega\f$ set of possible outcomes.

        \returns probability value associated to the outcome
        """
        return self.dist(value)

    def marginal(self, value: Value) -> float:
        """!
        \brief marginal distribution that is the probability of an outcome

        from Biagini, Campanino, 2016, p. 35
        <blockquote>
        Marginal distribution of X is the function: \f$p_1(x_i) = P(X=x_i)\f$
        </blockquote>

        \see CatRandomVariable.p_x

        \returns probability value associated to value
        """
        return self.p_x(value)

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
        >>>    distribution=grade_distribution
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
        >>>    distribution=grade_distribution
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
    """

    def __init__(
        self,
        node_id: str,
        input_data: Dict[str, Outcome],
        f: Callable[[Outcome], NumericValue] = lambda x: x,
        distribution: Callable[[NumericValue], float] = lambda x: 1.0,
    ):
        """!
        \brief constructor for Numeric Categorical Random Variable
        
        \see CatRandomVariable for explanation of parameters.
        The numeric categorical random variable is just as it says, a numeric
        categorical random variable. The outcome values of this random variable
        is numeric, that is it can be integer or float. For facilitating
        operations we treat everything as float.

        """
        super().__init__(
            node_id=node_id, input_data=input_data, f=f, distribution=distribution
        )

    @staticmethod
    def type_check(other: Any) -> bool:
        """!
        \brief simple function for checking whether the other is also a
        NumCatRVariable

        \param other it can be anything

        \throws TypeError if the other is not a NumCatRVariable, we raise a type
        error
        """
        if isinstance(other, NumCatRVariable) is False:
            raise TypeError(
                "other arg must be of type NumCatRVariable, it is " + type(other)
            )
        return True

    def evidence_check(self) -> bool:
        """!
        \brief Check if any evidence is associated with this random variable
        """
        data = self.data()
        if "evidence" not in data:
            msg = "Evidence " + " could not be found with in"
            msg += " attributed data of this random variable"
            raise ValueError(msg)
        return True

    def max(self):
        """!
        \brief maximum marginal value
        """
        return max([self.marginal(v) for v in self.values()])

    def max_marginal_value(self):
        if "evidence" in self.data():
            return self.marginal(self.data()["evidence"])

        mx = self.max_marginal_e()
        vs = []
        for v in self.values():
            marginal = self.marginal(v)
            if marginal == mx:
                vs.append((v, marginal))
        # break ties
        v, marginal = choice(vs)
        return v

    def min(self):
        return min([self.marginal(v) for v in self.values()])

    def marginal_over(self, evidence_value: float, other) -> float:
        """!
        Compute marginal distribution over other random variable given
        evidence with respect to current random variable.
        from Biagini and Campanino 2016, p. 35

        \f$ \sum_{j=1}^n p(x_i) p(y_j) = p(x_i) \sum_{j=1}^n p(y_j) \f$
        """
        self.type_check(other)
        marginal = self.marginal(evidence_value)
        return other.p_x_fn(phi=lambda x: x * marginal)

    def marginal_over_evidence_key(self, other):
        """!
        Compute marginal using evidence key.
        This means that the evidence is encoded to data associated to
        random variable
        """
        self.evidence_check()
        data = self.data()
        evidence_value = data["evidence"]
        return self.marginal_over(evidence_value, other)

    def expected_value(self) -> float:
        """!
        Expected value of random variable
        from Koller, Friedman 2009, p. 31

        \f$ \sum_{i=1}^n x_i p(x_i) \f$
        """
        return sum([value * self.p_x(value) for value in self.values()])

    def add_evidence(self, evidence_value: float):
        """!
        """
        e = {"evidence": evidence_value}
        self.update_data(e)

    def pop_evidence(self):
        """!
        """
        data = self.data()
        if "evidence" in data:
            data.pop("evidence")
        self.update_data(data)

    def reduce_to_value(self, val: NumericValue):
        ""
        vs = [v for v in self.values() if v == val]
        vdata = self.data()
        vdata["outcome-values"] = vs
        self.update_data(vdata)

    def P_X(self):
        """!
        Biagini, Campanino, 2016, p.11
        it is also the marginal over all values
        """
        return self.expected_value()

    def P_X_e(self):
        """!
        evaluate probability with given random variable's evidence if it is
        given.
        """
        if "evidence" in self.data():
            return self.marginal(self.data()["evidence"])
        return self.expected_value()

    def max_marginal_e(self):
        """!
        evaluate max probability with given random variable's evidence if it is
        present.
        """
        if "evidence" in self.data():
            return self.marginal(self.data()["evidence"])
        return self.max()

    def p_x_fn(self, phi: Callable[[float], float]):
        """!
        probability of a function applied to random variable
        from Biagini, Campanino, 2016, p. 11
        implements:
        \f$\sum_{i=1}^n \phi(x_i) p(x_i) \f$
        """
        return sum([phi(value) * self.p_x(value) for value in self.values()])

    def apply(self, phi: Callable[[NumericValue], NumericValue]):
        """!
        """
        return [phi(v) for v in self.values()]

    def apply_to_marginals(self, phi: Callable[[float], float]) -> List[float]:
        """!
        """
        return [phi(self.marginal(v)) for v in self.values()]

    def expected_apply(self, phi: Callable[[NumericValue], NumericValue]):
        """!
        """
        return self.p_x_fn(phi)

    def variance(self):
        """!
        Koller, Friedman 2009, p. 33
        \f E[X^2] - (E[X])^2 \f
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
        make a new random variable from given function
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
        """!
        """
        self.type_check(other)
        joint = self.max_joint(other)
        return max([v for v in other.apply_to_marginals(lambda x: joint / x)])
