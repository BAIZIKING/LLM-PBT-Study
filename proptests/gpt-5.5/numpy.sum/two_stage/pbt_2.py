from hypothesis import given, strategies as st
import numpy

def _prod(shape):
    result = 1
    for dim in shape:
        result *= dim
    return result

@given(st.data())
def test_numpy_sum_axis_none_scalar_includes_initial_and_where(data):
    values = data.draw(st.lists(st.integers(min_value=-100, max_value=100), max_size=30))
    mask = data.draw(st.lists(st.booleans(), min_size=len(values), max_size=len(values)))
    initial = data.draw(st.integers(min_value=-100, max_value=100))

    a = numpy.array(values, dtype=numpy.int64)
    where = numpy.array(mask, dtype=bool)

    result = numpy.sum(a, axis=None, where=where, initial=initial)
    expected = initial + sum(value for value, include in zip(values, mask) if include)

    assert numpy.asarray(result).shape == ()
    assert result == expected

@given(st.data())
def test_numpy_sum_axis_reduction_shape_and_keepdims(data):
    ndim = data.draw(st.integers(min_value=1, max_value=4))
    shape = tuple(
        data.draw(st.lists(st.integers(min_value=0, max_value=4), min_size=ndim, max_size=ndim))
    )
    axis_count = data.draw(st.integers(min_value=1, max_value=ndim))
    axes = data.draw(
        st.lists(
            st.integers(min_value=0, max_value=ndim - 1),
            min_size=axis_count,
            max_size=axis_count,
            unique=True,
        )
    )
    keepdims = data.draw(st.booleans())

    axis_arg = axes[0] if len(axes) == 1 and data.draw(st.booleans()) else tuple(axes)
    reduced_axes = set(axes)

    a = numpy.zeros(shape, dtype=numpy.int64)
    result = numpy.sum(a, axis=axis_arg, keepdims=keepdims)

    if keepdims:
        expected_shape = tuple(1 if i in reduced_axes else shape[i] for i in range(ndim))
    else:
        expected_shape = tuple(shape[i] for i in range(ndim) if i not in reduced_axes)

    assert numpy.shape(result) == expected_shape

@given(st.data())
def test_numpy_sum_negative_axis_matches_positive_axis(data):
    ndim = data.draw(st.integers(min_value=1, max_value=4))
    shape = tuple(
        data.draw(st.lists(st.integers(min_value=1, max_value=4), min_size=ndim, max_size=ndim))
    )
    size = _prod(shape)
    values = data.draw(
        st.lists(st.integers(min_value=-100, max_value=100), min_size=size, max_size=size)
    )
    negative_axis = data.draw(st.integers(min_value=-ndim, max_value=-1))

    a = numpy.array(values, dtype=numpy.int64).reshape(shape)

    result_negative = numpy.sum(a, axis=negative_axis)
    result_positive = numpy.sum(a, axis=negative_axis + ndim)

    assert numpy.array_equal(result_negative, result_positive)

@given(st.data())
def test_numpy_sum_where_excludes_elements_and_uses_initial_for_empty_slices(data):
    rows = data.draw(st.integers(min_value=0, max_value=5))
    cols = data.draw(st.integers(min_value=0, max_value=5))
    size = rows * cols

    values = data.draw(
        st.lists(st.integers(min_value=-100, max_value=100), min_size=size, max_size=size)
    )
    mask_values = data.draw(st.lists(st.booleans(), min_size=size, max_size=size))
    initial = data.draw(st.integers(min_value=-100, max_value=100))

    a = numpy.array(values, dtype=numpy.int64).reshape((rows, cols))
    where = numpy.array(mask_values, dtype=bool).reshape((rows, cols))

    result = numpy.sum(a, axis=1, where=where, initial=initial)

    expected_values = []
    for row in range(rows):
        row_sum = initial
        for col in range(cols):
            if where[row, col]:
                row_sum += int(a[row, col])
        expected_values.append(row_sum)

    expected = numpy.array(expected_values, dtype=result.dtype)

    assert numpy.array_equal(result, expected)

@given(st.data())
def test_numpy_sum_dtype_controls_output_and_small_integer_defaults_are_promoted(data):
    target_dtype = data.draw(
        st.sampled_from([numpy.int16, numpy.int32, numpy.int64, numpy.float32, numpy.float64])
    )
    values = data.draw(st.lists(st.integers(min_value=-100, max_value=100), max_size=20))

    a = numpy.array(values, dtype=numpy.int16)
    result = numpy.sum(a, dtype=target_dtype)

    assert numpy.asarray(result).dtype == numpy.dtype(target_dtype)

    small_dtype = data.draw(st.sampled_from([numpy.int8, numpy.uint8]))
    if numpy.issubdtype(numpy.dtype(small_dtype), numpy.unsignedinteger):
        promoted_values = data.draw(st.lists(st.integers(min_value=0, max_value=100), max_size=20))
        expected_default_dtype = numpy.dtype(f"u{numpy.dtype(numpy.int_).itemsize}")
    else:
        promoted_values = data.draw(st.lists(st.integers(min_value=-100, max_value=100), max_size=20))
        expected_default_dtype = numpy.dtype(numpy.int_)

    small_array = numpy.array(promoted_values, dtype=small_dtype)
    default_result = numpy.sum(small_array)

    assert numpy.asarray(default_result).dtype == expected_default_dtype
# End program