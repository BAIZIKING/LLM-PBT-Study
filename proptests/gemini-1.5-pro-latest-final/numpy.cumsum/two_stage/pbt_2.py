from hypothesis import given, strategies as st
import numpy as np

# Define strategy for generating arrays with controlled size and elements to avoid overflow issues
array_strategy = st.arrays(dtype=np.float64, shape=st.tuples(st.integers(1, 5), st.integers(1, 5)), 
                           elements=st.floats(allow_nan=False, allow_infinity=False))

@given(array_strategy)
def test_shape_consistency(a):
    """Shape of output should match input array when axis is not specified or input is 1D."""
    assert np.cumsum(a).shape == a.shape
    assert np.cumsum(a, axis=None).shape == a.shape

@given(array_strategy, st.integers(min_value=0, max_value=1))
def test_axis_summation(a, axis):
    """Elements along specified axis should be the cumulative sum."""
    result = np.cumsum(a, axis=axis)
    expected_shape = list(a.shape)
    expected_shape[axis] = 1
    assert (result.cumsum(axis=axis) == a.cumsum(axis=axis)).all()
    assert result.shape == tuple(expected_shape) 

@given(array_strategy, st.sampled_from([np.int32, np.float32, np.float64]))
def test_dtype_consistency(a, dtype):
    """Output dtype should match specified dtype or default to input dtype."""
    result = np.cumsum(a, dtype=dtype)
    assert result.dtype == dtype

@given(array_strategy)
def test_first_element(a):
    """First element of output should always match first element of input.""" 
    assert np.cumsum(a).flat[0] == a.flat[0]
    assert np.cumsum(a, axis=0)[0,0] == a[0,0]
    assert np.cumsum(a, axis=1)[0,0] == a[0,0]

@given(st.data())
def test_monotonicity(data):
    """Cumulative sum of non-decreasing array should be non-decreasing."""
    a = data.draw(array_strategy)
    np.testing.assert_array_less(-np.diff(a), 0) # Check if input array is non-decreasing
    assert (np.diff(np.cumsum(a)) >= 0).all()  # Check if output is non-decreasing

# End program