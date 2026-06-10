from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_within_bounds(data):
    assert min(data) <= statistics.mean(data) <= max(data)

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_mean_equals_element(x):
    assert statistics.mean([x] * 10) == x

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.floats(allow_nan=False, allow_infinity=False))
def test_mean_addition(data, c):
    assert statistics.mean([x + c for x in data]) == statistics.mean(data) + c

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.floats(allow_nan=False, allow_infinity=False))
def test_mean_multiplication(data, c):
    assert statistics.mean([x * c for x in data]) == statistics.mean(data) * c

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_concatenation(data1, data2):
    combined_data = data1 + data2
    mean1, mean2 = statistics.mean(data1), statistics.mean(data2)
    len1, len2 = len(data1), len(data2)
    expected_mean = (mean1 * len1 + mean2 * len2) / (len1 + len2)
    assert statistics.mean(combined_data) == expected_mean
# End program