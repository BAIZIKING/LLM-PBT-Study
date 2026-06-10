from hypothesis import given, strategies as st
import statistics
from math import prod

@given(st.lists(st.floats(min_value=0, max_value=1e100), min_size=1))
def test_geometric_mean_less_than_max(data):
    assert statistics.geometric_mean(data) <= max(data)

@given(st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1))
def test_geometric_mean_greater_than_min(data):
    assert statistics.geometric_mean(data) >= min(data)

@given(st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1))
def test_geometric_mean_times_length_less_than_product(data):
    assert statistics.geometric_mean(data) * len(data) <= prod(data)

@given(st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1))
def test_geometric_mean_invariant_under_permutation(data):
    permuted_data = data[::-1]
    assert statistics.geometric_mean(data) == statistics.geometric_mean(permuted_data)

@given(st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1), st.floats(min_value=1e-100, max_value=1e100))
def test_geometric_mean_multiplication_property(data, constant):
    scaled_data = [x * constant for x in data]
    assert statistics.geometric_mean(scaled_data) == statistics.geometric_mean(data) * constant
# End program