from hypothesis import given, strategies as st
from statistics import median

# Generate a variety of input data including edge cases like empty lists, 
# lists with duplicate values, lists with a mix of integers and floats,
# and very large lists. Use both odd and even length lists.
@given(st.lists(st.one_of(st.integers(), st.floats(allow_nan=False, allow_infinity=False)), min_size=0, max_size=1000))
def test_median(data):
    # Check that the result is always a number (int or float)
    assert isinstance(median(data), (int, float))
    
    # For non-empty input, check that the median is between the min and max of the input
    if len(data) > 0:
        assert min(data) <= median(data) <= max(data)
    
    # Check that the median is equal to the middle element for odd-length input
    if len(data) % 2 == 1:
        sorted_data = sorted(data)
        assert median(data) == sorted_data[len(data) // 2]
        
    # Check that the median is equal to the mean of the two middle elements for even-length input  
    if len(data) % 2 == 0 and len(data) > 0:
        sorted_data = sorted(data)
        assert median(data) == (sorted_data[len(data)//2 - 1] + sorted_data[len(data)//2]) / 2
# End program        