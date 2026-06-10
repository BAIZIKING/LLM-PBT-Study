from hypothesis import given, strategies as st
import numpy


def _draw_vector(data, min_size=1, max_size=20, min_value=-1000, max_value=1000):
    size = data.draw(st.integers(min_value=min_size, max_value=max_size))
    values = data.draw(
        st.lists(
            st.integers(min_value=min_value, max_value=max_value),
            min_size=size,
            max_size=size,
        )
    )
    return numpy.array(values, dtype=float)


def _draw_matrix(data, min_rows=1, max_rows=8, min_cols=1, max_cols=8):
    rows = data.draw(st.integers(min_value=min_rows, max_value=max_rows))
    cols = data.draw(st.integers(min_value=min_cols, max_value=max_cols))
    values = data.draw(
        st.lists(
            st.integers(min_value=-1000, max_value=1000),
            min_size=rows * cols,
            max_size=rows * cols,
        )
    )
    return numpy.array(values, dtype=float).reshape(rows, cols)


@given(st.data())
def test_numpy_linalg_norm_nonnegative_and_zero_only_for_zero_vector(data):
    x = _draw_vector(data)
    ord_value = data.draw(st.sampled_from([None, 1, 2, numpy.inf]))

    result = numpy.linalg.norm(x, ord=ord_value)

    assert result >= 0
    if numpy.all(x == 0):
        assert result == 0
    else:
        assert result > 0


@given(st.data())
def test_numpy_linalg_norm_axis_and_keepdims_shape(data):
    shape = tuple(
        data.draw(st.integers(min_value=1, max_value=5))
        for _ in range(3)
    )
    values = data.draw(
        st.lists(
            st.integers(min_value=-1000, max_value=1000),
            min_size=shape[0] * shape[1] * shape[2],
            max_size=shape[0] * shape[1] * shape[2],
        )
    )
    x = numpy.array(values, dtype=float).reshape(shape)

    axis = data.draw(st.sampled_from([0, 1, 2, (0, 1), (0, 2), (1, 2)]))
    keepdims = data.draw(st.booleans())

    result = numpy.linalg.norm(x, axis=axis, keepdims=keepdims)

    axes = axis if isinstance(axis, tuple) else (axis,)
    if keepdims:
        expected_shape = list(shape)
        for ax in axes:
            expected_shape[ax] = 1
        expected_shape = tuple(expected_shape)
    else:
        expected_shape = tuple(
            dim for i, dim in enumerate(shape) if i not in axes
        )

    assert result.shape == expected_shape
    assert numpy.broadcast_to(result, shape).shape == shape if keepdims else True


@given(st.data())
def test_numpy_linalg_norm_scaling_property(data):
    x = _draw_vector(data)
    scalar = data.draw(st.integers(min_value=-100, max_value=100))
    ord_value = data.draw(st.sampled_from([None, 1, 2, 3, numpy.inf]))

    left = numpy.linalg.norm(scalar * x, ord=ord_value)
    right = abs(scalar) * numpy.linalg.norm(x, ord=ord_value)

    assert numpy.allclose(left, right, rtol=1e-12, atol=1e-12)


@given(st.data())
def test_numpy_linalg_norm_vector_special_orders_match_definitions(data):
    x = _draw_matrix(data)
    axis = data.draw(st.sampled_from([0, 1]))
    ord_value = data.draw(st.sampled_from([numpy.inf, -numpy.inf, 0, 1]))

    result = numpy.linalg.norm(x, ord=ord_value, axis=axis)
    abs_x = numpy.abs(x)

    if ord_value == numpy.inf:
        expected = numpy.max(abs_x, axis=axis)
    elif ord_value == -numpy.inf:
        expected = numpy.min(abs_x, axis=axis)
    elif ord_value == 0:
        expected = numpy.sum(x != 0, axis=axis)
    else:
        expected = numpy.sum(abs_x, axis=axis)

    assert numpy.allclose(result, expected, rtol=1e-12, atol=1e-12)


@given(st.data())
def test_numpy_linalg_norm_matrix_special_orders_match_definitions(data):
    x = _draw_matrix(data)
    ord_value = data.draw(st.sampled_from(["fro", numpy.inf, -numpy.inf, 1, -1]))

    result = numpy.linalg.norm(x, ord=ord_value)
    abs_x = numpy.abs(x)

    if ord_value == "fro":
        expected = numpy.sqrt(numpy.sum(abs_x ** 2))
    elif ord_value == numpy.inf:
        expected = numpy.max(numpy.sum(abs_x, axis=1))
    elif ord_value == -numpy.inf:
        expected = numpy.min(numpy.sum(abs_x, axis=1))
    elif ord_value == 1:
        expected = numpy.max(numpy.sum(abs_x, axis=0))
    else:
        expected = numpy.min(numpy.sum(abs_x, axis=0))

    assert numpy.allclose(result, expected, rtol=1e-12, atol=1e-12)
# End program