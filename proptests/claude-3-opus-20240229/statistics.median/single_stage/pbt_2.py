from hypothesis import given, strategies as st
from statistics import median
import pytest

# Generate a variety of numeric data types including integers, floats, and decimals.
# Include both odd and even sized lists, as well as edge cases like empty lists, 
# lists with duplicate values, and lists with very large or very small numbers.
@given(st.lists(st.one_of(st.integers(), st.floats(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False)))) 
def test_statistics_median(data):
    # Test that the median is always one of the values for lists with an odd number of elements
    if len(data) % 2 == 1 and len(data) > 0:
        assert median(data) in data
    
    # Test that the median is between the min and max values (inclusive)
    if len(data) > 0:
        assert min(data) <= median(data) <= max(data)
    
    # Test that the median is the mean of the two middle values for lists with an even number of elements
    if len(data) % 2 == 0 and len(data) >= 2:
        sorted_data = sorted(data)
        lower = sorted_data[len(data)//2-1]  
        upper = sorted_data[len(data)//2]
        assert median(data) == (lower + upper) / 2
        
    # Test that empty list raises StatisticsError
    if len(data) == 0:
        with pytest.raises(StatisticsError):
            median(data)
# End program