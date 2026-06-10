from hypothesis import given, strategies as st
import numpy as np

@given(st.lists(st.integers(), min_size=1), st.just(None) | st.integers(0, 10), 
       st.sampled_from([None, np.int32, np.float32, np.float64]))
def test_numpy_cumsum_property(input_data, axis, dtype):
    # Convert the input data to a numpy array
    input_array = np.array(input_data)

    # Execute numpy.cumsum
    output = np.cumsum(input_array, axis=axis, dtype=dtype)

    # Test 1: Return type is numpy array
    assert isinstance(output, np.ndarray)

    # Test 2: Consistent shape, the output shape should be the same as input or 1D if axis=None
    if axis is None:
        assert output.shape == (len(input_data),)
    else:
        assert output.shape == input_array.shape

    # Test 3: Cumulative nature, each element in output is sum of all preceding elements in the input
    if axis is None:
        for i in range(1, len(output)):
            assert output[i] == output[i-1] + input_array[i]

    # Test 4: Overflow Handling, when dtype is int and result > np.iinfo(dtype).max, positive overflow wraps to negative
    if dtype and np.issubdtype(dtype, np.integer):
        maximum_value = np.iinfo(dtype).max
        overflow_index = next((i for i, val in enumerate(output) if val > maximum_value), None)
        if overflow_index is not None:
            assert output[overflow_index] < 0

    # Test 5: Check dtype of output, if dtype is given, output dtype should be as expected.
    expected_dtype = dtype or (np.float64 if np.issubdtype(input_array.dtype, np.integer) 
                               and input_array.dtype.itemsize < np.dtype('int').itemsize 
                               else input_array.dtype)
    assert output.dtype == expected_dtype