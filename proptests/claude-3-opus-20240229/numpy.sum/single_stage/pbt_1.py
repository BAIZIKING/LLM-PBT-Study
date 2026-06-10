from hypothesis import given, strategies as st
import numpy as np

# Generate a wide variety of inputs, including:
# - Different array shapes and sizes
# - Different integer and floating-point dtypes 
# - Negative, zero, and positive values
# - Arrays with NaNs and infinities
# - Different axis values (within valid range based on array shape)
# - Passing an initial value
# - Arrays with boolean masks
@given(
    a=st.arrays(
        shape=st.tuples(st.integers(0, 5), st.integers(0, 5)), 
        dtype=st.one_of(st.just(np.int8), st.just(np.int16), st.just(np.int32), st.just(np.int64),
                        st.just(np.uint8), st.just(np.uint16), st.just(np.uint32), st.just(np.uint64), 
                        st.just(np.float16), st.just(np.float32), st.just(np.float64)),
        elements=st.one_of(st.integers(-100, 100), st.floats(-100, 100), 
                           st.just(np.nan), st.just(np.inf), st.just(-np.inf))
    ),
    axis=st.one_of(st.none(), st.integers(-5, 5), st.tuples(st.integers(-5, 5), st.integers(-5, 5))),
    initial=st.one_of(st.none(), st.integers(-100, 100), st.floats(-100, 100)),
    where=st.one_of(st.none(), st.arrays(shape=st.tuples(st.integers(0, 5), st.integers(0, 5)), dtype=bool))
)
def test_numpy_sum(a, axis, initial, where):
    result = np.sum(a, axis=axis, initial=initial, where=where)
    
    # Check that the result is a scalar if axis is None, otherwise an array
    if axis is None:
        assert np.isscalar(result)
    else:
        assert isinstance(result, np.ndarray)
    
    # Check that specifying an initial value offsets the sum by that amount
    if initial is not None:
        assert np.allclose(result, np.sum(a, axis=axis, where=where) + initial)
    
    # Check that elements are included/excluded based on the where mask
    if where is not None:
        assert np.allclose(result, np.sum(np.where(where, a, 0), axis=axis))

    # Check that integer overflow is handled (sum wraps around)
    if np.issubdtype(a.dtype, np.integer):
        assert np.allclose(result, np.sum(a.astype(np.int64), axis=axis, where=where).astype(a.dtype))
    
    # Check that NaNs propagate
    if np.any(np.isnan(a)):
        assert np.isnan(result).any()
        
# End program