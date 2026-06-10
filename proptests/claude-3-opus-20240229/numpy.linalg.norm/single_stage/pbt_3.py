from hypothesis import given, strategies as st
import numpy as np

# Generate a variety of input arrays covering different shapes, dtypes and edge cases.
# Test different ord values, including non-zero int, inf, -inf, 'fro', 'nuc', and None.  
# If ord is None, restrict x to 1D or 2D arrays.
# Generate different axis values including None, int, and 2-tuple of ints.
# Toggle keepdims between True and False.
# Check the following properties:
# - norm should return a scalar for 1D vector input
# - norm should return an array of vector norms when axis=int 
# - norm should return an array of matrix norms when axis=2-tuple
# - norm result should broadcast with input when keepdims=True
# - for ord < 1, norm may not satisfy mathematical properties 
# - Frobenius norm is defined only for 2D matrices
# - nuclear norm is defined only for 2D matrices
@given(x=st.arrays(np.float, st.tuples(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10))),
       ord=st.one_of(st.integers().filter(lambda x: x != 0), st.just(np.inf), st.just(-np.inf), st.just('fro'), st.just('nuc'), st.none()),
       axis=st.one_of(st.none(), st.integers(min_value=-2, max_value=1), st.tuples(st.integers(min_value=-2, max_value=0), st.integers(min_value=-1, max_value=1))), 
       keepdims=st.booleans())
def test_norm(x, ord, axis, keepdims):
    if ord is None and x.ndim > 2:
        return
    if ord in ['fro', 'nuc'] and x.ndim != 2:
        return

    norm = np.linalg.norm(x, ord=ord, axis=axis, keepdims=keepdims)
    
    if axis is None:
        if x.ndim == 1:
            assert np.isscalar(norm)
        elif x.ndim == 2 and ord in [None, 'fro', 'nuc']:
            assert np.isscalar(norm)
    elif isinstance(axis, tuple):
        assert norm.ndim == x.ndim - len(axis)
    else:
        assert norm.ndim == x.ndim - 1
        
    if keepdims:
        assert norm.shape == tuple(1 if i in (axis if isinstance(axis, tuple) else [axis]) else d for i,d in enumerate(x.shape))
            
    if ord is not None and ord < 1:
        assert (norm >= 0).all()
# End program