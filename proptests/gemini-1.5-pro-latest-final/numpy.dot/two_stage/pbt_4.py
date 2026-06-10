from hypothesis import given, strategies as st
import numpy as np

# Define strategies for generating arrays with limitations on size and values to avoid overflows
array_strategy = st.arrays(dtype=np.float64, shape=st.tuples(st.integers(1, 4), st.integers(1, 4)), 
                           elements=st.floats(allow_nan=False, allow_infinity=False))

@given(a=array_strategy, b=array_strategy)
def test_output_shape(a, b):
    """Checks if the output shape of np.dot is as expected."""
    output = np.dot(a, b)
    expected_shape = (a.shape[0], b.shape[1])
    assert output.shape == expected_shape

@given(a=array_strategy, b=array_strategy)
def test_output_dtype(a, b):
    """Checks if the output dtype of np.dot is consistent with input dtypes."""
    output = np.dot(a, b)
    assert output.dtype == np.result_type(a.dtype, b.dtype)

@given(array=array_strategy, scalar=st.floats(allow_nan=False, allow_infinity=False))
def test_scalar_multiplication(array, scalar):
    """Checks if dot product with a scalar is equivalent to element-wise multiplication."""
    output = np.dot(array, scalar)
    expected_output = array * scalar
    np.testing.assert_array_equal(output, expected_output)

@given(a=array_strategy, b=array_strategy, c=array_strategy)
def test_distributive_property(a, b, c):
    """Checks the distributive property of dot product."""
    output1 = np.dot(a, b + c)
    output2 = np.dot(a, b) + np.dot(a, c)
    np.testing.assert_array_almost_equal(output1, output2) 

@given(a=array_strategy, b=array_strategy, c=array_strategy)
def test_associative_property(a, b, c):
    """Checks the associative property of dot product for compatible shapes."""
    if a.shape[1] == b.shape[0] and b.shape[1] == c.shape[0]:
        output1 = np.dot(a, np.dot(b, c))
        output2 = np.dot(np.dot(a, b), c)
        np.testing.assert_array_almost_equal(output1, output2) 
# End program