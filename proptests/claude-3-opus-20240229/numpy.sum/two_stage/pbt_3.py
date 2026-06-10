from hypothesis import given, strategies as st
import numpy as np

@given(st.arrays(st.floats(allow_nan=False, allow_infinity=False), shape=st.tuples(*[st.integers(0, 5) for _ in range(4)])))
def test_numpy_sum_output_shape(arr):
    axis = st.integers(0, arr.ndim - 1).example()
    result = np.sum(arr, axis=axis)
    assert result.shape == tuple(dim for i, dim in enumerate(arr.shape) if i != axis)

    result_none_axis = np.sum(arr)
    assert np.isscalar(result_none_axis)

@given(st.arrays(st.floats(allow_nan=False, allow_infinity=False), shape=st.tuples(*[st.integers(0, 0) for _ in range(4)])))
def test_numpy_sum_empty_array(arr):
    assert np.sum(arr) == 0
    assert np.sum(arr, dtype=np.float32) == 0
    assert np.sum(arr, dtype=np.int32) == 0

@given(st.arrays(st.floats(allow_nan=False, allow_infinity=False), shape=st.tuples(*[st.integers(1, 1) for _ in range(4)])))
def test_numpy_sum_single_element(arr):
    for axis in range(arr.ndim):
        assert np.sum(arr, axis=axis) == arr

@given(st.arrays(st.floats(allow_nan=False, allow_infinity=False), shape=st.tuples(*[st.integers(0, 5) for _ in range(4)])),
       st.arrays(st.booleans(), shape=st.tuples(*[st.integers(0, 5) for _ in range(4)])))
def test_numpy_sum_where(arr, where):
    where = where[tuple(slice(None, dim) for dim in arr.shape)]
    assert np.sum(arr, where=where) <= np.sum(arr)

@given(st.arrays(st.floats(allow_nan=False, allow_infinity=False), shape=st.tuples(*[st.integers(0, 5) for _ in range(4)])))
def test_numpy_sum_keepdims(arr):
    for axis in range(arr.ndim):
        result_keepdims = np.sum(arr, axis=axis, keepdims=True)
        assert result_keepdims.shape == tuple(1 if i == axis else dim for i, dim in enumerate(arr.shape))

        result_no_keepdims = np.sum(arr, axis=axis, keepdims=False)
        assert result_no_keepdims.shape == tuple(dim for i, dim in enumerate(arr.shape) if i != axis)
# End program