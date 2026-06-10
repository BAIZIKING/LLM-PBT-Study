from hypothesis import given, strategies as st
import numpy as np

# Define strategies for generating arrays with controlled size and element values
array_strategy = st.builds(np.array, st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=5), st.integers(min_value=1, max_value=3))

@given(a=array_strategy, b=array_strategy)
def test_numpy_dot_output_dtype(a, b):
    """Output dtype should be consistent with input dtypes and arithmetic rules."""
    output = np.dot(a, b)
    assert output.dtype == np.result_type(a.dtype, b.dtype)

@given(a=array_strategy, b=array_strategy)
def test_numpy_dot_output_shape(a, b):
    """Output shape should follow rules of matrix multiplication/tensor contraction."""
    output = np.dot(a, b)
    if a.ndim == 1 and b.ndim == 1:
        assert output.shape == ()  # scalar output for dot product of vectors
    else:
        expected_shape = np.dot(np.empty(a.shape), np.empty(b.shape)).shape
        assert output.shape == expected_shape

@given(a=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=5), b=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=5))
def test_numpy_dot_commutative_1d(a, b):
    """np.dot(a, b) should be equal to np.dot(b, a) for 1D arrays."""
    a_array = np.array(a)
    b_array = np.array(b)
    assert np.dot(a_array, b_array) == np.dot(b_array, a_array)

@given(a=array_strategy, b=array_strategy, c=array_strategy)
def test_numpy_dot_distributive(a, b, c):
    """np.dot should be distributive over addition."""
    assert np.allclose(np.dot(a, b + c), np.dot(a, b) + np.dot(a, c))

@given(a=array_strategy, b=array_strategy, k=st.floats(allow_nan=False, allow_infinity=False))
def test_numpy_dot_scalar_associative(a, b, k):
    """Scaling input is equivalent to scaling output."""
    assert np.allclose(np.dot(k * a, b), k * np.dot(a, b))
# End program