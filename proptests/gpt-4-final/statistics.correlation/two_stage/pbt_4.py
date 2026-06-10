from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=2), st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=2))
def test_correlation_output_range(l1, l2):
    result = statistics.correlation(l1, l2)
    assert -1 <= result <= 1

@given(st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=2))
def test_correlation_same_input(l):
    result = statistics.correlation(l, l)
    assert result == 1

@given(st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=2))
def test_correlation_reverse_input(l1):
    l2 = l1[::-1]
    result = statistics.correlation(l1, l2)
    assert result == -1

@given(st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=2), st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=2))
def test_correlation_no_correlation(l1, l2):
    result = statistics.correlation(l1, l2)
    assert abs(result) < 0.05

@given(st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=2))
def test_rank_correlation(l):
    list1 = sorted(l)
    list2 = sorted(l, reverse=True)
    result1 = statistics.correlation(list1, list2, method='ranked')
    result2 = statistics.correlation(list2, list1, method='ranked')
    assert result1 == 1 and result2 == -1