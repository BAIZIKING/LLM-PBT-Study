from hypothesis import given, strategies as st
import numpy as np

# Define strategies for array generation, considering potential overflows
array_strategy = st.arrays(dtype=np.float64, shape=st.tuples(st.integers(1, 5), st.integers(1, 5)), 
                           elements=st.floats(allow_nan=False, allow_infinity=False)) 
axis_strategy = st.integers(min_value=-1, max_value=1)  # -1 for last dimension, 0 and 1 for 2D arrays

@given(data=st.data())
def test_numpy_cumsum_shape(data):
    a = data.draw(array_strategy)
    axis = data.draw(axis_strategy)
    result = np.cumsum(a, axis=axis)
    expected_shape = a.shape if axis is None or a.ndim == 1 else list(a.shape)  # Adjust shape for axis
    if axis is not None:
        expected_shape[axis] = 1  # Dimension along axis becomes 1
    assert result.shape == tuple(expected_shape)

@given(data=st.data())
def test_numpy_cumsum_dtype(data):
    a = data.draw(array_strategy)
    dtype = data.draw(st.sampled_from([np.int32, np.int64, np.float32, np.float64]))
    result = np.cumsum(a, dtype=dtype)
    assert result.dtype == dtype

@given(data=st.data())
def test_numpy_cumsum_calculation(data):
    a = data.draw(array_strategy)
    axis = data.draw(axis_strategy)
    result = np.cumsum(a, axis=axis)
    if axis is None:
        assert np.all(result == np.cumsum(a.flatten()))  # Check against flattened array
    else:
        for i in range(a.shape[axis]):
            assert np.all(result[(slice(None),) * axis + (i,)] == np.cumsum(a[(slice(None),) * axis + (i,)], axis=None))

@given(data=st.data())
def test_numpy_cumsum_final_element(data):
    a = data.draw(array_strategy)
    axis = data.draw(axis_strategy)
    result = np.cumsum(a, axis=axis)
    if axis is None:
        assert result[-1] == np.sum(a)
    else:
        assert np.all(result[(slice(None),) * axis + (-1,)] == np.sum(a, axis=axis, keepdims=True))

@given(data=st.data())
def test_numpy_cumsum_empty_array(data):
    a = data.draw(st.arrays(dtype=np.float64, shape=st.tuples(st.integers(0, 0), st.integers(0, 0))))  # Empty array
    axis = data.draw(axis_strategy)
    result = np.cumsum(a, axis=axis)
    assert result.shape == a.shape and result.size == 0  # Check shape and size for empty array 
# End program