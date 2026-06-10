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
    scaled_data = [x * factor for x in data]
    assert isclose(statistics.variance(scaled_data), statistics.variance(data) * factor ** 2, rel_tol=1e-9, abs_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_permutation_invariant(data):
    permuted_data = list(data)
    st.shuffle(permuted_data)
    assert isclose(statistics.variance(data), statistics.variance(permuted_data), rel_tol=1e-9, abs_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_xbar_argument(data):
    xbar = statistics.mean(data)
    assert isclose(statistics.variance(data), statistics.variance(data, xbar), rel_tol=1e-9, abs_tol=1e-9)
# End program