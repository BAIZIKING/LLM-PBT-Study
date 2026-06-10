from hypothesis import given, strategies as st
from statistics import geometric_mean
from pytest import raises

# Generate a wide variety of numeric input data, including:
# - Empty lists 
# - Lists containing a 0
# - Lists containing negative numbers
# - Lists containing very large and small floats
# - Lists of varying lengths
@given(st.lists(st.one_of(
    st.integers(min_value=-1000000000, max_value=1000000000), 
    st.floats(min_value=-1e100, max_value=1e100, allow_nan=False, allow_infinity=False)
), min_size=0, max_size=1000))
def test_geometric_mean(data):
    # Test that an empty list raises a StatisticsError
    if len(data) == 0:
        with raises(StatisticsError):
            geometric_mean(data)
        return
    
    # Test that a list containing 0 raises a StatisticsError
    if 0 in data:
        with raises(StatisticsError):
            geometric_mean(data)
        return
    
    # Test that a list containing a negative number raises a StatisticsError
    if any(x < 0 for x in data):
        with raises(StatisticsError):
            geometric_mean(data)
        return
    
    # Test that the result is positive
    assert geometric_mean(data) > 0

    # Test that the result is less than or equal to the maximum value in the data
    assert geometric_mean(data) <= max(data)
    
    # Test that the result is greater than or equal to the minimum value in the data 
    assert geometric_mean(data) >= min(data)
# End program