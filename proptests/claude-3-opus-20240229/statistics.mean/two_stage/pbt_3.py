from hypothesis import given, strategies as st
import statistics
from math import isclose

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_within_range(data):
    assert min(data) <= statistics.mean(data) <= max(data)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_equals_value_for_equal_elements(data):
    equal_data = [data[0]] * len(data)
    assert statistics.mean(equal_data) == data[0]

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_doubles_when_data_doubles(data):
    doubled_data = [x * 2 for x in data]
    assert isclose(statistics.mean(doubled_data), statistics.mean(data) * 2)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_equals_sum_divided_by_length(data):
    assert isclose(statistics.mean(data), sum(data) / len(data))

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.floats(allow_nan=False, allow_infinity=False))
def test_mean_increases_by_constant_when_added(data, constant):
    increased_data = [x + constant for x in data]
    assert isclose(statistics.mean(increased_data), statistics.mean(data) + constant)
# End program