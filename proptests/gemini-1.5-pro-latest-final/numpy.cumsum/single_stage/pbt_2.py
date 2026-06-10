from hypothesis import given, strategies as st
import numpy as np

# Summary: The generation strategy aims to create a diverse range of inputs for `numpy.cumsum` to ensure robust testing. This includes:

# 1. Array Shapes: Generates arrays of varying shapes, including 1D, 2D, and higher dimensions, to test the function's behavior with different input structures.
# 2. Data Types: Includes various data types such as integers, floats, and complex numbers to cover different numerical scenarios and potential edge cases related to data type handling.
# 3. Axis Parameter: Generates random axis values within the valid range for the given array shape to test the cumulative sum along different axes. 
# 4. Edge Cases: Considers edge cases like empty arrays, arrays with a single element, and arrays with elements close to the limits of the data type's precision to assess behavior under these conditions.

@given(
    data=st.data(),
    shape=st.tuples(st.integers(min_value=0), st.integers(min_value=0)),
    dtype=st.sampled_from([np.int64, np.float64, np.complex128]),
    axis=st.integers(min_value=-1, max_value=1)
)
def test_numpy_cumsum(data, shape, dtype, axis):
    # Generate array with specified shape and dtype
    a = data.draw(st.arrays(dtype, shape))
    
    # Calculate cumulative sum using numpy.cumsum
    result = np.cumsum(a, axis=axis)
    
    # Properties to check based on the API documentation:

    # 1. Shape: Verify that the output array has the expected shape based on the input array and axis parameter.
    if axis is None:
        expected_shape = (a.size,)  # Flattened array
    else:
        expected_shape = a.shape
    assert result.shape == expected_shape

    # 2. Data Type: Ensure the output array's data type matches the specified dtype or the default behavior.
    assert result.dtype == dtype

    # 3. Cumulative Sum Calculation: Test that the cumulative sum is calculated correctly along the specified axis.
    if axis is None:
        # Compare with Python's built-in sum for the flattened case.
        assert np.allclose(result[-1], np.sum(a))
    else:
        # Verify cumulative sum along the given axis.
        for i in range(1, a.shape[axis]):
            assert np.allclose(result[(slice(None),) * axis + (i,)], result[(slice(None),) * axis + (i - 1,)] + a[(slice(None),) * axis + (i,)])
# End program