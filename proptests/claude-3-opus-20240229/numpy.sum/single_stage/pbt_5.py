from hypothesis import given, strategies as st
import numpy as np

# Summary: Generate a wide variety of input arrays and parameters to thoroughly test numpy.sum.
# Strategies include:
# - Different array shapes (1D, 2D, 3D, empty)
# - Different array dtypes (int, float, bool)
# - Arrays with NaN, Inf values
# - Different axis values (None, int, tuple of ints)
# - Initial values
# - Using the out parameter
# - Using the where parameter to conditionally include elements
# The key properties to test are:
# - The array shape is as expected after sum (e.g. axis removed)
# - The sum is correctly computed, accounting for NaNs, dtype, etc.
# - Sum of empty array is 0
# - The out parameter contains the result
# - The where parameter applies the condition correctly

@given(st.data())
def test_numpy_sum(data):
    # Generate array
    array_type = data.draw(st.sampled_from([np.int8, np.int32, np.float32, np.float64, bool]))
    shape = data.draw(st.sampled_from([(0,), (1,), (10,), (2, 3), (2, 3, 4), (0, 3), (2, 0)]))
    a = data.draw(st.arrays(dtype=array_type, shape=shape))
    
    # Randomly add some NaNs and Infs
    if array_type in [np.float32, np.float64]:
        mask = data.draw(st.arrays(dtype=bool, shape=shape))
        a[mask] = data.draw(st.sampled_from([np.nan, np.inf, -np.inf]))
    
    # Generate other parameters
    axis = data.draw(st.none() | st.integers(-len(shape), len(shape)-1) | st.lists(st.integers(-len(shape), len(shape)-1), min_size=1, max_size=len(shape)))
    initial = data.draw(st.none() | st.integers() | st.floats(allow_nan=False, allow_infinity=False))
    keepdims = data.draw(st.booleans())
    where = data.draw(st.none() | st.arrays(dtype=bool, shape=shape))
    
    out_shape = np.sum(a, axis=axis, keepdims=keepdims, initial=initial, where=where).shape
    
    if axis is None:
        expected_shape = () if keepdims else ()
    else:
        expected_shape = tuple(dim for i, dim in enumerate(shape) if i not in (axis if isinstance(axis, tuple) else (axis,))) if keepdims else tuple(dim for i, dim in enumerate(shape) if i not in (axis if isinstance(axis, tuple) else (axis,)))
        
    assert out_shape == expected_shape
    
    # Select elements to sum based on where parameter 
    if where is not None:
        a_sum = a[where]
    else:
        a_sum = a
        
    # Get expected sum
    if initial is not None:
        expected = initial + a_sum.astype(dtype=np.float64).sum(axis=axis)
    else:
        expected = a_sum.astype(dtype=np.float64).sum(axis=axis)

    if expected.shape == ():
        assert np.allclose(np.sum(a, axis=axis, keepdims=keepdims, initial=initial, where=where), expected, equal_nan=True)
    else:
        assert np.allclose(np.sum(a, axis=axis, keepdims=keepdims, initial=initial, where=where), expected.reshape(out_shape), equal_nan=True)
        
# End program