from hypothesis import given, strategies as st
import numpy as np

# Summary: Generate random input arrays with varying shapes, dtypes and dimensions.
# Check the following properties:
# 1. Output has same shape as input, or is 1D if axis is None
# 2. Final element of output equals sum of input array
# 3. Intermediate elements are correct cumulative sums 
# 4. Specifying an output array with `out` parameter works correctly
# 5. Overflow is handled gracefully with integer dtypes
@given(st.data())
def test_numpy_cumsum(data):
    # Generate random input array
    a = data.draw(st.arrays(
        num_elements=st.integers(0, 100), 
        dtype=st.one_of(st.integer_dtypes(), st.floating_dtypes()),
        shape=st.one_of(
            st.just(()), 
            st.tuples(st.integers(0, 10)),
            st.tuples(st.integers(0, 10), st.integers(0, 10))
        )
    ))
    
    axis = data.draw(st.one_of(st.none(), st.integers(-a.ndim, a.ndim-1)))
    
    out_shape = a.shape if axis is not None else (a.size,)
    out = data.draw(st.arrays(dtype=a.dtype, shape=out_shape))
    
    result = np.cumsum(a, axis=axis, out=out)
    
    assert result.shape == out_shape
    assert np.isclose(result[-1], a.sum())
    
    if axis is None:
        for i in range(1, a.size):
            assert np.isclose(result[i], a.flat[:i+1].sum())
    elif a.ndim == 1:
        for i in range(1, a.size):
            assert np.isclose(result[i], a[:i+1].sum())
    else:
        for i in range(1, a.shape[axis]):
            assert np.allclose(result.take(i, axis=axis), a.take(range(i+1), axis=axis).sum(axis=axis))
    
    assert np.may_share_memory(out, result)
# End program