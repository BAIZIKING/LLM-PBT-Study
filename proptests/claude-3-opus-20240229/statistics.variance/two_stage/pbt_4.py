from hypothesis import given, strategies as st
import statistics
from math import isclose

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_non_negative(data):
    assert statistics.variance(data) >= 0

@given(st.floats(allow_nan=False, allow_infinity=False), st.integers(min_value=2, max_value=1000))
def test_variance_identical_values(value, size):
    data = [value] * size
    assert isclose(statistics.variance(data), 0, rel_tol=1e-9, abs_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.floats(allow_nan=False, allow_infinity=False))
def test_variance_multiplication_property(data, factor):
    multiplied_data = [x * factor for x in data]
    assert isclose(statistics.variance(multiplied_data), statistics.variance(data) * factor ** 2, rel_tol=1e-9, abs_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.floats(allow_nan=False, allow_infinity=False))
def test_variance_addition_property(data, constant):
    shifted_data = [x + constant for x in data]
    assert isclose(statistics.variance(shifted_data), statistics.variance(data), rel_tol=1e-9, abs_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_order_invariant(data):
    assert isclose(statistics.variance(data), statistics.variance(list(reversed(data))), rel_tol=1e-9, abs_tol=1e-9)
# End program