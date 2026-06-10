from hypothesis import given, strategies as st
import numpy

def _shape_strategy(max_ndim=3, max_side=4):
    return st.lists(
        st.integers(min_value=0, max_value=max_side),
        min_size=0,
        max_size=max_ndim,
    ).map(tuple)

def _array_from_shape(data, shape, dtype=numpy.int64, min_value=-100, max_value=100):
    size = int(numpy.prod(shape)) if shape else 1
    values = data.draw(
        st.lists(
            st.integers(min_value=min_value, max_value=max_value),
            min_size=size,
            max_size=size,
        )
    )
    return numpy.array(values, dtype=dtype).reshape(shape)

def _bool_array_from_shape(data, shape):
    size = int(numpy.prod(shape)) if shape else 1
    values = data.draw(
        st.lists(st.booleans(), min_size=size, max_size=size)
    )
    return numpy.array(values, dtype=bool).reshape(shape)

@given(st.data())
def test_numpy_sum_matches_python_sum_with_where_and_initial(data):
    shape = data.draw(_shape_strategy())
    array = _array_from_shape(
        data,
        shape,
        dtype=numpy.int64,
        min_value=-1000,
        max_value=1000,
    )
    where = _bool_array_from_shape(data, shape)
    initial = data.draw(st.integers(min_value=-1000, max_value=1000))

    result = numpy.sum(
        array,
        dtype=numpy.int64,
        initial=initial,
        where=where,
    )

    expected = initial + sum(
        int(value)
        for value, include in zip(array.ravel(), where.ravel())
        if bool(include)
    )

    assert result == expected

@given(st.data())
def test_numpy_sum_axis_none_output_shape_respects_keepdims(data):
    shape = data.draw(_shape_strategy())
    array = _array_from_shape(data, shape, dtype=numpy.int64)
    keepdims = data.draw(st.booleans())

    result = numpy.sum(
        array,
        axis=None,
        dtype=numpy.int64,
        keepdims=keepdims,
    )

    if keepdims:
        expected_shape = tuple(1 for _ in shape)
    else:
        expected_shape = ()

    assert numpy.shape(result) == expected_shape

@given(st.data())
def test_numpy_sum_axis_output_shape_respects_reduced_axes_and_keepdims(data):
    ndim = data.draw(st.integers(min_value=1, max_value=3))
    shape = tuple(
        data.draw(st.integers(min_value=0, max_value=4))
        for _ in range(ndim)
    )
    array = _array_from_shape(data, shape, dtype=numpy.int64)

    axes = data.draw(
        st.lists(
            st.integers(min_value=0, max_value=ndim - 1),
            min_size=1,
            max_size=ndim,
            unique=True,
        )
    )

    axis_values = []
    for axis in axes:
        if data.draw(st.booleans()):
            axis_values.append(axis - ndim)
        else:
            axis_values.append(axis)

    if len(axis_values) == 1 and data.draw(st.booleans()):
        axis_argument = axis_values[0]
    else:
        axis_argument = tuple(axis_values)

    keepdims = data.draw(st.booleans())

    result = numpy.sum(
        array,
        axis=axis_argument,
        dtype=numpy.int64,
        keepdims=keepdims,
    )

    reduced_axes = set(axes)
    if keepdims:
        expected_shape = tuple(
            1 if axis in reduced_axes else size
            for axis, size in enumerate(shape)
        )
    else:
        expected_shape = tuple(
            size
            for axis, size in enumerate(shape)
            if axis not in reduced_axes
        )

    assert numpy.shape(result) == expected_shape

@given(st.data())
def test_numpy_sum_explicit_dtype_controls_output_dtype(data):
    shape = data.draw(_shape_strategy())
    requested_dtype = data.draw(
        st.sampled_from(
            [
                numpy.int8,
                numpy.int16,
                numpy.int32,
                numpy.int64,
                numpy.float32,
                numpy.float64,
            ]
        )
    )
    array = _array_from_shape(
        data,
        shape,
        dtype=numpy.int64,
        min_value=-5,
        max_value=5,
    )

    result = numpy.sum(array, axis=None, dtype=requested_dtype)

    assert numpy.asarray(result).dtype == numpy.dtype(requested_dtype)

@given(st.data())
def test_numpy_sum_out_is_returned_and_receives_cast_result(data):
    rows = data.draw(st.integers(min_value=0, max_value=4))
    columns = data.draw(st.integers(min_value=0, max_value=4))
    shape = (rows, columns)
    array = _array_from_shape(
        data,
        shape,
        dtype=numpy.int64,
        min_value=-100,
        max_value=100,
    )

    axis = data.draw(st.integers(min_value=0, max_value=1))
    out_dtype = data.draw(st.sampled_from([numpy.int64, numpy.float64]))

    if axis == 0:
        out_shape = (columns,)
    else:
        out_shape = (rows,)

    out = numpy.empty(out_shape, dtype=out_dtype)

    returned = numpy.sum(
        array,
        axis=axis,
        dtype=numpy.int64,
        out=out,
    )

    expected = numpy.sum(array, axis=axis, dtype=numpy.int64).astype(out_dtype)

    assert returned is out
    assert numpy.array_equal(out, expected)
# End program