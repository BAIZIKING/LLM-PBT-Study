from hypothesis import given, strategies as st
import numpy

@given(st.data())
def test_numpy_sum_axis_none_equals_python_sum_plus_initial(data):
    values = data.draw(
        st.lists(st.integers(min_value=-1000, max_value=1000), min_size=0, max_size=50)
    )
    initial = data.draw(st.integers(min_value=-1000, max_value=1000))

    result = numpy.sum(values, axis=None, initial=initial)

    assert numpy.ndim(result) == 0
    assert result == sum(values) + initial


@given(st.data())
def test_numpy_sum_axis_and_keepdims_determine_output_shape(data):
    ndim = data.draw(st.integers(min_value=1, max_value=4))
    shape = tuple(
        data.draw(st.integers(min_value=0, max_value=4)) for _ in range(ndim)
    )

    array = numpy.zeros(shape, dtype=numpy.int64)

    axis_count = data.draw(st.integers(min_value=1, max_value=ndim))
    positive_axes = data.draw(
        st.lists(
            st.integers(min_value=0, max_value=ndim - 1),
            min_size=axis_count,
            max_size=axis_count,
            unique=True,
        )
    )

    axes = []
    for ax in positive_axes:
        use_negative = data.draw(st.booleans())
        axes.append(ax - ndim if use_negative else ax)

    axis = axes[0] if len(axes) == 1 else tuple(axes)
    keepdims = data.draw(st.booleans())

    result = numpy.sum(array, axis=axis, keepdims=keepdims)

    reduced_axes = {ax % ndim for ax in axes}
    if keepdims:
        expected_shape = tuple(1 if i in reduced_axes else shape[i] for i in range(ndim))
    else:
        expected_shape = tuple(shape[i] for i in range(ndim) if i not in reduced_axes)

    assert result.shape == expected_shape


@given(st.data())
def test_numpy_sum_where_only_includes_true_elements(data):
    length = data.draw(st.integers(min_value=0, max_value=50))
    values = data.draw(
        st.lists(
            st.floats(
                min_value=-1000.0,
                max_value=1000.0,
                allow_nan=False,
                allow_infinity=False,
                width=32,
            ),
            min_size=length,
            max_size=length,
        )
    )
    mask = data.draw(
        st.lists(st.booleans(), min_size=length, max_size=length)
    )
    initial = data.draw(
        st.floats(
            min_value=-1000.0,
            max_value=1000.0,
            allow_nan=False,
            allow_infinity=False,
            width=32,
        )
    )

    result = numpy.sum(values, where=mask, initial=initial, dtype=numpy.float64)
    expected = initial + sum(value for value, include in zip(values, mask) if include)

    assert numpy.allclose(result, expected, rtol=1e-12, atol=1e-12)


@given(st.data())
def test_numpy_sum_empty_reduction_returns_zero_or_initial(data):
    initial = data.draw(st.integers(min_value=-1000, max_value=1000))

    result_without_initial = numpy.sum([])
    result_with_initial = numpy.sum([], initial=initial)

    assert result_without_initial == 0
    assert result_with_initial == initial


@given(st.data())
def test_numpy_sum_out_is_returned_and_contains_cast_result(data):
    rows = data.draw(st.integers(min_value=0, max_value=8))
    columns = data.draw(st.integers(min_value=0, max_value=8))
    values = data.draw(
        st.lists(
            st.integers(min_value=-1000, max_value=1000),
            min_size=rows * columns,
            max_size=rows * columns,
        )
    )
    out_dtype = data.draw(st.sampled_from([numpy.int64, numpy.float64]))

    array = numpy.array(values, dtype=numpy.int64).reshape((rows, columns))
    out = numpy.empty((rows,), dtype=out_dtype)

    returned = numpy.sum(array, axis=1, out=out)
    expected = numpy.sum(array, axis=1).astype(out_dtype)

    assert returned is out
    assert out.dtype == numpy.dtype(out_dtype)
    assert numpy.array_equal(out, expected)
# End program