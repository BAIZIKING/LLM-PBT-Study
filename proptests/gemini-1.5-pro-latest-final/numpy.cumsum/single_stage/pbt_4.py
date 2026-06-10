from hypothesis import given, strategies as st
import numpy as np

# Summary: Generates arrays of various shapes, data types, and axis values to test numpy.cumsum
@given(
    data=st.data(),
    shape=st.tuples(st.integers(min_value=0, max_value=5), st.integers(min_value=0, max_value=5)),
    dtype=st.sampled_from([np.int8, np.int16, np.int32, np.int64, np.float16, np.float32, np.float64, np.complex64, np.complex128]),
    axis=st.integers(min_value=-1, max_value=3),
)
def test_numpy_cumsum(data, shape, dtype, axis):
    # Generate input array
    arr = data.draw(st.arrays(dtype, shape))

    # Calculate cumulative sum using numpy.cumsum
    result = np.cumsum(arr, axis=axis, dtype=dtype)

    # Check output shape
    if axis is None or arr.ndim == 1:
        assert result.shape == arr.shape
    else:
        # Verify shape change based on axis
        expected_shape = list(arr.shape)
        expected_shape[axis] = 1
        assert result.shape == tuple(expected_shape)

    # Check data type
    assert result.dtype == dtype

    # Check cumulative sum calculation (simplified for brevity)
    if arr.size > 0:
        assert result[-1] == arr.sum(axis=axis)

# End program