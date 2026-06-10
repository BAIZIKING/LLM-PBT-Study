from hypothesis import given, strategies as st
import numpy as np

# Generate a wide variety of inputs for numpy.sum, including:
# - Different array shapes and sizes
# - Different data types (int, float)
# - Different axis values (None, int, tuple of ints)
# - Test keepdims parameter
# - Test initial parameter
# - Test where parameter with boolean mask
#
# Properties to test:
# - If axis is None, output is a scalar
# - If axis is an int, output has same shape as input with axis removed
# - If axis is a tuple, output has same shape as input with each axis removed
# - keepdims parameter leaves reduced axes in result with size 1
# - initial parameter adds to the sum
# - where parameter only includes elements where the mask is True
# - The sum of an empty array is 0
@given(st.data())
def test_numpy_sum(data):
    shape = data.draw(st.lists(st.integers(0, 5), min_size=0, max_size=3))
    dtype = data.draw(st.sampled_from([int, float]))
    a = data.draw(st.arrays(dtype=dtype, shape=shape))
    
    axis_strategy = st.none() | st.integers(-len(shape), len(shape)-1) | st.lists(st.integers(-len(shape), len(shape)-1), max_size=len(shape))
    axis = data.draw(axis_strategy)
    
    keepdims = data.draw(st.booleans())
    initial = data.draw(st.integers(-100, 100))
    
    where_mask = data.draw(st.arrays(bool, shape=shape))
    
    result = np.sum(a, axis=axis, keepdims=keepdims, initial=initial, where=where_mask)
    
    if axis is None:
        assert np.isscalar(result)
    elif isinstance(axis, int):
        assert result.shape == np.delete(a.shape, axis) 
    else:
        for ax in axis:
            a = np.sum(a, axis=ax, keepdims=True)
        assert result.shape == a.shape
        
    if keepdims:
        if axis is None:
            assert result.shape == (1,) * a.ndim
        elif isinstance(axis, int):
            assert result.shape[axis] == 1
        else:
            for ax in axis:
                assert result.shape[ax] == 1
    
    assert np.sum(a, where=where_mask, initial=0) + initial == np.sum(a, where=where_mask, initial=initial)
    
    assert np.sum([], initial=0) == 0
# End program