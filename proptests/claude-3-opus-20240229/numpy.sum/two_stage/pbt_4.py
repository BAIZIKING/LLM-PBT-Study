from hypothesis import given, strategies as st
import numpy as np

@given(st.arrays(dtype=np.float64, shape=st.tuples(*[st.integers(min_value=0, max_value=10) for _ in range(4)]), elements=st.floats(allow_nan=False, allow_infinity=False)), st.none() | st.integers(-4, 3), st.booleans())
def test_numpy_sum_properties(arr, axis, keepdims):
    output = np.sum(arr, axis=axis, keepdims=keepdims)

    # Property 1
    if axis is None:
        assert np.isscalar(output)
    else:
        assert output.shape == tuple(dim for i, dim in enumerate(arr.shape) if i != axis)

    # Property 2
    assert np.sum(np.array([], dtype=arr.dtype)) == 0

    # Property 3
    assert np.sum(np.array([42], dtype=arr.dtype)) == 42
    assert np.sum(np.array([42], dtype=arr.dtype), axis=0) == 42

    # Property 4
    assert np.allclose(np.sum(arr), sum(arr.flatten()))

    # Property 5
    if keepdims:
        assert output.ndim == arr.ndim
        assert all(dim == 1 for i, dim in enumerate(output.shape) if i == axis)
    else:
        assert output.ndim == arr.ndim - 1
# End program