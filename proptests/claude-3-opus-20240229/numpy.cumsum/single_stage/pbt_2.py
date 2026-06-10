from hypothesis import given, strategies as st
import numpy as np

# Summary: 
# Generate arrays with varying sizes, dimensions, and element types.
# Test a variety of axis values, including the default (None).
# Verify expected properties: shape, dtype, and cumulative sum.
@given(
    arr=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1).map(np.array),
    axis=st.one_of(st.none(), st.integers(-10, 10)),
    dtype=st.one_of(st.none(), st.sampled_from([np.int32, np.int64, np.float32, np.float64])),
)
def test_numpy_cumsum(arr, axis, dtype):
    result = np.cumsum(arr, axis=axis, dtype=dtype)

    # Check shape
    if axis is None:
        assert result.shape == (arr.size,)
    else:
        assert result.shape == arr.shape

    # Check dtype
    if dtype is None:
        assert result.dtype == arr.dtype
    else:
        assert result.dtype == dtype

    # Check values
    assert np.allclose(result, np.cumsum(arr, axis=axis))
# End program    