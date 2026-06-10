from hypothesis import given, strategies as st
import numpy as np

# Summary: This test generates arrays of varying lengths and dimensions, which also contain integers or floats.
# It then checks the properties related to numpy.cumsum
@given(st.data())
def test_numpy_cumsum(data):
    # Draw array size
    arr_size = data.draw(st.integers(min_value=0, max_value=100), label="Size of array")
    
    # Draw data type of array elements
    data_type = data.draw(st.sampled_from([int, float]), label="Element Data type")
    
    # Array of given size and type
    array = data.draw(st.lists(st.builds(data_type), min_size=arr_size, max_size=arr_size), label="Input Array")
    
    # Convert to numpy array
    array = np.array(array)
    
    # Calculate cumsum
    cumsum_arr = np.cumsum(array)
    
    # Check that output array is of the same shape as the input array
    assert cumsum_arr.shape == array.shape
    
    # Check that the output array has the correct dtype
    assert cumsum_arr.dtype == array.dtype
    
    # Check that the sum of all elements of output is equal to the last element, only for integer input
    if data_type == int:
        assert sum(cumsum_arr) == cumsum_arr[-1]
# End program