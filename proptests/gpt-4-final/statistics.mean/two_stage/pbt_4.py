from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_output_type(lst):
    mean = statistics.mean(lst)
    assert isinstance(mean, (float, int))

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=5, max_size=5))
def test_mean_same_numbers(lst):
    mean = statistics.mean(lst)
    assert mean == lst[0]

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_within_range(lst):
    mean = statistics.mean(lst)
    assert min(lst) <= mean <= max(lst)

@given(st.lists(st.integers()), st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10))
def test_mean_distribution(lst, n, m):
    x = 5
    y = 10
    lst = lst + [x]*n + [y]*m
    mean = statistics.mean(lst)
    if n > m:
        assert mean > x
    else:
        assert mean < y