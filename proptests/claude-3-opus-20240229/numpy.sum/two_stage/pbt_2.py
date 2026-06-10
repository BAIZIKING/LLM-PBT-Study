from hypothesis import given, strategies as st
import numpy as np

@given(st.arrays(dtype=np.float64, shape=st.integers(0, 5), elements=st.floats(-1e10, 1e10)))
def test_numpy_sum_shape(arr):
    axis = np.random.choice(list(range(arr.ndim)) + [None])
    result = np.sum(arr, axis=axis)
    if axis is None:
        assert np.isscalar(result)
    else:
        assert result.shape == np.delete(arr.shape, axis)

@given(st.arrays(dtype=np.float64, shape=0, elements=st.floats(-1e10, 1e10)), st.floats(-1e10, 1e10))
def test_numpy_sum_empty_array(arr, initial):
    result1 = np.sum(arr)
    result2 = np.sum(arr, initial=initial)
    assert result1 == 0
    assert result2 == initial

@given(st.arrays(dtype=np.float64, shape=st.integers(0, 5), elements=st.floats(-1e10, 1e10)),
       st.permutations(range(5)))
def test_numpy_sum_commutativity(arr, perm):
    axis = np.random.choice(list(range(arr.ndim)) + [None])
    result1 = np.sum(arr, axis=axis)
    result2 = np.sum(arr.transpose(perm), axis=axis)
    assert np.allclose(result1, result2)

@given(st.arrays(dtype=np.float64, shape=st.integers(0, 5), elements=st.floats(0, 1e10)))
def test_numpy_sum_nonnegative(arr):
    axis = np.random.choice(list(range(arr.ndim)) + [None])
    result = np.sum(arr, axis=axis)
    if axis is None:
        assert result >= np.max(arr)
    else:
        assert np.all(result >= np.max(arr, axis=axis))

@given(st.arrays(dtype=np.float64, shape=st.integers(0, 5), elements=st.floats(-1e10, 1e10)))
def test_numpy_sum_out_parameter(arr):
    axis = np.random.choice(list(range(arr.ndim)) + [None])
    out = np.zeros_like(arr)
    result = np.sum(arr, axis=axis, out=out)
    assert result is out
    assert np.allclose(result, np.sum(arr, axis=axis))
# End program