"""
\brief tests related domain.py
"""
import unittest
from pygmodels.value.valuetype.domain import DomainValue
from pygmodels.value.valuetype.domain import Domain
from pygmodels.value.valuetype.domain import DomainSample
from pygmodels.value.valuetype.domain import Sample
from pygmodels.value.valuetype.domain import OrderedDomain
from pygmodels.value.valuetype.domain import FiniteDomain
from pygmodels.value.valuetype.domain import OrderedFiniteDomain
from pygmodels.value.valuetype.value import StringValue
from pygmodels.value.valuetype.value import SetValue
from pygmodels.utils import is_all_type


class DomainTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        self.v1 = DomainValue(v=StringValue(v="foo"), set_id="bar")
        self.v2 = Domain(
            name="v2", iterable=set([DomainValue(v=StringValue(v="foo"), set_id="bar")])
        )
        self.v3 = DomainSample(name="v3", iterable={v for v in self.v2})
        self.v4 = Sample(name="v4", iterable={v for v in self.v2})
        self.v5 = OrderedDomain(
            name="v5", iterable=[DomainValue(v=StringValue(v="foo"), set_id="bar")]
        )
        self.v6 = FiniteDomain(
            name="v6",
            iterable=frozenset([DomainValue(v=StringValue(v="foo"), set_id="bar")]),
        )
        self.v7 = OrderedFiniteDomain(
            name="v7",
            iterable=tuple([DomainValue(v=StringValue(v="foo"), set_id="bar")]),
        )

    def test_domain_value(self):
        """"""
        self.assertTrue(isinstance(self.v1, SetValue))

    def test_domain(self):
        """"""
        self.assertTrue(isinstance(self.v2, Domain))

    def test_domain_sample(self):
        """"""
        self.assertTrue(isinstance(self.v3, DomainSample))

    def test_sample(self):
        """"""
        self.assertTrue(isinstance(self.v4, Sample))

    def test_ordered_domain(self):
        """"""
        self.assertTrue(isinstance(self.v5, OrderedDomain))

    def test_finite_domain(self):
        """"""
        self.assertTrue(isinstance(self.v6, FiniteDomain))

    def test_ordered_finite_domain(self):
        """"""
        self.assertTrue(isinstance(self.v7, OrderedFiniteDomain))


if __name__ == "__main__":
    unittest.main()
