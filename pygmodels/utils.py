"""!
Utility functions
"""

from typing import Any, Optional


def is_type(val: Any, originType: Any, shouldRaiseError=False) -> bool:
    """!
    Check if given value is of origin type
    """
    if isinstance(val, originType) is False:
        if shouldRaiseError:
            raise TypeError(
                "value"
                + " must be of type: "
                + originType.__name__
                + " but it is "
                + type(val).__name__
            )
        return False
    return True


def is_other_type(
    val: Any,
    other: Any,
    shouldRaiseError: bool,
    originType: Optional[Any] = None,
) -> bool:
    """"""
    comp_type = type(val) if originType is None else originType
    if isinstance(other, comp_type) is False:
        if shouldRaiseError:
            raise TypeError(
                "other arg must be of type "
                + type(val).__name__
                + ", it is "
                + type(other).__name__
            )
        return False
    return True


def type_check(
    val: Any,
    other: Optional[Any] = None,
    shouldRaiseError=False,
    originType: Optional[Any] = None,
) -> bool:
    """!"""
    if originType is not None:
        if (
            is_type(val, originType, shouldRaiseError=shouldRaiseError)
            is False
        ):
            return False
    other_check = is_other_type(
        val=val,
        other=other,
        originType=originType,
        shouldRaiseError=shouldRaiseError,
    )
    if other_check is False:
        return False
    return True
