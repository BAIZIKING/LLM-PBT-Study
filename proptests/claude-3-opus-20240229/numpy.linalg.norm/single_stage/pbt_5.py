from hypothesis import given, strategies as st
import numpy as np

# Summary: Generate a wide variety of array shapes, data types and norms to test.
# Inputs generated include: 1-D and 2-D arrays, different numeric data types (int, float, complex), 
# arrays with inf/nan values, empty arrays, a variety of norm orders (1, 2, inf, -inf, 'fro', 'nuc'), 
# testing both with and without the axis and keepdims parameters.
# Properties to check: 
# - norm should always be >= 0
# - norm of all 0s should be 0  
# - norm of identity matrix should be 1 for 2-norm, Frobenius norm
# - norm is invariant to multiplying vector by -1
# - Frobenius norm and 'nuc' norm orders only work on 2-D matrices
# - 2-norm of vector is equivalent to direct sqrt(sum(x^2)) calculation
@given(st.data())
def test_numpy_linalg_norm(data):
    # Generate array
    x = data.draw(st.one_of(
            st.lists(st.floats(allow_infinity=True, allow_nan=True), min_size=0, max_size=10), 
            st.lists(st.lists(st.floats(allow_infinity=True, allow_nan=True), min_size=0, max_size=5), min_size=0, max_size=5)
        ))
    x = np.array(x)
    
    # Generate other parameters  
    ord = data.draw(st.one_of(st.none(), st.integers(-3,3), st.sampled_from([np.inf, -np.inf, 'fro', 'nuc'])))
    axis = data.draw(st.one_of(st.none(), st.integers(0, x.ndim-1), 
                               st.tuples(st.integers(0, x.ndim-1), st.integers(0, x.ndim-1))))
    keepdims = data.draw(st.booleans())

    xnorm = np.linalg.norm(x, ord=ord, axis=axis, keepdims=keepdims)
    
    # Check properties
    assert np.all(xnorm >= 0)  # norm is always non-negative
    
    if np.all(x == 0):
        assert np.all(xnorm == 0)  # norm of 0s is 0
        
    if x.ndim == 2 and np.array_equal(x, np.eye(x.shape[0])):
        if ord == 2 or ord == 'fro':
            assert np.allclose(xnorm, 1)  # norm of identity is 1
            
    assert np.allclose(xnorm, np.linalg.norm(-x, ord=ord, axis=axis, keepdims=keepdims))  # norm is invariant to sign
    
    if ord in ['fro', 'nuc'] and x.ndim != 2:
        assert isinstance(xnorm, ValueError)  # Frobenius and nuc norm only work on 2D
        
    if ord == 2 and axis is None and x.ndim == 1:
        assert np.allclose(xnorm, np.sqrt(np.sum(np.abs(x)**2))) # 2-norm is sqrt of sum of squares
        
# End program