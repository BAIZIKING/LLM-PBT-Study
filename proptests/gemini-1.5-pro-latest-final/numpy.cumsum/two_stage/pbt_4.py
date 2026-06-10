from hypothesis import given, strategies as st
import numpy as np

# Define a strategy for generating arrays with reasonable sizes and avoiding overflows
array_strategy = st.arrays(dtype=np.float64, shape=st.tuples(st.integers(1, 5), st.integers(1, 5)), elements=st.floats(allow_nan=False, allow_infinity=False))

@given(array_strategy)
def test_shape_consistency(a):
    """Checks if the output shape matches the input shape when axis is not specified."""
    assert np.cumsum(a).shape == a.shape

@given(array_strategy, st.integers(min_value=0, max_value=1))
def test_element_relationship(a, axis):
    """Verifies the cumulative sum property along the specified axis."""
    result = np.cumsum(a, axis=axis)
    for i in range(result.shape[axis]):
        expected_sum = np.sum(a.take(np.arange(i + 1), axis=axis), axis=axis)
        assert np.allclose(result.take(i, axis=axis), expected_sum)

@given(array_strategy, st.sampled_from([np.float32, np.float64, np.int32, np.int64]))
def test_dtype_consistency(a, dtype):
    """Checks if the output dtype matches the specified dtype."""
    assert np.cumsum(a, dtype=dtype).dtype == dtype

@given(array_strategy)
def test_first_element(a):
    """Verifies that the first element of the output is the same as the input."""
    assert np.all(np.cumsum(a)[0] == a[0])

@given(st.arrays(dtype=np.float64, shape=st.tuples(st.integers(1, 5), st.integers(1, 5)), elements=st.floats(min_value=0, allow_nan=False, allow_infinity=False)), 
       st.integers(min_value=0, max_value=1))
def test_monotonicity(a, axis):
    """Checks for monotonically non-decreasing values in the output for non-negative inputs."""
    result = np.cumsum(a, axis=axis)
    assert np.all(np.diff(result, axis=axis) >= 0)

# End program