"""!
\file abstractvalue.py Value of a set
"""

from abc import ABC, abstractmethod
from typing import Any


class AbstractSetValue:
    @abstractmethod
    def belongs_to(self) -> str:
        "The name of the set that contains the value"
        raise NotImplementedError

    @abstractmethod
    def value(self) -> Any:
        "Returns the value associated with the set value"
        raise NotImplementedError
