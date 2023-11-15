"""
expectation of a random number as described by Biagini, Campanino, 2016, p. 8
"""

from pygmodels.randvar.randvartype.baserandvar2 import BaseRandomNumber
from pygmodels.graph.graphtype.graphobj import GraphObject
from pygmodels.utils import is_type, is_optional_type
from typing import Optional
from abc import abstractmethod


class Expectation(GraphObject):
    """"""

    def __init__(
        self,
        expectation_id: str,
        randvar: Optional[BaseRandomNumber] = None,
        data: Optional[dict] = None,
    ):
        """"""
        super().__init__(oid=expectation_id, data=data)
        is_optional_type(randvar, "randvar", BaseRandomNumber, True)
        self._randvar = randvar
        if randvar is not None:
            if not randvar.is_bounded():
                raise ValueError(
                    "Expectation of unbounded random numbers are not supported"
                )

    @property
    def randvar(self):
        if self._randvar is None:
            raise ValueError("randvar is none")
        return self._randvar

    @abstractmethod
    def __call__(self) -> float:
        """"""
        raise NotImplementedError
