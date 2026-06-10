from hypothesis import given, strategies as st
import numpy as np

@given(
    a=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100).map(np.array),
    b=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100).map(np.array),
    out=st.none() | st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100).map(np.array)
)
def test_numpy_dot(a, b, out):
    try:
        result = np.dot(a, b, out)
    except ValueError:
        # The last dimension of a is not the same size as the second-to-last dimension of b
        assert a.shape[-1] != b.shape[-2]
    else:
        # Check the output dtype
        assert result.dtype == np.result_type(a, b)     

        if out is not None:
            # If out is provided, check if it is same as result
            assert np.array_equal(out, result)

        # Check dimension reduction
        expected_shape = a.shape[:-1] + b.shape[:-2] + (b.shape[-1],)
        assert result.shape == expected_shape