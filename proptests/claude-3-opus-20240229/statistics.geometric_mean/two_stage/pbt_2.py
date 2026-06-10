from hypothesis import given, strategies as st
import statistics
from math import prod

@given(st.lists(st.floats(min_value=0, max_value=1e100), min_size=1))
def test_geometric_mean_less_than_max(data):
    assert statistics.geometric_mean(data) <= max(data)

@given(st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1))
def test_geometric_mean_greater_than_min(data):
    assert statistics.geometric_mean(data) >= min(data)

@given(st.floats(min_value=1e-100, max_value=1e100), st.integers(min_value=1, max_value=1000))
def test_geometric_mean_identical_values(value, size):
    data = [value] * size
    assert statistics.geometric_mean(data) == value

@given(st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1), st.floats(min_value=1e-100, max_value=1e100))
def test_geometric_mean_multiplication(data, factor):
    scaled_data = [x * factor for x in data]
    assert statistics.geometric_mean(scaled_data) == statistics.geometric_mean(data) * factor

@given(st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1), st.floats(min_value=-100, max_value=100))
def test_geometric_mean_power(data, power):
    powered_data = [x ** power for x in data]
    assert statistics.geometric_mean(powered_data) == statistics.geometric_mean(data) ** power
# End program