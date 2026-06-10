from hypothesis import given, strategies as st
import numpy as np

# Define strategies for generating arrays with controlled sizes and dtype
array_strategy = st.builds(np.array, st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=1), st.sampled_from([np.float32, np.float64]))

@given(array_strategy, array_strategy)
def test_numpy_dot_output_dtype(a, b):
    """Output dtype should be consistent with input dtypes."""
    output = np.dot(a, b)
    assert output.dtype == np.result_type(a.dtype, b.dtype)

@given(st.integers(min_value=1, max_value=5), st.integers(min_value=1, max_value=5), st.integers(min_value=1, max_value=5), st.integers(min_value=1, max_value=5))
def test_numpy_dot_output_shape(m, n, p, q):
    """Output shape should follow matrix multiplication/tensor contraction rules."""
    a = np.random.rand(m, n)
    b = np.random.rand(p, q)
    if n != p: 
        with pytest.raises(ValueError):
            np.dot(a, b)
    else:
        output = np.dot(a, b)
        assert output.shape == (m, q)

@given(st.floats(allow_infinity=False, allow_nan=False), array_strategy)
def test_numpy_dot_scalar_multiplication(scalar, array):
    """Dot product with scalar should be equivalent to element-wise multiplication."""
    output = np.dot(scalar, array)
    expected = scalar * array
    np.testing.assert_array_equal(output, expected)

@given(array_strategy, array_strategy, array_strategy)
def test_numpy_dot_distributive_property(a, b, c):
    """Dot product should distribute over addition for compatible shapes."""
    try:
        np.testing.assert_array_equal(np.dot(a, b + c), np.dot(a, b) + np.dot(a, c))
    except ValueError:
        pass  # Ignore cases with incompatible shapes

@given(array_strategy, array_strategy, array_strategy)
def test_numpy_dot_associative_property(a, b, c):
    """Dot product should be associative for compatible shapes (with caveats)."""
    try:
        np.testing.assert_array_almost_equal(np.dot(a, np.dot(b, c)), np.dot(np.dot(a, b), c)) 
    except ValueError:
        pass  # Ignore cases with incompatible shapes
# End program