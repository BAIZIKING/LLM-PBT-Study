from hypothesis import given, strategies as st
import numpy as np

# Define strategies for array generation with controlled size and element range
array_strategy = st.arrays(dtype=np.float64, 
                           shape=st.tuples(st.integers(min_value=1, max_value=5), 
                                          st.integers(min_value=1, max_value=5)),
                           elements=st.floats(min_value=-1e6, max_value=1e6))
axis_strategy = st.integers(min_value=0, max_value=1) # Limit axis to 0 or 1 for 2D arrays


@given(array_strategy, axis_strategy)
def test_numpy_cumsum_shape_consistency(arr, axis):
    result = np.cumsum(arr, axis=axis)
    if axis is None:
        assert result.shape == arr.shape
    else:
        assert result.shape == arr.shape

@given(array_strategy, axis_strategy, st.booleans())
def test_numpy_cumsum_dtype_consistency(arr, axis, use_int_dtype):
    dtype = np.int32 if use_int_dtype else None
    result = np.cumsum(arr, axis=axis, dtype=dtype)
    if dtype is None:
        assert result.dtype == arr.dtype
    else:
        assert result.dtype == dtype

@given(array_strategy)
def test_numpy_cumsum_final_element_sum(arr):
    result = np.cumsum(arr)
    np.testing.assert_allclose(result[-1], np.sum(arr), rtol=1e-5)

@given(array_strategy, axis_strategy)
def test_numpy_cumsum_monotonicity(arr, axis):
    result = np.cumsum(arr, axis=axis)
    if (arr >= 0).all():
        assert np.all(np.diff(result, axis=axis) >= 0)
    elif (arr <= 0).all():
        assert np.all(np.diff(result, axis=axis) <= 0)

@given(array_strategy, axis_strategy)
def test_numpy_cumsum_reversibility_diff(arr, axis):
    result = np.cumsum(arr, axis=axis)
    recovered = np.diff(result, axis=axis, prepend=0)
    np.testing.assert_allclose(recovered, arr)
# End program