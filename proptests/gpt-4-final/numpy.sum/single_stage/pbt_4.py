from hypothesis import given, strategies as st
import numpy as np

# A test that generates a variety of numpy arrays and tests the validity of numpy.sum
@given(st.data())
def test_numpy_sum(data):

    # Draw arrays of int, float, and bool values
    array = data.draw(st.one_of(
        st.arrays(dtype=np.int32, shape=data.draw(st.tuples(st.integers(0,20), st.integers(0,20)))),
        st.arrays(dtype=np.float32, shape=data.draw(st.tuples(st.integers(0,20), st.integers(0,20)))),
        st.arrays(dtype=bool, shape=data.draw(st.tuples(st.integers(0,20), st.integers(0,20))))
    ))

    # Draw an axis parameter with a chance for None
    axis = data.draw(st.one_of(st.integers(-array.ndim, array.ndim-1), st.none()))

    # Draw a dtype parameter with a chance for None
    dtype = data.draw(st.one_of(st.sampled_from([np.int32, np.float32]), st.none()))

    # Draw a keepdims parameter
    keepdims = data.draw(st.booleans())

    # Draw an initial parameter with a chance for None
    initial = data.draw(st.one_of(st.floats(allow_nan=False, allow_infinity=False), st.none()))
    
    # Test sum functionality
    result = np.sum(array, axis=axis, dtype=dtype, keepdims=keepdims, initial=initial)
    
    # Check correct sum
    if dtype is not None:
        # dtype will affect the precision of the result
        assert result.dtype == dtype
        
    if initial is not None:
        # the initial value should be included in the output
        assert result >= initial
        
    if keepdims:
        # if keepdims is True, the result should still have the input number of dimensions
        assert result.ndim == array.ndim
    else:
        # otherwise, one dimension should be reduced, unless a sum over the whole array was taken
        assert result.ndim == array.ndim - 1 if axis is not None else 0
# End program