from hypothesis import given, strategies as st
import numpy as np

@given(input_array=st.lists(st.floats(allow_nan=True, allow_infinity=True), min_size=1).map(np.array), dtype=st.sampled_from([None, np.int8, np.int16, np.int32, np.int64, np.float32, np.float64, np.complex128]), axis=st.integers(-3, 3))
def test_numpy_cumsum(input_array, dtype, axis):
    try:
        result = np.cumsum(input_array, dtype=dtype, axis=axis)
    except np.AxisError:
        # Invalid axis for the input array dimensions
        pass
    else:
        # Check that the output array has the same size as the input array
        assert result.size == input_array.size
        # If the dtype is specified, the output array should have this dtype
        if dtype is not None:
            assert result.dtype == dtype
        # When input_array is non-empty, numpy.cumsum(input_array)[0] should be equal to input_array[0]
        if input_array.size > 0:
            assert result[0] == input_array[0]
        # numpy.cumsum(input_array)[-1] should not always be equal numpy.sum(input_array) for floating-point values
        assert np.isclose(result[-1], np.sum(input_array), atol=0.1) if input_array.dtype == 'float' else True
# End program