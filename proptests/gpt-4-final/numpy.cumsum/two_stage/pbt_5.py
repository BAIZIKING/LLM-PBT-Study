from hypothesis import given, strategies as st
import numpy as np

@given(st.lists(st.integers(-100, 100), min_size=1), st.integers(0, 1))
def test_numpy_cumsum_property(input_list, axis):
    input_array = np.array(input_list)

    cumsum_output = np.cumsum(input_array, axis=axis)

    # Property 1: The output of np.cumsum is always an ndarray
    assert isinstance(cumsum_output, np.ndarray)

    # Property 2: The dtype of output matches input array if dtype isn't specified
    assert input_array.dtype == cumsum_output.dtype

    # Property 3: The shape of the output array should be equal to shape of input array if axis is not None
    if axis is not None:
        assert input_array.shape == cumsum_output.shape

    # Property 4: The elements of output array are cumulatively summed
    if len(input_array) > 0:
        assert np.all(np.diff(cumsum_output) == input_array[1:] if axis == 0 else input_array[:-1])

    # Property 5: Overflow doesn't raise any error for integer types
    try:
        np.cumsum(input_array, dtype='int')
    except OverflowError:
        assert False