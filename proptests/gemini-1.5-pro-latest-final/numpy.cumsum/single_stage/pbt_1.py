from hypothesis import given, strategies as st
import numpy as np

# Summary: The generation strategy aims to create a diverse set of inputs for `np.cumsum` to ensure robust testing. 
# It considers various shapes and dtypes for the input array and different axis values. Edge cases, like empty arrays and 
# arrays with a single element, are also included.

@given(
    data=st.data(),
    shape=st.tuples(st.integers(min_value=0, max_value=5), st.integers(min_value=0, max_value=5)),
    dtype=st.sampled_from([np.int8, np.int16, np.int32, np.int64, np.float16, np.float32, np.float64]),
    axis=st.integers(min_value=-1, max_value=1),
)
def test_numpy_cumsum(data, shape, dtype, axis):
    # Generate input array with specified shape and dtype
    a = data.draw(st.arrays(dtype, shape))

    # Calculate cumulative sum using np.cumsum
    result = np.cumsum(a, axis=axis)

    # Properties to check:
    # 1. Shape of the result: 
    #   - If axis is None, the result should be a 1D array.
    #   - If axis is specified, the shape of the result should match the input array except for the dimension along the specified axis, 
    #     which should have a size of 1.
    if axis is None:
        assert result.ndim == 1
    else:
        expected_shape = list(a.shape)
        expected_shape[axis] = 1
        assert result.shape == tuple(expected_shape)

    # 2. Data type of the result: The data type of the result should match the specified dtype or the default dtype of the input array.
    assert result.dtype == dtype

    # 3. Cumulative sum calculation: 
    #   - For each element in the result, it should be equal to the sum of all the elements up to that position along the specified axis in the input array.
    #   - Handle edge cases like empty arrays and arrays with a single element.
    if a.size > 0:
        if axis is None:
            np.testing.assert_array_equal(result, np.cumsum(a.flatten()))
        else:
            for i in range(result.shape[axis]):
                np.testing.assert_array_equal(result.take(i, axis=axis), np.sum(a.take(np.arange(i + 1), axis=axis), axis=axis))

# End program