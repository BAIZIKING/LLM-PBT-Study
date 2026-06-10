from hypothesis import given, strategies as st
import numpy as np

@given(st.data())
def test_output_shape(data):
    shape = data.draw(st.lists(st.integers(min_value=0, max_value=10), min_size=1, max_size=5))
    axis = data.draw(st.none() | st.integers(-len(shape), len(shape) - 1))
    arr = data.draw(st.arrays(np.float64, shape, elements=st.floats(-1e10, 1e10)))
    
    output = np.sum(arr, axis=axis)
    
    if axis is None:
        assert np.isscalar(output)
    else:
        assert output.shape == np.delete(arr.shape, axis)

@given(st.data())
def test_sum_reversed(data):
    shape = data.draw(st.lists(st.integers(min_value=0, max_value=10), min_size=1, max_size=5))
    axis = data.draw(st.integers(0, len(shape) - 1))
    arr = data.draw(st.arrays(np.float64, shape, elements=st.floats(-1e10, 1e10)))
    
    assert np.sum(arr, axis=axis) == np.sum(np.flip(arr, axis=axis), axis=axis)

@given(st.data())
def test_sum_flattened(data):
    shape = data.draw(st.lists(st.integers(min_value=0, max_value=10), min_size=1, max_size=5))
    axis = data.draw(st.integers(0, len(shape) - 1))
    arr = data.draw(st.arrays(np.float64, shape, elements=st.floats(-1e10, 1e10)))
    
    assert np.sum(arr, axis=axis) == np.sum(arr.flatten())

@given(st.data())
def test_sum_empty(data):
    shape = data.draw(st.lists(st.integers(min_value=0, max_value=10), min_size=0, max_size=5))
    initial = data.draw(st.floats(-1e10, 1e10))
    arr = np.zeros(shape)
    
    assert np.sum(arr) == 0
    assert np.sum(arr, initial=initial) == initial

@given(st.data())
def test_keepdims(data):
    shape = data.draw(st.lists(st.integers(min_value=0, max_value=10), min_size=1, max_size=5))
    axis = data.draw(st.integers(0, len(shape) - 1))
    keepdims = data.draw(st.booleans())
    arr = data.draw(st.arrays(np.float64, shape, elements=st.floats(-1e10, 1e10)))
    
    output = np.sum(arr, axis=axis, keepdims=keepdims)
    
    if keepdims:
        assert len(output.shape) == len(arr.shape)
        assert output.shape[axis] == 1
    else:
        assert len(output.shape) == len(arr.shape) - 1
# End program