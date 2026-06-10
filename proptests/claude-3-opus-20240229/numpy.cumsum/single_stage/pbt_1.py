from hypothesis import given, strategies as st
import numpy as np

# Generate a variety of input arrays to test numpy.cumsum:
# - Use arrays with different dimensions (1D, 2D, 3D)
# - Test different dtypes (int, float, complex)
# - Include edge cases like empty arrays, arrays with inf/nan
# - Specify an axis to test along different dimensions
@given(st.data())
def test_numpy_cumsum(data):
    # Generate array shape (1D, 2D or 3D)
    shape = data.draw(st.lists(st.integers(min_value=0, max_value=10), min_size=1, max_size=3))
    
    # Generate input array dtype
    dtype = data.draw(st.sampled_from([int, float, complex]))
    
    # Allow some elements to be inf or nan
    allow_infinity = data.draw(st.booleans())
    allow_nan = data.draw(st.booleans())
    
    # Generate input array
    arr = data.draw(st.arrays(shape=shape, dtype=dtype, 
                              elements=st.floats(allow_infinity=allow_infinity, allow_nan=allow_nan)))
    
    # Select an axis to take cumsum along
    axis = data.draw(st.one_of(st.none(), st.integers(min_value=-len(shape), max_value=len(shape)-1)))
    
    # Take cumulative sum along specified axis
    result = np.cumsum(arr, axis=axis)
    
    # Check that result matches taking cumsum manually
    if axis is None:
        expected = np.array([np.sum(arr.flatten()[:i+1]) for i in range(arr.size)]).reshape(result.shape) 
    else:
        expected = np.apply_along_axis(lambda x: [np.sum(x[:i+1]) for i in range(len(x))], axis, arr)
    
    # For floats, allow small tolerance due to rounding errors
    if dtype is float or dtype is complex:
        np.testing.assert_allclose(result, expected)
    else:
        assert np.array_equal(result, expected)
# End program        