"""
\brief tests related codomain.py
"""
import unittest
from pygmodels.value.valuetype.codomain import CodomainValue
from pygmodels.value.valuetype.codomain import Codomain
from pygmodels.value.valuetype.codomain import Range
from pygmodels.value.valuetype.codomain import RangeSubset
from pygmodels.value.valuetype.codomain import OrderedCodomain
from pygmodels.value.valuetype.codomain import FiniteCodomain
from pygmodels.value.valuetype.codomain import OrderedFiniteCodomain
from pygmodels.value.valuetype.value import StringValue
from pygmodels.value.valuetype.value import SetValue
from pygmodels.utils import is_all_type


class CodomainTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        self.v1 = CodomainValue(
            v=StringValue(v="foo"), set_id="bar", mapping_name="baz", domain_name="ban"
        )
        self.v2 = Codomain(
            name="v2",
            iterable=set(
                [
                    CodomainValue(
                        v=StringValue(v="foo"), set_id="bar", mapping_name="baz"
                    )
                ]
            ),
        )
        self.v3 = Range(name="v3", iterable={v for v in self.v2})
        self.v4 = RangeSubset(name="v4", iterable={v for v in self.v2})
        self.v5 = OrderedCodomain(
            name="v5",
            iterable=[
                CodomainValue(v=StringValue(v="foo"), set_id="bar", mapping_name="baz")
            ],
        )
        self.v6 = FiniteCodomain(
            name="v6",
            iterable=frozenset(
                [
                    CodomainValue(
                        v=StringValue(v="foo"), set_id="bar", mapping_name="baz"
                    )
                ]
            ),
        )
        self.v7 = OrderedFiniteCodomain(
            name="v7",
            iterable=tuple(
                [
                    CodomainValue(
                        v=StringValue(v="foo"), set_id="bar", mapping_name="baz"
                    )
                ]
            ),
        )

    def test_codomain_value(self):
        """"""
        self.assertTrue(isinstance(self.v1, SetValue))

    def test_codomain(self):
        """"""
        self.assertTrue(isinstance(self.v2, Codomain))

    def test_range(self):
        """"""
        self.assertTrue(isinstance(self.v3, Range))

    def test_range_subset(self):
        """"""
        self.assertTrue(isinstance(self.v4, RangeSubset))

    def test_ordered_codomain(self):
        """"""
        self.assertTrue(isinstance(self.v5, OrderedCodomain))

    def test_finite_codomain(self):
        """"""
        self.assertTrue(isinstance(self.v6, FiniteCodomain))

    def test_ordered_finite_codomain(self):
        """"""
        self.assertTrue(isinstance(self.v7, OrderedFiniteCodomain))


if __name__ == "__main__":
    unittest.main()
