from hypothesis import given, strategies as st
import statistics
from math import isclose

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_non_negative(data):
    assert statistics.variance(data) >= 0

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_all_equal(data):
    assert isclose(statistics.variance([data[0]] * len(data)), 0)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.floats(allow_nan=False, allow_infinity=False))
def test_variance_multiplication(data, k):
    assert isclose(statistics.variance([x * k for x in data]), statistics.variance(data) * k**2)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.floats(allow_nan=False, allow_infinity=False))
def test_variance_addition(data, c):
    assert isclose(statistics.variance([x + c for x in data]), statistics.variance(data))

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_xbar(data):
    xbar = statistics.mean(data)
    assert isclose(statistics.variance(data, xbar=xbar), statistics.variance(data))
# End program