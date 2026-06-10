from hypothesis import given, strategies as st
import numpy as np

# Define strategies for generating arrays with limitations to avoid overflows
array_strategy = st.arrays(dtype=np.float64, shape=st.tuples(st.integers(1, 5), st.integers(1, 5)), elements=st.floats(allow_nan=False, allow_infinity=False))

@given(a=array_strategy, b=array_strategy)
def test_numpy_dot_output_shape(a, b):
    """Test that the output shape is as expected based on input shapes and dot product type."""
    result = np.dot(a, b)
    expected_shape = (a.shape[0], b.shape[1]) if len(a.shape) == 2 and len(b.shape) == 2 else (a.shape[0],)
    assert result.shape == expected_shape

@given(a=array_strategy, b=array_strategy)
def test_numpy_dot_output_dtype(a, b):
    """Test that the output dtype matches the result of multiplying input element dtypes."""
    result = np.dot(a, b)
    expected_dtype = np.result_type(a.dtype, b.dtype)
    assert result.dtype == expected_dtype

@given(a=array_strategy, scalar=st.floats(allow_nan=False, allow_infinity=False))
def test_numpy_dot_scalar_multiplication(a, scalar):
    """Test that dot product with a scalar is equivalent to element-wise multiplication."""
    result_dot = np.dot(a, scalar)
    result_mult = a * scalar
    np.testing.assert_array_equal(result_dot, result_mult)

@given(a=array_strategy, b=array_strategy, c=array_strategy)
def test_numpy_dot_distributive_property(a, b, c):
    """Test that dot product distributes over addition."""
    result1 = np.dot(a, b + c)
    result2 = np.dot(a, b) + np.dot(a, c)
    np.testing.assert_array_almost_equal(result1, result2)  # Account for potential floating-point errors

@given(a=array_strategy, b=array_strategy, c=array_strategy)
def test_numpy_dot_associative_property(a, b, c):
    """Test that dot product is associative for matrix multiplication (with caveats)."""
    if a.shape[1] == b.shape[0] and b.shape[1] == c.shape[0]:
        result1 = np.dot(a, np.dot(b, c))
        result2 = np.dot(np.dot(a, b), c)
        np.testing.assert_array_almost_equal(result1, result2)  # Account for potential floating-point errors
# End program