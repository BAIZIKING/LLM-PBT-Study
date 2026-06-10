from hypothesis import given, strategies as st
import statistics
import math

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_correlation_output_range(x, y):
    result = statistics.correlation(x, y)
    assert -1 <= result <= 1

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_correlation_input_order(x, y):
    result1 = statistics.correlation(x, y)
    result2 = statistics.correlation(y, x)
    assert math.isclose(result1, result2)

@given(st.floats(allow_nan=False, allow_infinity=False), st.floats(allow_nan=False, allow_infinity=False), st.floats(min_value=0), st.integers(min_value=2, max_value=100))
def test_correlation_perfectly_positive(a, b, c, n):
    x = st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=n, max_size=n).example()
    y = [a * xi + b for xi in x]
    result = statistics.correlation(x, y)
    assert math.isclose(result, 1.0)

@given(st.floats(allow_nan=False, allow_infinity=False), st.floats(allow_nan=False, allow_infinity=False), st.floats(max_value=0), st.integers(min_value=2, max_value=100))
def test_correlation_perfectly_negative(a, b, c, n):
    x = st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=n, max_size=n).example()
    y = [a * xi + b for xi in x]
    result = statistics.correlation(x, y)
    assert math.isclose(result, -1.0)

@given(st.floats(allow_nan=False, allow_infinity=False), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_correlation_constant_input(c, y):
    x = [c] * len(y)
    try:
        statistics.correlation(x, y)
        assert False
    except statistics.StatisticsError:
        assert True
# End program