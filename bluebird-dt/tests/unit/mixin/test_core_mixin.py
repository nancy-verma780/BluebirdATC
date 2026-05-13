from __future__ import annotations

from bluebird_dt.mixin import Comparison


class DummyData(Comparison):
    def __init__(self, payload: dict):
        self._payload = payload
        # Comparison checks for a "data" attribute in vars(self)
        self.data = lambda: self._payload

    def data(self) -> dict:
        return self._payload


class DummyNoData(Comparison):
    def __init__(self, value: int):
        self.value = value


def test_eq_with_nested_data():
    """
    Test that mixin __eq__ works as expected
    """
    a = DummyData({"a": [1.0, 2.0], "b": {"c": 3.0}})
    b = DummyData({"a": [1.0, 2.0], "b": {"c": 3.0 + 1e-9}})
    c = DummyData({"a": [1.0, "2.0"], "b": {"c": 3.0}})

    assert a == b
    assert a != c


def test_hash_comparison():
    """
    Test that mixin hash comparison works.
    """
    a = DummyData({"x": 1.0, "y": "z"})
    b = DummyData({"x": 1.0, "y": "z"})
    assert hash(a) == hash(b)


def test_comparison_operators():
    """
    Test that core mixin's comparison operators work.
    """
    a = DummyNoData(1)
    b = DummyNoData(2)

    assert a != b
    assert a < b
    assert b > a
