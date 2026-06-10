from hypothesis import given, strategies as st
import statistics

# Property 1: Greater than or equal to the minimum value
@given(st.lists(st.floats(min_value=0.0001, max_value=1000), min_size=1)) 
def test_geometric_mean_greater_than_min(data):
    result = statistics.geometric_mean(data)
    assert result >= min(data)

# Property 2: Less than or equal to the maximum value
@given(st.lists(st.floats(min_value=0.0001, max_value=1000), min_size=1))
def test_geometric_mean_less_than_max(data):
    result = statistics.geometric_mean(data)
    assert result <= max(data)

# Property 3: Equal to the value if all values are equal
@given(st.floats(min_value=0.0001, max_value=1000))
def test_geometric_mean_equal_when_all_equal(value):
    data = [value] * 5  
    result = statistics.geometric_mean(data)
    assert result == value

# Property 4: Sensitive to scale
@given(st.lists(st.floats(min_value=0.0001, max_value=1000), min_size=1), 
       st.floats(min_value=0.0001, max_value=1000))
def test_geometric_mean_scale_sensitivity(data, factor):
    scaled_data = [x * factor for x in data]
    result = statistics.geometric_mean(data)
    scaled_result = statistics.geometric_mean(scaled_data)
    assert scaled_result == result * factor 

# Property 5: Errors on zero or negative values
@given(st.one_of(st.lists(st.floats(max_value=0), min_size=1, max_size=1), 
                 st.lists(st.floats(min_value=-1000, max_value=-0.0001), min_size=1, max_size=1)))
def test_geometric_mean_error_on_zero_negative(data):
    with pytest.raises(statistics.StatisticsError):
        result = statistics.geometric_mean(data)

# End program