from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_returns_numeric(result):
    assert isinstance(statistics.mean(result), float)

@given(st.lists(st.integers(), min_size=1))
def test_mean_of_constant(result):
    constant = result[0]
    assert statistics.mean(result) == constant

@given(st.lists(st.integers(), min_size=1))
def test_mean_of_zero_sum(result):
    if sum(result)==0:
       assert statistics.mean(result) == 0.0

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=1))
def test_mean_single_element(result):
    assert statistics.mean(result) == result[0]

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_same_reverse(result):
    assert statistics.mean(result) == statistics.mean(result[::-1])