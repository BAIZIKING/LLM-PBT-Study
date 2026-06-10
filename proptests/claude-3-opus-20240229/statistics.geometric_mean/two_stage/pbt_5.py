from hypothesis import given, strategies as st
import statistics
from math import isclose

@given(st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1))
def test_geometric_mean_greater_than_min(data):
    result = statistics.geometric_mean(data)
    assert result >= min(data)

@given(st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1))
def test_geometric_mean_less_than_max(data):
    result = statistics.geometric_mean(data)
    assert result <= max(data)

@given(st.floats(min_value=1e-100, max_value=1e100), st.integers(min_value=1, max_value=100))
def test_geometric_mean_equal_for_same_values(value, size):
    data = [value] * size
    result = statistics.geometric_mean(data)
    assert isclose(result, value)

@given(st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1), st.floats(min_value=1e-100, max_value=1e100))
def test_geometric_mean_multiplication_property(data, factor):
    result1 = statistics.geometric_mean(data)
    result2 = statistics.geometric_mean([x * factor for x in data])
    assert isclose(result2, result1 * factor)

@given(st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1), st.floats(min_value=-100, max_value=100))
def test_geometric_mean_power_property(data, power):
    result1 = statistics.geometric_mean(data)
    result2 = statistics.geometric_mean([x ** power for x in data])
    assert isclose(result2, result1 ** power)
# End program