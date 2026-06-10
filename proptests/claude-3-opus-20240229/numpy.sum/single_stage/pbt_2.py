from hypothesis import given, strategies as st
import numpy as np

# Summary: Generate a wide variety of array inputs to test numpy.sum.
# Strategies include generating arrays of different dimensions (0-d to 3-d),
# different data types (int, float), testing edge cases like empty arrays, 
# nan values, and specifying different axis values. Properties to check 
# include the return type matches the input dtype or default int/float, 
# the shape is reduced along the specified axis or a scalar is returned, 
# and overflow is handled for integer types.
@given(st.data())
def test_numpy_sum(data):
    # Generate array with random shape and dtype
    shape = data.draw(st.lists(st.integers(min_value=0, max_value=5), min_size=0, max_size=3))
    dtype = data.draw(st.sampled_from([int, float, np.int8, np.int32, np.float32, np.float64]))
    arr = data.draw(st.arrays(dtype=dtype, shape=shape))
    
    # Randomly add nan values for float types
    if np.issubdtype(arr.dtype, np.floating):
        mask = data.draw(st.arrays(dtype=bool, shape=arr.shape))
        arr[mask] = np.nan
    
    # Generate axis, keepdims, initial, where parameters
    axis = data.draw(st.none() | st.integers(-arr.ndim, arr.ndim-1) | 
                     st.lists(st.integers(-arr.ndim, arr.ndim-1), unique=True))
    keepdims = data.draw(st.booleans())
    initial = data.draw(st.integers() | st.floats(allow_nan=False))
    where = data.draw(st.none() | st.arrays(bool, shape=arr.shape))
    
    result = np.sum(arr, axis=axis, keepdims=keepdims, initial=initial, where=where)
    
    # Check result dtype matches expected
    if dtype in [int, np.int8, np.int32]:
        assert np.issubdtype(result.dtype, np.signedinteger)
    elif dtype in [float, np.float32, np.float64]:
        assert np.issubdtype(result.dtype, np.floating)
    
    # Check shape matches expected
    if axis is None:
        assert result.ndim == 0
    elif isinstance(axis, int):
        assert result.shape == arr.shape[:axis] + arr.shape[axis+1:] 
    else:
        assert result.shape == tuple(dim for i,dim in enumerate(arr.shape) if i not in axis)
    
    if keepdims:
        assert result.ndim == arr.ndim
        
    # Check overflow handled for integer types
    if arr.dtype == np.int8:
        assert np.all(result >= -128) and np.all(result <= 127)
        
    if arr.dtype == np.int32:
        assert np.all(result >= -2**31) and np.all(result <= 2**31-1)
        
# End program        