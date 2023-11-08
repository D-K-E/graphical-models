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
        self.object_id = oid
        is_optional_type(odata, "odata", dict, True)
        self.object_data = odata if odata is not None else {}

    def data(self):
        """!"""
        return self.object_data

    def id(self):
        """!"""
        return self.object_id

    def copy(self):
        return deepcopy(self)

    def clear_data(self):
        """!"""
        self.object_data.clear()

    def update_data(self, ndata: dict):
        """!"""
        is_type(ndata, "ndata", dict, True)
        self.object_data.update(ndata)
