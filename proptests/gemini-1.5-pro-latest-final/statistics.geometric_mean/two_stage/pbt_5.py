from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(min_value=0.0001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1))
def test_geometric_mean_less_than_arithmetic_mean(data):
    assert statistics.geometric_mean(data) <= statistics.mean(data)

@given(st.floats(min_value=0.0001, max_value=1000, allow_nan=False, allow_infinity=False))
def test_geometric_mean_equal_for_identical_values(value):
    data = [value] * 5
    assert statistics.geometric_mean(data) == value

@given(st.floats(min_value=0.0001, max_value=1000, allow_nan=False, allow_infinity=False))
def test_geometric_mean_of_single_value(value):
    assert statistics.geometric_mean([value]) == value

@given(st.lists(st.floats(min_value=0.0001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1), 
       st.floats(min_value=0.0001, max_value=1000, allow_nan=False, allow_infinity=False))
def test_geometric_mean_scaling(data, factor):
    scaled_data = [x * factor for x in data]
    assert statistics.geometric_mean(scaled_data) == statistics.geometric_mean(data) * factor 

@given(st.lists(st.floats(min_value=0.0001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1))
def test_geometric_mean_positive(data):
    assert statistics.geometric_mean(data) > 0
# End program