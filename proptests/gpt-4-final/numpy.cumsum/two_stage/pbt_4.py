from hypothesis import given, strategies as st
import numpy as np

@given(st.lists(st.integers()), st.integers(min_value=0, max_value=1), st.sampled_from([int, float, None]), st.booleans())
def test_numpy_cumsum_property(input_list, axis, dtype, out):
    if dtype is None:
        dtype = np.random.choice([int, float])

    a = np.array(input_list, dtype=dtype)

    if out:
        out = np.zeros_like(a)
        result = np.cumsum(a, axis=axis, dtype=dtype, out=out)
        assert np.array_equal(result, out), "Output array does not match with the result"

    result = np.cumsum(a, axis=axis, dtype=dtype)

    # Property 1: Length of result list is same as the input list
    assert len(result) == len(a), "Length of the result is not equal to the length of the array"

    # Property 2: If axis = None, the result must be a 1D array
    if axis is None:
        assert result.ndim == 1, "Resulting array is not flattened"

    # Property 3: If axis is given, the output shape should match the input shape
    elif axis in [0, 1]:
        assert result.shape == a.shape, "Shapes of the resulting array and the input array are not equal"

    # Property 4: The dtype of the returned array should correspond to the specified dtype
    assert result.dtype == dtype, "Dtype of the result does not match with the specified dtype"

    # Property 5: The values in the result array is the running total of values from the array
    if len(a) > 0:
        assert np.all(result[1:] >= result[:-1]), "Values in the result array are not cumulatively summed from the array"