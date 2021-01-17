"""!
Implementation of a random variable
"""

from gmodels.gtypes.node import Node
from typing import Callable, Set, Any, List, Dict
import math
from uuid import uuid4


class RandomVariable(Node):
    def __init__(
        self, node_id: str, data: Any, f: Callable[[Any], Any] = lambda x: x,
    ):
        ""
        super().__init__(node_id=node_id, data=data)

    def p_x(self, value: Any):
        raise NotImplementedError


Outcome = Any
Value = Any
NumericValue = float


class CatRandomVariable(RandomVariable):
    """!
    a discrete random variable
    """

    def __init__(
        self,
        node_id: str,
        input_data: Dict[str, Outcome],
        f: Callable[[Outcome], Value] = lambda x: x,
        distribution: Callable[[Value], float] = lambda x: 1.0,
    ):
        ""
        data = {}
        data.update(input_data)
        if "outcomes" in input_data:
            data["outcome-values"] = {
                (i, v): f(v) for i, v in enumerate(input_data["outcomes"])
            }
        super().__init__(node_id=node_id, data=data, f=f)
        if "outcome-values" in data:
            psum = sum(list(map(distribution, data["outcome-values"])))
            if psum > 1 and psum < 0:
                raise ValueError("probability sum bigger than 1 or smaller than 0")
        self.dist = distribution

    def p_x(self, value: Any) -> float:
        return self.dist(value)

    def marginal(self, value: float) -> float:
        """!
        marginal distribution
        from Biagini, Campanino, 2016, p. 35
        """
        return self.p_x(value)


class NumCatRVariable(CatRandomVariable):
    """!
    Numerical categorical random variable object
    """

    def __init__(
        self,
        node_id: str,
        input_data: Dict[str, Outcome],
        f: Callable[[Outcome], NumericValue] = lambda x: x,
        distribution: Callable[[NumericValue], float] = lambda x: 1.0,
    ):
        ""
        super().__init__(
            node_id=node_id, input_data=input_data, f=f, distribution=distribution
        )

    @staticmethod
    def type_check(other):
        """!
        """
        if isinstance(other, NumCatRVariable) is False:
            raise TypeError(
                "other arg must be of type NumCatRVariable, it is " + type(other)
            )
        return True

    def evidence_key_check(self):
        """!
        check if given evidence key is associated with this random variable
        """
        data = self.data()
        if "evidence" not in data:
            msg = "Evidence " + " could not be found with in"
            msg += " attributed data of this random variable"
            raise ValueError(msg)
        return True

    def max(self):
        values = self.data()["outcome-values"]
        return max([self.marginal(v) for v in values])

    def min(self):
        values = self.data()["outcome-values"]
        return min([self.marginal(v) for v in values])

    def marginal_over(self, evidence_value: float, other) -> float:
        """!
        Compute marginal distribution over other random variable given
        evidence with respect to current random variable.
        from Biagini and Campanino 2016, p. 35

        \f \sum_{j=1}^n p(x_i) p(y_j) = p(x_i) \sum_{j=1}^n p(y_j) \f
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
        self.evidence_key_check()
        data = self.data()
        evidence_value = data["evidence"]
        return self.marginal_over(evidence_value, other)

    def expected_value(self) -> float:
        """!
        Expected value of random variable
        from Koller, Friedman 2009, p. 31

        \f \sum_{i=1}^n x_i p(x_i) \f
        """
        values = self.data()["outcome-values"]
        return sum([value * self.p_x(value) for value in values])

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

    def p_x_fn(self, phi: Callable[[float], float]):
        """!
        probability of a function applied to random variable
        from Biagini, Campanino, 2016, p. 11
        implements:
        \f \sum_{i=1}^n \phi(x_i) p(x_i) \f
        """
        values = self.data()["outcome-values"]
        return sum([phi(value) * self.p_x(value) for value in values])

    def apply(self, phi: Callable[[NumericValue], NumericValue]):
        """!
        """
        values = self.data()["outcome-values"]
        return [phi(v) for v in values]

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

    def conditional(self, other):
        """!
        Conditional probability distribution (Bayes rule)
        from Koller and Friedman
        """
        self.type_check(other)
        return self.joint(other) / other.P_X_e()
