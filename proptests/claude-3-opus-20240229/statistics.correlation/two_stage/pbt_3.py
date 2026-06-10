from hypothesis import given, strategies as st
import statistics
import math

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_correlation_range(x):
    y = x[::]  # Create a copy of x
    assert -1 <= statistics.correlation(x, y) <= 1

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_correlation_monotonically_increasing(x):
    y = sorted(x)
    assert math.isclose(statistics.correlation(x, y), 1, rel_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_correlation_monotonically_decreasing(x):
    y = sorted(x, reverse=True)
    assert math.isclose(statistics.correlation(x, y), -1, rel_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_correlation_order_invariant(x):
    y = x[::]  # Create a copy of x
    assert math.isclose(statistics.correlation(x, y), statistics.correlation(y, x), rel_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.floats(allow_nan=False, allow_infinity=False))
def test_correlation_scale_invariant(x, scale):
    assume(scale != 0)
    y = [i * scale for i in x]
    assert math.isclose(statistics.correlation(x, y), statistics.correlation(x, x), rel_tol=1e-9)
# End program