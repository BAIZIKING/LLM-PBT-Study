from hypothesis import given, strategies as st
import numpy as np
import numpy.testing as npt

@given(st.data())
def test_numpy_cumsum(data):
    dtype= data.draw(st.sampled_from([np.int32, np.int64, np.float32, np.float64]))
    
    a = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100).map(lambda x: np.array(x, dtype=dtype)))
    
    axis = data.draw(st.integers(min_value=-a.ndim, max_value=a.ndim-1) | st.none())

    # Calculate cumulative sum
    cumsum_arr = np.cumsum(a, axis=axis)

    if axis is None or a.ndim == 1:
        # If axis is not specified or input array is 1D then cumsum_arr must have the same shape as a
        assert cumsum_arr.shape == a.shape
    else:
        # If axis is specified cumsum_arr must have the specified axis length equal to input array
        assert cumsum_arr.shape[axis] == a.shape[axis]
    
    # dtype of cumsum_arr and a should be same
    assert cumsum_arr.dtype == a.dtype

    # creating output array
    out_arr = np.empty(100, dtype=dtype)
    out_arr = np.cumsum(a, out=out_arr)
    
    # both arrays should be same
    npt.assert_array_equal(out_arr, cumsum_arr)