"""
object contained in a graph
"""
from copy import deepcopy

from pygmodels.graph.graphtype.abstractobj import AbstractGraphObj
from pygmodels.utils import is_type, is_optional_type
from typing import Optional


class GraphObject(AbstractGraphObj):
    """!object contained in a graph"""

    def __init__(self, oid: str, odata: Optional[dict] = None):
        """!"""
        is_type(oid, "oid", str, True)
        self._id = oid
        is_optional_type(odata, "odata", dict, True)
        self._data = odata

    @property
    def data(self):
        """!"""
        if self._data is None:
            raise ValueError("data is none")
        return self._data

    @property
    def id(self):
        """!"""
        return self._id

    def copy(self):
        return deepcopy(self)

    def clear_data(self):
        """!"""
        self._data.clear()

    def update_data(self, ndata: dict):
        """!"""
        is_type(ndata, "ndata", dict, True)
        if self._data is None:
            self._data = ndata
        else:
            self._data.update(ndata)
