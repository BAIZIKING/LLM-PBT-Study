from hypothesis import given, strategies as st
import statistics
import math

@given(st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1))
def test_geometric_mean_less_than_max(data):
    assert statistics.geometric_mean(data) <= max(data)

@given(st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1))
def test_geometric_mean_greater_than_min(data):
    assert statistics.geometric_mean(data) >= min(data)

@given(st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1))
def test_geometric_mean_product_property(data):
    assert math.isclose(statistics.geometric_mean(data) ** len(data), math.prod(data))

@given(st.floats(min_value=1e-100, max_value=1e100))
def test_geometric_mean_constant_dataset(c):
    data = [c] * 10
    assert math.isclose(statistics.geometric_mean(data), c)

@given(st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1), st.floats(min_value=1e-100, max_value=1e100))
def test_geometric_mean_multiplication_property(data, k):
    scaled_data = [x * k for x in data]
    assert math.isclose(statistics.geometric_mean(scaled_data), statistics.geometric_mean(data) * k)
# End program