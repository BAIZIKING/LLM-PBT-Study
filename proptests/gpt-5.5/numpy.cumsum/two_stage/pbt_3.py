from hypothesis import given, strategies as st
import numpy

_DTYPES = (numpy.int8, numpy.int16, numpy.int32, numpy.int64, numpy.float32, numpy.float64)


def _default_cumsum_dtype(dtype):
    dtype = numpy.dtype(dtype)
    if numpy.issubdtype(dtype, numpy.signedinteger) and dtype.itemsize < numpy.dtype(numpy.int_).itemsize:
        return numpy.dtype(numpy.int_)
    return dtype


def _draw_array_axis_and_dtype(data):
    ndim = data.draw(st.integers(min_value=1, max_value=3))
    shape = tuple(
        data.draw(
            st.lists(
                st.integers(min_value=1, max_value=4),
                min_size=ndim,
                max_size=ndim,
            )
        )
    )
    size = int(numpy.prod(shape))
    dtype = data.draw(st.sampled_from(_DTYPES))
    values = data.draw(
        st.lists(
            st.integers(min_value=-1, max_value=1),
            min_size=size,
            max_size=size,
        )
    )
    axis = data.draw(st.one_of(st.none(), st.integers(min_value=-ndim, max_value=ndim - 1)))
    dtype_arg = data.draw(st.one_of(st.none(), st.sampled_from(_DTYPES)))
    array = numpy.array(values, dtype=dtype).reshape(shape)
    return array, axis, dtype_arg


def _manual_cumsum(array, axis=None, dtype=None):
    result_dtype = numpy.dtype(dtype) if dtype is not None else _default_cumsum_dtype(array.dtype)

    if axis is None:
        flat = array.ravel()
        result = numpy.empty(flat.shape, dtype=result_dtype)
        total = 0
        for i, value in enumerate(flat):
            total += value.item()
            result[i] = total
        return result

    axis = axis % array.ndim
    moved = numpy.moveaxis(array, axis, 0)
    result_moved = numpy.empty(moved.shape, dtype=result_dtype)

    for rest_index in numpy.ndindex(moved.shape[1:]):
        total = 0
        for i in range(moved.shape[0]):
            index = (i,) + rest_index
            total += moved[index].item()
            result_moved[index] = total

    return numpy.moveaxis(result_moved, 0, axis)


@given(st.data())
def test_numpy_cumsum_shape_and_size_property(data):
    array, axis, dtype_arg = _draw_array_axis_and_dtype(data)

    result = numpy.cumsum(array, axis=axis, dtype=dtype_arg)

    expected_shape = (array.size,) if axis is None else array.shape
    assert result.shape == expected_shape
    assert result.size == array.size


@given(st.data())
def test_numpy_cumsum_matches_manual_cumulative_sum_property(data):
    array, axis, dtype_arg = _draw_array_axis_and_dtype(data)

    result = numpy.cumsum(array, axis=axis, dtype=dtype_arg)
    expected = _manual_cumsum(array, axis=axis, dtype=dtype_arg)

    numpy.testing.assert_array_equal(result, expected)


@given(st.data())
def test_numpy_cumsum_recurrence_property(data):
    array, axis, dtype_arg = _draw_array_axis_and_dtype(data)

    result = numpy.cumsum(array, axis=axis, dtype=dtype_arg)

    if axis is None:
        flat_input = array.ravel().astype(result.dtype, copy=False)
        flat_result = result.ravel()
        numpy.testing.assert_array_equal(flat_result[0], flat_input[0])
        numpy.testing.assert_array_equal(flat_result[1:] - flat_result[:-1], flat_input[1:])
    else:
        normalized_axis = axis % array.ndim
        first_result = numpy.take(result, 0, axis=normalized_axis)
        first_input = numpy.take(array, 0, axis=normalized_axis).astype(result.dtype, copy=False)
        numpy.testing.assert_array_equal(first_result, first_input)

        result_differences = numpy.diff(result, axis=normalized_axis)
        input_tail = numpy.take(
            array,
            range(1, array.shape[normalized_axis]),
            axis=normalized_axis,
        ).astype(result.dtype, copy=False)
        numpy.testing.assert_array_equal(result_differences, input_tail)


@given(st.data())
def test_numpy_cumsum_dtype_property(data):
    array, axis, dtype_arg = _draw_array_axis_and_dtype(data)

    result = numpy.cumsum(array, axis=axis, dtype=dtype_arg)

    if dtype_arg is not None:
        assert result.dtype == numpy.dtype(dtype_arg)
    else:
        assert result.dtype == _default_cumsum_dtype(array.dtype)


@given(st.data())
def test_numpy_cumsum_out_property(data):
    array, axis, dtype_arg = _draw_array_axis_and_dtype(data)
    out_dtype = data.draw(st.sampled_from(_DTYPES))

    out_shape = (array.size,) if axis is None else array.shape
    out = numpy.empty(out_shape, dtype=out_dtype)

    result = numpy.cumsum(array, axis=axis, dtype=dtype_arg, out=out)
    expected = _manual_cumsum(array, axis=axis, dtype=dtype_arg).astype(out_dtype)

    assert result is out
    numpy.testing.assert_array_equal(out, expected)
# End program