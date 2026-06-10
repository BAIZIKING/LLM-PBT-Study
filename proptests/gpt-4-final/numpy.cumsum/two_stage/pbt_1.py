from hypothesis import given, strategies as st
import numpy

@given(st.lists(st.integers(-100,100), min_size=5, max_size=100), 
       st.optional(st.sampled_from([numpy.int32, numpy.int64, numpy.float32, numpy.float64])),
       st.sampled_from([None, 0]))
def test_numpy_cumsum_property(input_array, dtype, axis):
    # Convert list to numpy array
    np_array = numpy.array(input_array, dtype=dtype)

    # calculate cumulative sum
    cumsum_result = numpy.cumsum(np_array, dtype=dtype, axis=axis)

    # if dtype is not specified, it should default to the dtype of a
    if dtype is None:
        assert cumsum_result.dtype == np_array.dtype
    else:
        assert cumsum_result.dtype == dtype

    # The size of the output array should be the same as that of the input array
    assert np_array.size == cumsum_result.size

    # If an axis is specified, the output array should have the same shape as the input array
    if axis is not None:
        assert np_array.shape == cumsum_result.shape
    else:
        assert cumsum_result.shape == (np_array.size, )

    # for floating point numbers, cumsum(a)[-1] may not equal sum(a)
    if np_array.dtype in [numpy.float32, numpy.float64]:
        assert not numpy.isclose(cumsum_result[-1], numpy.sum(np_array))

    # If input values are integers, the cumsum(a)[-1] should be equal to sum(a)
    elif np_array.dtype in [numpy.int32, numpy.int64]:
        assert cumsum_result[-1] == numpy.sum(np_array)

# End program