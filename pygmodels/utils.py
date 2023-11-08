"""!
Utility functions
"""

from typing import Any, Optional


def is_type(field_value, field_name: str, field_type, raise_error: bool = True) -> bool:
    "check type of field value"
    if not isinstance(field_name, str):
        raise TypeError(
            "field_name {0} must be a string but it has type {1}".format(
                str(field_name), str(type(field_name))
            )
        )
    if not isinstance(field_value, field_type):
        if raise_error:
            raise TypeError(
                "field_value {0} must be a {1} but it has type {2}".format(
                    str(field_value), str(field_type), str(type(field_value))
                )
            )
        return False
    return True


def is_optional_type(
    field_value, field_name: str, field_type, raise_error: bool = True
) -> bool:
    "check type of field value"
    if field_value is None:
        return True
    else:
        return is_type(field_value, field_name, field_type, raise_error)


def is_all_type(field_value, field_name: str, field_type, raise_error: bool = True):
    """"""
    if not is_type(
        field_value, field_name, (list, set, frozenset, tuple), raise_error=raise_error
    ):
        return False
    is_all = all(
        is_type(i, "member", field_type, raise_error=raise_error) for i in field_value
    )
    return is_all


def is_optional_all_type(
    field_value, field_name: str, field_type, raise_error: bool = True
):
    """"""
    if field_value is None:
        return True
    else:
        return is_all_type(field_value, field_name, field_type, raise_error)


def is_dict_type(
    field_value, field_name: str, key_type, value_type, raise_error: bool = True
):
    """"""
    if not is_type(field_value, field_name, dict, raise_error=raise_error):
        return False
    keys = list(field_value.keys())
    values = list(field_value.values())
    is_keys = is_all_type(keys, "keys", key_type, raise_error)
    is_values = is_all_type(values, "values", value_type, raise_error)

    return is_keys and is_values


def is_optional_dict_type(
    field_value, field_name: str, key_type, value_type, raise_error: bool = True
):
    """"""
    if field_value is None:
        return True
    else:
        return is_dict_type(field_value, field_name, key_type, value_type, raise_error)


def read_json(path: str):
    """"""
    if not Path(path).exists():
        raise ValueError(f"Path {path} does not exists")
    with open(path, "r", encoding="utf-8", newline="\n") as f:
        jfile = json.load(f)
    return jfile
