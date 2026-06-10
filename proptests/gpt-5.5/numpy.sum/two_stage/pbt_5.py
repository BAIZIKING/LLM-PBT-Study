from hypothesis import given, strategies as st
import numpy


def _size(shape):
    total = 1
    for dim in shape:
        total *= dim
    return total


def _draw_shape(data):
    ndim = data.draw(st.integers(min_value=0, max_value=4))
    if ndim == 0:
        return ()
    return tuple(
        data.draw(
            st.lists(
                st.integers(min_value=0, max_value=3),
                min_size=ndim,
                max_size=ndim,
            )
        )
    )


def _draw_int_array(data, shape, min_value=-20, max_value=20):
    size = _size(shape)
    values = data.draw(
        st.lists(
            st.integers(min_value=min_value, max_value=max_value),
            min_size=size,
            max_size=size,
        )
    )
    return numpy.array(values, dtype=numpy.int64).reshape(shape)


def _draw_bool_array(data, shape):
    size = _size(shape)
    values = data.draw(
        st.lists(
            st.booleans(),
            min_size=size,
            max_size=size,
        )
    )
    return numpy.array(values, dtype=bool).reshape(shape)


def _draw_axis(data, ndim):
    if ndim == 0:
        return None

    kind = data.draw(st.sampled_from(["none", "int", "tuple"]))

    if kind == "none":
        return None

    if kind == "int":
        return data.draw(st.integers(min_value=-ndim, max_value=ndim - 1))

    normalized_axes = data.draw(
        st.lists(
            st.integers(min_value=0, max_value=ndim - 1),
            min_size=1,
            max_size=ndim,
            unique=True,
        )
    )

    axes = []
    for axis in normalized_axes:
        if data.draw(st.booleans()):
            axes.append(axis - ndim)
        else:
            axes.append(axis)
    return tuple(axes)


def _normalized_reduced_axes(axis, ndim):
    if axis is None:
        return tuple(range(ndim))
    if isinstance(axis, tuple):
        return tuple(ax % ndim for ax in axis)
    return (axis % ndim,)


def _expected_reduction_shape(shape, axis, keepdims):
    ndim = len(shape)
    reduced_axes = set(_normalized_reduced_axes(axis, ndim))

    if keepdims:
        return tuple(1 if i in reduced_axes else dim for i, dim in enumerate(shape))

    return tuple(dim for i, dim in enumerate(shape) if i not in reduced_axes)


@given(st.data())
def test_numpy_sum_matches_python_sum_for_axis_none_where_and_initial(data):
    shape = _draw_shape(data)
    array = _draw_int_array(data, shape)
    where = _draw_bool_array(data, shape)
    initial = data.draw(st.integers(min_value=-100, max_value=100))

    result = numpy.sum(
        array,
        axis=None,
        dtype=numpy.int64,
        where=where,
        initial=initial,
    )

    expected = initial + sum(
        int(value)
        for value, include in zip(array.reshape(-1), where.reshape(-1))
        if include
    )

    assert int(result) == expected


@given(st.data())
def test_numpy_sum_axis_none_returns_scalar_without_keepdims(data):
    shape = _draw_shape(data)
    array = _draw_int_array(data, shape)

    result = numpy.sum(array, axis=None, dtype=numpy.int64)

    assert numpy.ndim(result) == 0


@given(st.data())
def test_numpy_sum_reduction_shape_matches_axis_and_keepdims(data):
    shape = _draw_shape(data)
    array = _draw_int_array(data, shape)
    axis = _draw_axis(data, len(shape))
    keepdims = data.draw(st.booleans())

    result = numpy.sum(array, axis=axis, dtype=numpy.int64, keepdims=keepdims)

    assert numpy.shape(result) == _expected_reduction_shape(shape, axis, keepdims)


@given(st.data())
def test_numpy_sum_all_false_where_returns_identity_or_initial(data):
    shape = _draw_shape(data)
    array = _draw_int_array(data, shape)
    axis = _draw_axis(data, len(shape))
    keepdims = data.draw(st.booleans())
    use_initial = data.draw(st.booleans())

    where = numpy.zeros(shape, dtype=bool)

    if use_initial:
        initial = data.draw(st.integers(min_value=-100, max_value=100))
        result = numpy.sum(
            array,
            axis=axis,
            dtype=numpy.int64,
            where=where,
            initial=initial,
            keepdims=keepdims,
        )
        expected_value = initial
    else:
        result = numpy.sum(
            array,
            axis=axis,
            dtype=numpy.int64,
            where=where,
            keepdims=keepdims,
        )
        expected_value = 0

    assert numpy.shape(result) == _expected_reduction_shape(shape, axis, keepdims)
    assert numpy.all(numpy.asarray(result) == expected_value)


@given(st.data())
def test_numpy_sum_out_is_returned_and_contains_cast_result(data):
    shape = _draw_shape(data)
    array = _draw_int_array(data, shape, min_value=-10, max_value=10)
    axis = _draw_axis(data, len(shape))
    keepdims = data.draw(st.booleans())
    out_dtype = data.draw(st.sampled_from([numpy.int16, numpy.int64, numpy.float64]))

    expected = numpy.sum(array, axis=axis, dtype=numpy.int64, keepdims=keepdims)
    expected_shape = _expected_reduction_shape(shape, axis, keepdims)

    out = numpy.empty(expected_shape, dtype=out_dtype)
    returned = numpy.sum(
        array,
        axis=axis,
        dtype=numpy.int64,
        out=out,
        keepdims=keepdims,
    )

    assert returned is out
    assert numpy.array_equal(out, numpy.asarray(expected, dtype=out_dtype))


# End program