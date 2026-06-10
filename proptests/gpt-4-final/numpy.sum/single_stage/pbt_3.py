from hypothesis import given, strategies as st
import numpy as np

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.integers(min_value=0, max_value=2))
def test_numpy_sum(l, axis):
    a = np.array(l)
    result = np.sum(a, axis=axis)

    # Check if output is scalar when axis is None
    if axis is None:
        assert np.isscalar(result)

    # Check if output array has same shape as expected output
    if type(result) == np.ndarray:
        if axis == 0:
            assert result.shape == (a.shape[1],)
        elif axis == 1:
            assert result.shape == (a.shape[0],)
    
    # Check if sum of all elements is returned when axis is None
    if axis is None:
        assert result == np.sum(a)

    # Test case when input is empty list and output should be 0.0
    a = np.array([])
    result = np.sum(a, axis=axis)
    assert result == 0.0
# End program