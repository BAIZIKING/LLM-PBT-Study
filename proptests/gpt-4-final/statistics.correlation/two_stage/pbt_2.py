from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.just('linear'))  # testing this with 'linear' method first
def test_correlation_output_float(x, y, method):
    assert isinstance(statistics.correlation(x, y, method=method), float)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.just('linear'))  # testing this with 'linear' method first
def test_correlation_output_between_neg1_pos1(x, y, method):
    assert -1 <= statistics.correlation(x, y, method=method) <= 1

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.just('linear'))  # testing this with 'linear' method first
def test_correlation_output_order_invariant(x, y, method):
    assert statistics.correlation(x, y, method=method) == statistics.correlation(y, x, method=method)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.just('linear'))  # testing this with 'linear' method first
def test_correlation_output_same_lists(x, method):
    assert statistics.correlation(x, x, method=method) == 1

@given(st.lists(st.integers(1, 10), min_size=2),
       st.just('ranked'))  # testing this with 'ranked' method now
def test_correlation_output_tie_handling(x, method):
    y = x.copy()
    y.reverse()
    assert statistics.correlation(x, y, method=method) == statistics.correlation(y, x, method=method)

# End program