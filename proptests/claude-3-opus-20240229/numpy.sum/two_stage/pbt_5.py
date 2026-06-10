from hypothesis import given, strategies as st
import numpy as np

@given(st.data())
def test_numpy_sum_shape(data):
    shape = data.draw(st.lists(st.integers(min_value=0, max_value=10), min_size=1, max_size=5))
    array = data.draw(st.arrays(np.float64, shape=shape))
    axis = data.draw(st.none() | st.integers(-len(shape), len(shape) - 1))
    
    result = np.sum(array, axis=axis)
    if axis is None:
        assert np.isscalar(result)
    else:
        assert result.shape == tuple(dim for i, dim in enumerate(shape) if i != axis)

@given(st.data())
def test_numpy_sum_inverse(data):
    array = data.draw(st.arrays(np.float64, shape=st.lists(st.integers(0, 10), min_size=1, max_size=5)))
    
    result = np.sum(array) + np.sum(-array)
    assert np.isclose(result, 0.0)

@given(st.data())
def test_numpy_sum_keepdims(data):
    shape = data.draw(st.lists(st.integers(min_value=0, max_value=10), min_size=1, max_size=5))
    array = data.draw(st.arrays(np.float64, shape=shape))
    axis = data.draw(st.integers(-len(shape), len(shape) - 1))
    
    result = np.sum(array, axis=axis, keepdims=True)
    assert result.shape == tuple(1 if i == axis else dim for i, dim in enumerate(shape))

@given(st.data())
def test_numpy_sum_empty(data):
    array = data.draw(st.arrays(np.float64, shape=st.just((0,))))
    
    result = np.sum(array)
    assert result == 0.0

@given(st.data())
def test_numpy_sum_initial(data):
    array = data.draw(st.arrays(np.float64, shape=st.lists(st.integers(0, 10), min_size=0, max_size=5)))
    initial = data.draw(st.floats())
    
    result = np.sum(array, initial=initial)
    assert np.isclose(result, np.sum(array) + initial)
# End program