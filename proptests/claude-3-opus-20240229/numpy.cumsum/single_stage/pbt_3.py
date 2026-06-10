from hypothesis import given, strategies as st
import numpy as np

# Summary: Generate a wide variety of array inputs, including different sizes, dimensions, and element types.
# Check properties such as output shape matches input shape, output dtype matches expected, and output values are correct.
@given(st.data())
def test_numpy_cumsum(data):
    # Generate array with varying shape, dimensions, and element types
    shape = data.draw(st.lists(st.integers(min_value=1, max_value=10), min_size=1, max_size=5))
    dtype = data.draw(st.sampled_from([np.int8, np.int16, np.int32, np.int64, np.float16, np.float32, np.float64]))
    a = data.draw(st.arrays(dtype=dtype, shape=shape))
    
    # Generate axis parameter (can be None, or an integer within valid range)
    axis = data.draw(st.one_of(st.none(), st.integers(min_value=-len(shape), max_value=len(shape)-1)))
    
    # Call numpy.cumsum with generated input
    result = np.cumsum(a, axis=axis)
    
    # Check that output array has same shape as input (or flattened if axis=None)
    if axis is None:
        assert result.shape == (a.size,)
    else:
        assert result.shape == a.shape
    
    # Check that output array has expected dtype based on input
    if dtype in [np.int8, np.int16, np.int32, np.int64]:
        assert result.dtype == np.int64
    else:
        assert result.dtype == dtype

    # Check that output values are correct
    if axis is None:
        expected = np.cumsum(a.flatten()) 
    else:
        expected = np.apply_along_axis(np.cumsum, axis, a)
    np.testing.assert_array_equal(result, expected)
# End program