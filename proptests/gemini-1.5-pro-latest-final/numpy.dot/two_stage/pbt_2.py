from hypothesis import given, strategies as st
import numpy as np

# Define strategies for generating arrays with controlled sizes and element types
small_ints = st.integers(min_value=-100, max_value=100)
array_shapes = st.tuples(st.integers(min_value=1, max_value=3), st.integers(min_value=1, max_value=3))

@given(data=st.data(), shape=array_shapes)
def test_numpy_dot_output_dtype(data, shape):
    # Generate arrays with random dtypes and given shape
    arr1 = data.draw(st.arrays(dtype=st.sampled_from(np.sctypes['int']), shape=shape))
    arr2 = data.draw(st.arrays(dtype=st.sampled_from(np.sctypes['float']), shape=shape))

    # Calculate dot product and check output dtype
    result = np.dot(arr1, arr2)
    assert result.dtype == np.result_type(arr1, arr2)

@given(data=st.data(), shape1=array_shapes, shape2=array_shapes)
def test_numpy_dot_output_shape(data, shape1, shape2):
    # Generate arrays with compatible shapes
    arr1 = data.draw(st.arrays(dtype=float, shape=shape1))
    arr2 = data.draw(st.arrays(dtype=float, shape=shape2))
    
    # Calculate dot product and check output shape
    result = np.dot(arr1, arr2)
    expected_shape = (shape1[0], shape2[1])
    assert result.shape == expected_shape

@given(data=st.data(), arr=st.arrays(dtype=float, shape=array_shapes), scalar=st.floats(allow_nan=False))
def test_numpy_dot_scalar_multiplication(data, arr, scalar):
    # Calculate dot product with scalar and compare to element-wise multiplication
    dot_result = np.dot(scalar, arr)
    mult_result = scalar * arr
    np.testing.assert_array_equal(dot_result, mult_result)

@given(data=st.data(), shape=(array_shapes, array_shapes, array_shapes))
def test_numpy_dot_distributive_property(data, shape):
    # Generate arrays with compatible shapes
    arr1 = data.draw(st.arrays(dtype=float, shape=shape[0]))
    arr2 = data.draw(st.arrays(dtype=float, shape=shape[1]))
    arr3 = data.draw(st.arrays(dtype=float, shape=shape[2]))

    # Test distributive property
    result1 = np.dot(arr1, arr2 + arr3)
    result2 = np.dot(arr1, arr2) + np.dot(arr1, arr3)
    np.testing.assert_array_almost_equal(result1, result2)

@given(data=st.data(), shape=(array_shapes, array_shapes, array_shapes))
def test_numpy_dot_associative_property(data, shape):
    # Generate arrays with compatible shapes
    arr1 = data.draw(st.arrays(dtype=float, shape=shape[0]))
    arr2 = data.draw(st.arrays(dtype=float, shape=shape[1]))
    arr3 = data.draw(st.arrays(dtype=float, shape=shape[2]))

    # Test associative property
    result1 = np.dot(arr1, np.dot(arr2, arr3))
    result2 = np.dot(np.dot(arr1, arr2), arr3)
    np.testing.assert_array_almost_equal(result1, result2)
# End program