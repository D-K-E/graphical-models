"""!
"""

from typing import Any, Callable, Dict, FrozenSet, List, Optional, Set, Tuple

DomainValue = Any


class DomainValue:
    def __init__(self, v):
        self.data = v
