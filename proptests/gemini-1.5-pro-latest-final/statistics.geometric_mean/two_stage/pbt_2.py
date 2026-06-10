from hypothesis import given, strategies as st
import statistics

# Property 1: The output is always positive.
@given(st.lists(st.floats(min_value=0.0001, max_value=1000), min_size=1))  
def test_geometric_mean_positive(data):
    result = statistics.geometric_mean(data)
    assert result > 0

# Property 2: The output is never greater than the arithmetic mean of the same input.
@given(st.lists(st.floats(min_value=0.0001, max_value=1000), min_size=1))
def test_geometric_mean_less_than_arithmetic_mean(data):
    result = statistics.geometric_mean(data)
    assert result <= statistics.mean(data)

# Property 3: If all inputs are identical, the output equals the input values.
@given(st.floats(min_value=0.0001, max_value=1000))
def test_geometric_mean_equal_for_identical_inputs(x):
    data = [x] * 5  
    result = statistics.geometric_mean(data)
    assert result == x

# Property 4: The output is in the same units as the input values. 
# (This property can't be directly tested with Hypothesis as it's about units, not values)

# Property 5: If one of the input values increases, while others remain the same, the output will not decrease. 
@given(st.lists(st.floats(min_value=0.0001, max_value=1000), min_size=2), 
       st.integers(min_value=0, max_value=1))
def test_geometric_mean_increases_with_increasing_value(data, index_to_increase):
    original_result = statistics.geometric_mean(data)
    data[index_to_increase] *= 2  
    new_result = statistics.geometric_mean(data)
    assert new_result >= original_result
# End program