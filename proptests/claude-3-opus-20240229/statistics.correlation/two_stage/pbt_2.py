from hypothesis import given, strategies as st
import statistics
from math import isclose

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_correlation_range(x, y):
    assert -1 <= statistics.correlation(x, y) <= 1
    assert -1 <= statistics.correlation(x, y, method='ranked') <= 1

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_perfect_monotonic_correlation(x):
    y = sorted(x)
    assert isclose(statistics.correlation(x, y, method='ranked'), 1.0)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_perfect_positive_linear_correlation(x):
    y = [i * 2 for i in x]
    assert isclose(statistics.correlation(x, y), 1.0)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_perfect_negative_linear_correlation(x):
    y = [-i * 2 for i in x]
    assert isclose(statistics.correlation(x, y), -1.0)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=1), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_length_mismatch(x, y):
    try:
        statistics.correlation(x, y)
    except statistics.StatisticsError:
        pass
    else:
        assert False, "Expected StatisticsError"
# End program