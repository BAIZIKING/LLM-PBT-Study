from hypothesis import given, strategies as st
import numpy as np

# Define strategies for generating arrays
array_shapes = st.tuples(st.integers(0, 5), st.integers(0, 5))
data_types = st.sampled_from([np.int8, np.int16, np.int32, np.int64, 
                              np.float16, np.float32, np.float64, np.complex64, np.complex128])
array_data = st.data()

# Generate pairs of arrays and optional arguments
@given(array_shapes, array_shapes, data_types, data_types, array_data)
def test_numpy_add(shape1, shape2, dtype1, dtype2, data):
    # Generate arrays with specified shapes and data types
    x1 = data.draw(st.arrays(dtype1, shape1, elements=st.floats(allow_nan=True, allow_infinity=True)))
    x2 = data.draw(st.arrays(dtype2, shape2, elements=st.floats(allow_nan=True, allow_infinity=True)))
    
    # Draw optional arguments for np.add
    where_cond = data.draw(st.booleans())
    out_array = data.draw(st.arrays(dtype1, shape1)) if where_cond else None

    # Perform addition and check properties
    result = np.add(x1, x2, out=out_array, where=where_cond)
    expected = x1 + x2

    # Check element-wise sum
    np.testing.assert_allclose(result, expected, rtol=1e-5)

    # Check output shape
    assert result.shape == np.broadcast(x1, x2).shape

    # Check output data type
    # (further assertions can be added for specific casting rules)

    # Check output array
    if out_array is not None:
        assert out_array is result
    
    # Check where argument
    if where_cond:
        assert np.array_equal(result[where_cond], expected[where_cond])

# End program