from hypothesis import given, strategies as st
import statistics
from math import isclose

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_non_negative(data):
    assert statistics.variance(data) >= 0

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_equal_elements(data):
    equal_data = [data[0]] * len(data)
    assert isclose(statistics.variance(equal_data), 0, rel_tol=1e-9, abs_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.floats(allow_nan=False, allow_infinity=False))
def test_variance_multiplication_property(data, k):
    scaled_data = [x * k for x in data]
    assert isclose(statistics.variance(scaled_data), statistics.variance(data) * k ** 2, rel_tol=1e-9, abs_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.floats(allow_nan=False, allow_infinity=False))
def test_variance_addition_property(data, c):
    shifted_data = [x + c for x in data]
    assert isclose(statistics.variance(shifted_data), statistics.variance(data), rel_tol=1e-9, abs_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_xbar_property(data):
    xbar = statistics.mean(data)
    assert isclose(statistics.variance(data, xbar), statistics.variance(data), rel_tol=1e-9, abs_tol=1e-9)
# End program