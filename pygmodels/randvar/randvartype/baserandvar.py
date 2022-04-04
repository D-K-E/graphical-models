"""!
\file baserandvar.py Base Random Variable object that implements the abstract
random variable interface. Inheriting from this object would make your object
usable for all the operations defined in \see baserandvarops.py.
"""

from typing import Callable, Optional, Set

from pygmodels.graph.graphtype.graphobj import GraphObject
from pygmodels.randvar.randvartype.abstractrandvar import (
    AbstractRandomVariable,
    AssociatedValueSet,
    PossibleOutcome,
    PossibleOutcomes,
)
from pygmodels.value.codomain import CodomainValue
from pygmodels.value.value import NumericValue


class BaseRandomVariable(AbstractRandomVariable, GraphObject):
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
        randvar_id: str,
        randvar_name: Optional[str] = None,
        data: Optional[dict] = None,
        input_data: Optional[PossibleOutcomes] = None,
        f: Callable[[PossibleOutcome], CodomainValue] = lambda x: x,
        marginal_distribution: Callable[
            [CodomainValue], float
        ] = lambda x: 1.0,
    ):
        """!
        \brief Constructor for random variable

        \param marginal_distribution a function that takes in a value from
        codomain of the random variable and outputs a value in the range [0,1].
        Notice that is not a local distribution, it should be the marginal
        distribution that is independent of local structure.

        \param data The data associated to random variable can be anything
        \param randvar_id identifier of random variable. Same identifier is used
        as node identifier in a graph.
        \param randvar_name name of random variable for easy recognition
        \param f a function who takes data or from data, and outputs anything.

        \returns a random variable instance


        \throws ValueError We raise a value error if the probability values
        associated to outcomes add up to a value bigger than one.

        For other parameters and the definition of a random variable \see
        RandomVariable.

        A simple data specification is provided for passing evidences and
        input. The possible outcomes key holds a set of values belonging to
        space of possible outcomes. If the input data just contains a key as
        'possible-outcomes', we suppose that it contains a object which
        represents the space of all possible outcomes of the measurable event
        set associated to random variable.

        The function associated to our random variable transforms the set of
        possible outcomes to values as per its definition in Koller, Friedman,
        2009, p. 20. Lastly we check whether obtained, or associated
        outcome-values satisfy the probability rule by checking if the
        probabilities associated to these values add up to one.

        \code{.py}

        >>> 
        >>> dicename = "dice"
        >>> diceid = "dice01"
        >>> dice_input_data = set(
        >>>    [DomainValue(v=i, dom_id=diceid) for i in range(1, 7)]
        >>> )
        >>> dice_f = lambda x: x
        >>> dice_distribution = lambda x: x.v / 6.0
        >>> dice = BaseRandomVariable(
        >>>    randvar_id=diceid,
        >>>    randvar_name=dicename,
        >>>    data=None,
        >>>    input_data=dice_input_data,
        >>>    f=dice_f,
        >>>    marginal_distribution=dice_distribution,
        >>> )
        >>> 

        \endcode

        constructor for a random variable"""
        super().__init__(
            oid=randvar_id, odata=data if data is not None else {}
        )
        self.name = randvar_name
        if input_data is None and data is None:
            raise ValueError("Either input data or data must not be None")
        if input_data is None and data is not None:
            if "possible-outcomes" not in data:
                msg = "if input_data is not provided, provided data"
                msg += "must contain 'possible-outcomes' key"
                raise ValueError(msg)
            else:
                possible_outcomes = data["possible-outcomes"]
        elif input_data is not None:
            possible_outcomes = input_data
        else:
            raise ValueError("Unknown data configuration")
        self._inputs = possible_outcomes
        if not callable(f):
            raise TypeError("f must be a callable")
        self.f = f
        self._outs = None
        psum = sum(list(map(marginal_distribution, possible_outcomes)))
        if psum > 1 and psum < 0:
            raise ValueError("probability sum bigger than 1 or smaller than 0")
        self.dist = marginal_distribution

    @property
    def inputs(self) -> PossibleOutcomes:
        """!"""
        return self._inputs

    def image(self, sampler: Callable) -> AssociatedValueSet:
        """!
        Image of the random variable's function
        """
        if self._outs is None:
            self._outs = sampler(
                frozenset(set(self.f(i) for i in self.inputs))
            )
        return self._outs

    def p(self, outcome: CodomainValue) -> NumericValue:
        """!
        \brief probability of given outcome value as per the associated
        distribution

        \param value a member of \f$\Omega\f$ set of possible outcomes.

        \returns probability value associated to the outcome
        """
        return self.dist(outcome)

    def __eq__(self, other: AbstractRandomVariable) -> bool:
        """!
        Checks the instance first and then the probability distribution
        """
        if not isinstance(other, AbstractRandomVariable):
            return False
        if other.inputs() != self.inputs():
            return False
        if other.image() != self.image():
            return False
        for ins in self.inputs():
            if other.p(ins) != self.p(ins):
                return False
        return True

    def __str__(self):
        """!
        String representation of a random variable
        """
        msg = "<RandomVariable :: id: "
        msg += self.id()
        msg += " name: " + (self.name if self.name is not None else "None")
        msg += ">"
        return msg

    def __hash__(self):
        """!
        \brief Obtain hash value from string representation of RandomVariable
        """
        return hash(self.__str__())
