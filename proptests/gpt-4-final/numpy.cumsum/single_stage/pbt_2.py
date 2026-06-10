from hypothesis import given, strategies as st
import numpy as np

# Strategy: Generate lists of various lengths (including edge cases) that contain integers, floats, and nested lists
@given(st.lists(st.one_of(st.integers(), st.floats(allow_nan=False, allow_infinity=False), st.lists(elements=st.floats(allow_nan=False, allow_infinity=False), min_size=1)), min_size=0))
def test_numpy_cumsum_property(input_list):
    # Convert to np array since input parameter of cumsum should array_like
    arr = np.array(input_list)
    
    # Calculate the cumsum
    cumsum_result = np.cumsum(arr)
    
    # Property: For a 1d array, the result should have the same length as the input array.
    if len(input_list) > 0 and (not isinstance(input_list[0], list)):
        assert len(cumsum_result) == len(input_list)

    # Property: The cumsum of an empty list should be an empty list.
    if len(input_list) == 0:
        assert len(cumsum_result) == 0

    # Property: The cumsum of a list with one number should be a list with that number.
    if len(input_list) == 1:
        assert cumsum_result[0] == input_list[0]
        
    # Property: For an ndarray input array, the result should have the same shape as the input array if the axis is not None.
    axis = np.random.choice([None, 0, 1], p=[0.5, 0.25, 0.25]) if arr.ndim != 1 else None
    
    cumsum_result_axis = np.cumsum(arr, axis=axis)
    
    if axis is not None:
        assert arr.shape == cumsum_result_axis.shape
# End program