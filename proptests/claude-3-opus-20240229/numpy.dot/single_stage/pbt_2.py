from hypothesis import given, strategies as st
import numpy as np

# Generate a wide variety of random input arrays to test numpy.dot:
# - Test different array shapes: 0-D (scalar), 1-D, 2-D, and N-D 
# - Test different array sizes, including empty and large arrays
# - Test different numeric data types: int, float, complex
# - Sometimes generate the optional `out` array parameter
#
# Verify properties based on the numpy.dot documentation:
# - Return value is a scalar if both inputs are scalar or 1-D
# - Otherwise return value is an array
# - Returned array has expected shape based on input shapes
# - Returned values are the expected dot products
# - Passing an `out` array of the right type/shape/order returns it
# - ValueError is raised if last dim of a != second-to-last dim of b
@given(st.data())
def test_numpy_dot(data):
    # Generate variety of random input arrays a and b
    a = data.draw(st.one_of(
        st.floats(), # 0-D scalar 
        arrays(shape=st.integers(0, 10), dtype=scalar_dtypes()), # 1-D
        arrays(shape=array_shapes(max_dims=2), dtype=scalar_dtypes()), # 2-D
        arrays(shape=array_shapes(min_dims=3), dtype=scalar_dtypes()) # N-D
    ))
    b = data.draw(st.one_of(
        st.floats(), # 0-D scalar
        arrays(shape=st.integers(0, 10), dtype=scalar_dtypes()), # 1-D 
        arrays(shape=array_shapes(max_dims=2), dtype=scalar_dtypes()), # 2-D
        arrays(shape=array_shapes(min_dims=2), dtype=scalar_dtypes()) # M-D
    ))

    # Occasionally generate an `out` array of the expected result shape
    use_out = data.draw(st.booleans())
    if use_out:
        out_shape = np.dot(np.zeros_like(a), np.zeros_like(b)).shape
        out = np.zeros(out_shape, dtype=np.result_type(a, b))
        result = np.dot(a, b, out=out)
        assert result is out
    else:
        result = np.dot(a, b)

    # Check return type and shape
    if a.ndim <= 1 and b.ndim <= 1:
        assert np.isscalar(result)
    else:
        assert isinstance(result, np.ndarray)
        expected_shape = (*a.shape[:-1], *b.shape[:-2], b.shape[-1])
        assert result.shape == expected_shape

    # Check result values
    if np.isscalar(a) or np.isscalar(b):
        assert result == a * b
    else:
        assert np.allclose(result, np.matmul(a, b))

    # Check dimension mismatch raises ValueError
    if a.shape[-1] != b.shape[-2]:
        with pytest.raises(ValueError):
            np.dot(a, b)
# End program