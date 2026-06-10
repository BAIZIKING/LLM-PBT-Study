from hypothesis import given, strategies as st
import numpy as np

# Define strategies for generating input parameters
array_shapes = st.tuples(st.integers(min_value=0), st.integers(min_value=0))
data_types = st.sampled_from([np.int8, np.int16, np.int32, np.int64, 
                               np.uint8, np.uint16, np.uint32, np.uint64, 
                               np.float16, np.float32, np.float64, np.complex64, np.complex128])
axis_values = st.one_of(st.none(), st.integers(), st.tuples(st.integers()))
keepdims_values = st.booleans()
initial_values = st.floats(allow_nan=False, allow_infinity=False)

# Summary: Generates diverse input arrays, axes, and parameters for testing numpy.sum.
@given(st.data())
def test_numpy_sum(data):
    # Generate input data
    shape = data.draw(array_shapes)
    dtype = data.draw(data_types)
    a = data.draw(st.arrays(dtype, shape))
    axis = data.draw(axis_values)
    keepdims = data.draw(keepdims_values)
    initial = data.draw(initial_values)
    where = data.draw(st.arrays(np.bool, shape))

    # Calculate the expected output shape
    expected_shape = np.delete(a.shape, axis).tolist() if axis is not None else ()
    if keepdims:
        expected_shape = np.insert(expected_shape, axis, 1).tolist()

    # Calculate the expected sum using a different approach
    expected_sum = np.add.reduce(a, axis=axis, dtype=dtype, keepdims=keepdims, initial=initial, where=where)

    # Compute the sum using numpy.sum
    result = np.sum(a, axis=axis, dtype=dtype, keepdims=keepdims, initial=initial, where=where)

    # Check properties
    assert result.shape == tuple(expected_shape)
    assert result.dtype == expected_sum.dtype
    np.testing.assert_allclose(result, expected_sum)  # Account for potential floating-point differences

# End program