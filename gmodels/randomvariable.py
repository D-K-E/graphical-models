"""!
Implementation of a random variable
"""

from gmodels.gtypes.node import Node
from typing import Callable, Set, Any, List
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


class CatRandomVariable(RandomVariable):
    """!
    a discrete random variable
    """

    def __init__(
        self,
        node_id: str,
        input_data: List[Outcome],
        f: Callable[[Outcome], Value],
        distribution: Callable[[Value], float],
    ):
        ""
        data = {(i, v): f(v) for i, v in enumerate(input_data)}
        super().__init__(node_id=node_id, data=data, f=f)
        psum = sum(list(map(distribution, data.values())))
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
        input_data: Set[Outcome],
        f: Callable[[Outcome], float],
        distribution: Callable[[float], float],
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

    def evidence_key_check(self, evidence_key: str):
        """!
        check if given evidence key is associated with this random variable
        """
        data = self.data()
        if evidence_key not in data:
            msg = "Evidence key " + evidence_key + " could not be found with in"
            msg += " attributed data of this random variable"
            raise ValueError(msg)
        return True

    def marginal_over(self, evidence_value: float, other) -> float:
        """!
        Compute marginal distribution over other random variable given
        evidence with respect to current random variable.
        from Biagini and Campanino 2016, p. 35

        \f \sum_{j=1}^n p(x_i) p(y_j) \f
        """
        self.type_check(other)
        marginal = self.marginal(evidence_value)
        return other.p_x_fn(phi=lambda x: x * marginal)

    def marginal_over_evidence_key(self, evidence_key: str, other):
        """!
        Compute marginal using evidence key.
        This means that the evidence is encoded to data associated to
        random variable
        """
        self.evidence_key_check(evidence_key)
        data = self.data()
        evidence_value = data[evidence_key]
        return self.marginal_over(evidence_value, other)

    def expected_value(self) -> float:
        """!
        Expected value of random variable
        from Koller, Friedman 2009, p. 31

        \f \sum_{i=1}^n x_i p(x_i) \f
        """
        return sum([value * self.p_x(value) for value in self.data().values()])

    def P_X(self):
        """!
        Biagini, Campanino, 2016, p.11
        """
        return self.expected_value()

    def p_x_fn(self, phi: Callable[[float], float]):
        """!
        probability of a function applied to random variable
        from Biagini, Campanino, 2016, p. 11
        implements:
        \f \sum_{i=1}^n \phi(x_i) p(x_i) \f
        """
        return sum([phi(value) * self.p_x(value) for value in self.data().values()])

    def variance(self):
        """!
        Koller, Friedman 2009, p. 33
        """
        E_X2 = self.p_x_fn(phi=lambda x: x * x)
        return E_X2 - (self.expected_value * self.expected_value)

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
            node_id=str(uuid4()),
            f=phi,
            input_data=set([i for i in self.data().keys()]),
            distribution=self.dist,
        )

    def joint(self, v):
        """!
        """
        self.type_check(v)
        return self.P_X() * v.P_X()

    def joint_over(self, evidence_value: float, other, other_evidence_value: float):
        """!
        Joint distribution of two random variables
        from Biagini and Campanino 2016 p. 35
        """
        self.type_check(other)
        return self.p_x(evidence_value) * other.p_x(other_evidence_value)

    def joint_over_evidence_key(
        self, evidence_key: str, other, other_evidence_key: str
    ):
        """!
        Joint distribution of two random variables using attached evidence
        from Biagini and Campanino 2016 p. 35
        """
        self.type_check(other)
        self.evidence_key_check(evidence_key)
        other.evidence_key_check(other_evidence_key)
        data = self.data()
        other_data = other.data()
        return self.joint_over(
            evidence_value=data[evidence_key],
            other=other,
            other_evidence_value=other_data[other_evidence_key],
        )
