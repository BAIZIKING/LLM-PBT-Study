from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.sampled_from(['linear', 'ranked']))
def test_correlation_range(x, method):
    y = x[:]
    assert -1 <= statistics.correlation(x, y, method=method) <= 1

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.sampled_from(['linear', 'ranked']))
def test_identical_inputs(x, method):
    y = x[:]
    assert statistics.correlation(x, y, method=method) == 1

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.sampled_from(['linear', 'ranked']))
def test_different_lengths(x, method):
    y = x[:-1]
    try:
        statistics.correlation(x, y, method=method)
    except StatisticsError: 
        assert True

@given(st.lists(st.integers(min_value=1, max_value=10), min_size=2), st.sampled_from(['linear', 'ranked']))
def test_perfect_positive_correlation(x, method):
    y = [v * 2 for v in x]
    assert statistics.correlation(x, y, method=method) == 1

@given(st.lists(st.integers(min_value=1, max_value=10), min_size=2), st.sampled_from(['linear', 'ranked']))
def test_correlation_methods(x, method):
    y = list(range(1, len(x) + 1))  # ranks
    correlation = statistics.correlation(x, y, method=method)
    if method == 'linear':
        assert correlation != 1
    else:
        assert correlation == 1