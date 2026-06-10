from hypothesis import given, strategies as st
import numpy as np

# Generate a wide variety of array shapes, dimensions, and data types.
# Include edge cases like empty arrays, 1-element arrays, and large arrays.
# Draw from all valid dtypes including integer, float, and complex.
# Test axis=None and all valid axis values for different dimensionalities. 
@given(st.data())
def test_numpy_cumsum(data):
    shape = data.draw(st.lists(st.integers(min_value=0, max_value=10), min_size=0, max_size=5))
    dtype = data.draw(st.sampled_from([np.int8, np.int16, np.int32, np.int64,
                                       np.uint8, np.uint16, np.uint32, np.uint64,
                                       np.float16, np.float32, np.float64,
                                       np.complex64, np.complex128]))
    
    a = data.draw(st.arrays(dtype=dtype, shape=shape))
    axis = data.draw(st.none() | st.integers(-len(shape), len(shape)-1))

    cumsum = np.cumsum(a, axis=axis)
    
    # Check that cumsum has the expected shape
    if axis is None:
        assert cumsum.shape == (np.prod(shape),)
    else:
        assert cumsum.shape == a.shape
    
    # Check that the final cumsum element equals sum
    assert cumsum.ravel()[-1] == np.sum(a)
    
    # Check that cumsum over an axis equals cumsum over flattened sub-arrays
    if axis is not None:
        assert np.all(cumsum == np.apply_along_axis(np.cumsum, axis, a))

    # Check dtypes match, unless an integer dtype with 
    # less precision than default int was provided
    if dtype not in (np.int8, np.int16, np.uint8, np.uint16):
        assert cumsum.dtype == np.result_type(dtype)
        
# End program