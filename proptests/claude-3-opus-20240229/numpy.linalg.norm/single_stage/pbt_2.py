from hypothesis import given, strategies as st
import numpy as np

# Summary: 
# Generate random numpy arrays of various shapes (1D, 2D, 3D), data types, and values. 
# Test different ord values, including None, 'fro', 'nuc', np.inf, -np.inf, 1, -1, 2, -2.
# Test different axis values, including None, int, (int, int).
# Check that norm always returns a non-negative value.
# Check that norm of all zero vector/matrix is 0.  
# Check that multiplying vector/matrix by a scalar c, multiplies norm by abs(c).
# Check that norm is invariant under unitary transforms.
@given(
    arr=st.arrays(
        dtype=st.one_of(
            st.just(np.float32), st.just(np.float64), 
            st.just(np.int32), st.just(np.int64)
        ),
        shape=st.one_of(
            st.integers(min_value=1, max_value=100),
            st.tuples(st.integers(1, 100), st.integers(1, 100)), 
            st.tuples(st.integers(1, 10), st.integers(1, 10), st.integers(1, 10))
        ),
        elements=st.floats(allow_nan=False, allow_infinity=False),
    ),
    ord=st.one_of(
        st.none(), st.just('fro'), st.just('nuc'), 
        st.just(np.inf), st.just(-np.inf),
        st.integers(min_value=1, max_value=5), st.integers(min_value=-5, max_value=-1)
    ),
    axis=st.one_of(st.none(), st.integers(-3, 3), st.tuples(st.integers(-3, 3), st.integers(-3, 3))), 
    keepdims=st.booleans(),
)
def test_norm(arr, ord, axis, keepdims):
    norm = np.linalg.norm(arr, ord=ord, axis=axis, keepdims=keepdims)
    
    # norm is always non-negative
    assert norm >= 0
    
    # norm of zero vector/matrix is 0
    assert np.linalg.norm(np.zeros_like(arr), ord=ord, axis=axis, keepdims=keepdims) == 0
    
    # scaling vector/matrix by c, scales norm by abs(c)
    c = np.random.randn() 
    assert np.allclose(
        np.linalg.norm(c*arr, ord=ord, axis=axis, keepdims=keepdims),
        abs(c)*np.linalg.norm(arr, ord=ord, axis=axis, keepdims=keepdims)
    )
    
    if arr.ndim == 2 and axis is None and ord in (None, 2, -2):
        # invariant under unitary transforms
        q, _ = np.linalg.qr(np.random.randn(*arr.shape))
        assert np.allclose(
            np.linalg.norm(arr, ord=ord, axis=axis, keepdims=keepdims),
            np.linalg.norm(arr @ q, ord=ord, axis=axis, keepdims=keepdims)
        )
# End program        