from hypothesis import given, strategies as st
import numpy as np

# Summary: 
# Generate a variety of input types and shapes for a and b:
# - Scalars (integers, floats, complex numbers)
# - 1D arrays of various lengths
# - 2D arrays of various shapes
# - ND arrays of various shapes
# Choose a range of values that includes 0, positive, and negative numbers.
# Optionally generate an out array with a matching shape and dtype.
# Verify properties:
# - Result is scalar if a and b are scalars or 1D
# - Result shape matches matrix multiplication rules 
# - Result values match explicit sum of products calculation
# - If out array is supplied, it is returned as result
# - Raises ValueError if dimension mismatch

@given(st.data())
def test_numpy_dot(data):
    # Generate scalar or array inputs
    a = data.draw(st.one_of(
        st.integers(-100, 100), 
        st.floats(-100, 100),
        st.complex_numbers(-100, 100),
        st.lists(st.floats(-100, 100), min_size=1, max_size=100).map(np.array),
        st.lists(st.lists(st.floats(-100, 100), min_size=1, max_size=10), min_size=1, max_size=10).map(np.array),
        arrays(np.float64, (data.draw(st.integers(1, 5)), data.draw(st.integers(1, 5)), data.draw(st.integers(1, 5))), elements=st.floats(-100, 100))
    ))
    b = data.draw(st.one_of(
        st.integers(-100, 100),
        st.floats(-100, 100), 
        st.complex_numbers(-100, 100),
        st.lists(st.floats(-100, 100), min_size=1, max_size=100).map(np.array),
        st.lists(st.lists(st.floats(-100, 100), min_size=1, max_size=10), min_size=1, max_size=10).map(np.array),
        arrays(np.float64, (data.draw(st.integers(1, 5)), data.draw(st.integers(1, 5)), data.draw(st.integers(1, 5))), elements=st.floats(-100, 100))
    ))
    
    # Optionally generate a compatible out array 
    use_out = data.draw(st.booleans())
    if use_out:
        out = np.zeros(np.broadcast(a, b).shape)
    else:
        out = None
    
    # Check result properties
    result = np.dot(a, b, out=out)

    if np.isscalar(a) and np.isscalar(b):
        assert np.isscalar(result)
        assert result == a * b
    elif a.ndim == 1 and b.ndim == 1:
        assert result.ndim == 0
        assert result == np.inner(a, b)
    elif a.ndim == 2 and b.ndim == 2:
        assert result.shape == (a.shape[0], b.shape[1])
        assert np.allclose(result, a @ b)
    elif b.ndim == 1:
        assert result.shape == a.shape[:-1] 
        assert np.allclose(result, np.sum(a * b, axis=-1))
    else:
        assert result.shape == a.shape[:-1] + b.shape[:-2] + b.shape[-1:]
        sum_of_products = np.sum(a[...,np.newaxis] * b[...,np.newaxis,:].swapaxes(-3,-2), axis=-1)
        assert np.allclose(result, sum_of_products)

    if out is not None:
        assert result is out
        
    # Check dimension mismatch raises ValueError 
    if a.shape[-1] != b.shape[-2]:
        with pytest.raises(ValueError):
            np.dot(a, b)
        
# End program