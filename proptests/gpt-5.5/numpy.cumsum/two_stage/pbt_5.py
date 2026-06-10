from hypothesis import given, strategies as st
import numpy

_DTYPE_NAMES = ("int8", "int16", "int64", "float32", "float64")


def _draw_shape(data, min_side=0, max_side=4, max_ndim=3):
    ndim = data.draw(st.integers(min_value=1, max_value=max_ndim))
    return tuple(
        data.draw(
            st.lists(
                st.integers(min_value=min_side, max_value=max_side),
                min_size=ndim,
                max_size=ndim,
            )
        )
    )


def _shape_size(shape):
    return int(numpy.prod(shape, dtype=numpy.int64))


def _draw_axis(data, ndim):
    return data.draw(st.one_of(st.none(), st.integers(min_value=-ndim, max_value=ndim - 1)))


def _draw_array(data, shape, dtype_names=_DTYPE_NAMES):
    dtype_name = data.draw(st.sampled_from(dtype_names))
    dtype = numpy.dtype(dtype_name)
    size = _shape_size(shape)

    if dtype.kind in ("i", "u"):
        values = data.draw(
            st.lists(
                st.integers(min_value=-100, max_value=100),
                min_size=size,
                max_size=size,
            )
        )
    else:
        values = data.draw(
            st.lists(
                st.floats(
                    min_value=-1000.0,
                    max_value=1000.0,
                    allow_nan=False,
                    allow_infinity=False,
                    width=32 if dtype == numpy.dtype("float32") else 64,
                ),
                min_size=size,
                max_size=size,
            )
        )

    return numpy.array(values, dtype=dtype).reshape(shape)


@given(st.data())
def test_numpy_cumsum_shape_and_size_property(data):
    shape = _draw_shape(data, min_side=0)
    a = _draw_array(data, shape)
    axis = _draw_axis(data, a.ndim)

    result = numpy.cumsum(a, axis=axis)

    assert result.size == a.size
    if axis is None:
        assert result.shape == (a.size,)
    else:
        assert result.shape == a.shape


@given(st.data())
def test_numpy_cumsum_first_element_property(data):
    shape = _draw_shape(data, min_side=1)
    a = _draw_array(data, shape)
    axis = _draw_axis(data, a.ndim)

    result = numpy.cumsum(a, axis=axis)

    if axis is None:
        expected_first = numpy.asarray(a.reshape(-1)[0], dtype=result.dtype)
        assert result[0] == expected_first
    else:
        first_result_slice = numpy.take(result, 0, axis=axis)
        first_input_slice = numpy.asarray(numpy.take(a, 0, axis=axis), dtype=result.dtype)
        assert numpy.array_equal(first_result_slice, first_input_slice)


@given(st.data())
def test_numpy_cumsum_recurrence_property(data):
    shape = _draw_shape(data, min_side=1)
    a = _draw_array(data, shape, dtype_names=("int64", "float32", "float64"))
    axis = _draw_axis(data, a.ndim)

    result = numpy.cumsum(a, axis=axis)

    if axis is None:
        flat_input = a.reshape(-1)
        for i in range(1, result.size):
            assert result[i] == result[i - 1] + flat_input[i]
    else:
        moved_input = numpy.moveaxis(a, axis, 0)
        moved_result = numpy.moveaxis(result, axis, 0)
        for i in range(1, moved_result.shape[0]):
            assert numpy.array_equal(
                moved_result[i],
                moved_result[i - 1] + moved_input[i],
            )


@given(st.data())
def test_numpy_cumsum_dtype_and_out_property(data):
    shape = _draw_shape(data, min_side=0)
    a = _draw_array(data, shape, dtype_names=("int8", "int16", "int64"))
    axis = _draw_axis(data, a.ndim)
    specified_dtype = numpy.dtype(data.draw(st.sampled_from(("int64", "float64"))))

    result = numpy.cumsum(a, axis=axis, dtype=specified_dtype)
    assert result.dtype == specified_dtype

    out = numpy.empty(result.shape, dtype=specified_dtype)
    returned = numpy.cumsum(a, axis=axis, dtype=specified_dtype, out=out)

    assert returned is out
    assert out.dtype == specified_dtype
    assert out.shape == result.shape
    assert numpy.array_equal(out, result)


@given(st.data())
def test_numpy_cumsum_integer_overflow_is_modular_property(data):
    dtype_name = data.draw(st.sampled_from(("int8", "uint8", "int16", "uint16")))
    dtype = numpy.dtype(dtype_name)
    info = numpy.iinfo(dtype)

    values = data.draw(
        st.lists(
            st.integers(min_value=int(info.min), max_value=int(info.max)),
            min_size=1,
            max_size=30,
        )
    )

    a = numpy.array(values, dtype=dtype)
    result = numpy.cumsum(a, dtype=dtype)

    running = 0
    modulus = int(info.max) - int(info.min) + 1
    expected_values = []
    for value in values:
        running += int(value)
        expected_values.append(((running - int(info.min)) % modulus) + int(info.min))

    expected = numpy.array(expected_values, dtype=dtype)

    assert result.dtype == dtype
    assert numpy.array_equal(result, expected)
# End program