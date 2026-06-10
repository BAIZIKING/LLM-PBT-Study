from hypothesis import given, strategies as st
import numpy as np

# Summary: 
# Generate a variety of shapes and data types for input array x
# Draw ord from a strategy including valid int, inf, -inf, 'fro', 'nuc', None 
# Draw axis from a strategy including valid int, 2-tuple of ints, None
# Draw keepdims from booleans()
# Check that output is a scalar for 1D vector norms
# Check that output is a 1D array for vector norms over an axis
# Check that output is a scalar for matrix norms
# Check that output is non-negative
# Check that invalid ord raises ValueError for > 2D arrays
# Check that invalid axis raises np.AxisError
# Check that output has expected shape when keepdims=True
@given(x=st.arrays(dtype=st.one_of(st.integer_dtypes(), st.floating_dtypes(), st.complex_number_dtypes()), 
                   shape=st.one_of(st.integers(1, 5), st.tuples(st.integers(1, 5), st.integers(1, 5))), 
                   elements=st.floats(-100, 100)),
       ord=st.one_of(st.just(None), st.sampled_from([None, 'fro', 'nuc', np.inf, -np.inf, 1, -1, 2, -2]), 
                     st.integers(-10, 10).filter(lambda x: x != 0)),
       axis=st.one_of(st.none(), st.integers(-2, 1), 
                      st.tuples(st.integers(-2, 1), st.integers(-2, 1)).filter(lambda x: len(set(x)) == 2)),
       keepdims=st.booleans())
def test_numpy_linalg_norm(x, ord, axis, keepdims):
    #catch unsupported ord for > 2d
    try:
        result = np.linalg.norm(x, ord=ord, axis=axis, keepdims=keepdims)
    except ValueError:
        assert (ord in ('nuc', 'fro') or ord == None) and x.ndim > 2
        return
    
    #check result is scalar for 1d vector norm
    if axis is None and x.ndim == 1:
        assert np.isscalar(result)
    elif axis is not None and isinstance(axis, int):
        #check 1d output for vector norm over an axis
        assert result.ndim == 1
        #check keepdims
        if keepdims:
            assert result.shape[axis] == 1
        else:
            assert result.shape[axis] == x.shape[axis]
    elif axis is None and x.ndim == 2:
        #check scalar output for matrix norm
        assert np.isscalar(result)

    #check non-negative 
    assert result >= 0
    
    #check keepdims
    if keepdims:
        assert result.shape == tuple(1 if i in ((axis,) if isinstance(axis, int) else axis) else d for i,d in enumerate(x.shape))
    
# End program