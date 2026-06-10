from hypothesis import given, strategies as st
import numpy as np

# Define strategy for generating arrays with controlled size and element range
array_strategy = st.arrays(dtype=np.float64, 
                           shape=st.tuples(st.integers(min_value=1, max_value=5), 
                                           st.integers(min_value=1, max_value=5)),
                           elements=st.floats(min_value=-1e6, max_value=1e6))

@given(array_strategy, st.integers(min_value=0, max_value=1), st.sampled_from([np.float32, np.float64]))
def test_numpy_cumsum_shape_preservation(arr, axis, dtype):
    # Test that output shape matches input shape unless axis is specified
    result = np.cumsum(arr, axis=axis, dtype=dtype)
    if axis is None:
        assert result.shape == arr.shape 
    else:
        assert result.shape == np.delete(arr.shape, axis)

@given(array_strategy, st.sampled_from([None, np.float32, np.float64]))
def test_numpy_cumsum_dtype(arr, dtype):
    # Test output dtype matches specified dtype or input dtype
    result = np.cumsum(arr, dtype=dtype)
    if dtype is None:
        assert result.dtype == arr.dtype 
    else:
        assert result.dtype == dtype

@given(array_strategy)
def test_numpy_cumsum_final_element(arr):
    # Test final element matches sum with consideration for floating-point precision
    result = np.cumsum(arr)
    np.testing.assert_allclose(result[-1], np.sum(arr), rtol=1e-5)

@given(array_strategy)
def test_numpy_cumsum_monotonicity(arr):
    # Test monotonicity along the axis of cumulation (axis=None here)
    result = np.cumsum(arr)
    assert all(np.diff(result) >= 0)

@given(array_strategy, array_strategy)
def test_numpy_cumsum_linearity(arr1, arr2):
    # Test linearity of cumsum with respect to element-wise sum
    assert np.allclose(np.cumsum(arr1 + arr2), np.cumsum(arr1) + np.cumsum(arr2))
# End program