from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(min_value=0.0001, max_value=1000), min_size=1))
def test_geometric_mean_greater_than_min(data):
    assert statistics.geometric_mean(data) >= min(data)

@given(st.lists(st.floats(min_value=0.0001, max_value=1000), min_size=1))
def test_geometric_mean_less_than_max(data):
    assert statistics.geometric_mean(data) <= max(data)

@given(st.floats(min_value=0.0001, max_value=1000), st.integers(min_value=2, max_value=5))
def test_geometric_mean_equal_to_arithmetic_mean(value, size):
    data = [value] * size
    assert statistics.geometric_mean(data) == statistics.mean(data)

@given(st.floats(min_value=2, max_value=10), st.integers(min_value=1, max_value=5))
def test_geometric_mean_of_powers_of_base(base, power):
    data = [base**i for i in range(1, power + 1)]
    assert statistics.geometric_mean(data) == base

@given(st.lists(st.floats(min_value=0.0001, max_value=1000), min_size=1), st.floats(min_value=0.0001, max_value=10))
def test_geometric_mean_scaling(data, factor):
    scaled_data = [x * factor for x in data]
    assert statistics.geometric_mean(scaled_data) == statistics.geometric_mean(data) * factor
# End program