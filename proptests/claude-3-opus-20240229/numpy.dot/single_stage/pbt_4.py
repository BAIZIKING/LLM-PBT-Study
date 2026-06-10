from hypothesis import given, strategies as st
import numpy as np

# Summary: Generate a wide variety of input arrays to test numpy.dot
# - Generate 1D, 2D, and higher dimensional arrays 
# - Test with different dtypes like int, float, complex
# - Generate arrays with varying sizes (including 0, 1) and shapes
# - Generate scalar values (0D arrays)
# - Use the `out` parameter to specify output array
@given(st.data())
def test_numpy_dot(data):
    # Generate a and b as either scalars or arrays
    a = data.draw(st.one_of(st.integers(), st.floats(allow_nan=False, allow_infinity=False), 
                            st.complex_numbers(), st.arrays(np.int8, st.integers(0, 5), st.integers(1, 3)),
                            st.arrays(np.int16, st.integers(0, 5), st.integers(1, 3)), 
                            st.arrays(np.int32, st.integers(0, 5), st.integers(1, 3)),
                            st.arrays(np.int64, st.integers(0, 5), st.integers(1, 3)), 
                            st.arrays(np.float32, st.integers(0, 5), st.integers(1, 3)),
                            st.arrays(np.float64, st.integers(0, 5), st.integers(1, 3)), 
                            st.arrays(np.complex64, st.integers(0, 5), st.integers(1, 3)),
                            st.arrays(np.complex128, st.integers(0, 5), st.integers(1, 3))))
    
    b = data.draw(st.one_of(st.integers(), st.floats(allow_nan=False, allow_infinity=False),
                            st.complex_numbers(), st.arrays(np.int8, st.integers(0, 5), st.integers(1, 3)), 
                            st.arrays(np.int16, st.integers(0, 5), st.integers(1, 3)),
                            st.arrays(np.int32, st.integers(0, 5), st.integers(1, 3)), 
                            st.arrays(np.int64, st.integers(0, 5), st.integers(1, 3)),
                            st.arrays(np.float32, st.integers(0, 5), st.integers(1, 3)), 
                            st.arrays(np.float64, st.integers(0, 5), st.integers(1, 3)),
                            st.arrays(np.complex64, st.integers(0, 5), st.integers(1, 3)), 
                            st.arrays(np.complex128, st.integers(0, 5), st.integers(1, 3))))
    
    # Optionally generate an output array
    use_out = data.draw(st.booleans())
    if use_out:
        out = np.empty(np.broadcast(a, b).shape, dtype=np.result_type(a, b))
        result = np.dot(a, b, out=out)
        assert out is result
    else:
        result = np.dot(a, b)
    
    # Check properties based on spec
    if np.isscalar(a) or np.isscalar(b):
        assert result == a * b
    else:
        if a.ndim == 1 and b.ndim == 1:
            assert result == np.inner(a, b)
        elif a.ndim == 2 and b.ndim == 2:
            assert result == a @ b
        else:
            assert result.shape == np.broadcast(a[...,np.newaxis], b).shape[:-1]
# End program