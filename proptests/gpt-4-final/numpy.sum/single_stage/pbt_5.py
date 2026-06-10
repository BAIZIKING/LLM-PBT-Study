from hypothesis import given, strategies as st, assume
import numpy as np

@given(array=st.lists(st.floats(allow_nan=True, allow_infinity=True), min_size=0, max_size=10).map(np.array))
def test_numpy_sum(array):
    # Property: Sum of an array should be equal to manual summation
    assert np.sum(array) == sum(array)

    # When sum over axis 0 or -1 (when the input is 1D), the output should be a scalar
    assert isinstance(np.sum(array, axis=0), np.number)
    assert isinstance(np.sum(array, axis=-1), np.number)

    # For multi-dimensional array
    if len(array.shape) > 1:
        assert np.sum(array, axis=0).shape == array.shape[1:]
        assert np.sum(array, axis=-1).shape == array.shape[:-1]

    # If the dtype="float64", the result should be a float
    assume(array.dtype == "float64")
    assert isinstance(np.sum(array), float)

    # If keepdims=True, the returned array should have same number of dimensions
    assert np.sum(array, keepdims=True).ndim == array.ndim