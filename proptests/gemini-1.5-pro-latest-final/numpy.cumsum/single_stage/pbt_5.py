from hypothesis import given, strategies as st
import numpy as np

# Summary: Generates arrays with different shapes, data types, and values,
#          and tests the properties of numpy.cumsum based on the API documentation.
@given(
    data=st.data(),
    shape=st.integers(min_value=1, max_value=3).flatmap(
        lambda d: st.tuples(*[st.integers(min_value=0, max_value=5) for _ in range(d)])
    ),
    dtype=st.sampled_from([np.int32, np.float64, bool]),
    axis=st.integers(min_value=-1, max_value=2),
)
def test_numpy_cumsum(data, shape, dtype, axis):
    arr = data.draw(st.arrays(dtype, shape))

    # Check output shape
    result = np.cumsum(arr, axis=axis)
    expected_shape = arr.shape if axis is None or arr.ndim == 1 else list(arr.shape)
    if axis is not None and arr.ndim > 1:
        expected_shape[axis] = 1
    assert result.shape == tuple(expected_shape)

    # Check data type consistency
    assert result.dtype == arr.dtype if dtype is None else dtype

    # Verify cumulative sum calculation (for small arrays)
    if arr.size <= 10:
        expected_result = np.array([arr[:i].sum(axis=axis) for i in range(1, arr.size + 1)])
        np.testing.assert_array_equal(result, expected_result)

    # Check overflow behavior (for integer types)
    if np.issubdtype(arr.dtype, np.integer):
        overflow_result = np.cumsum(np.array([2**31 - 1, 1], dtype=arr.dtype))
        assert overflow_result[1] == 0  # modular arithmetic
# End program