from hypothesis import given, strategies as st
import numpy

FINITE_FLOATS = st.floats(
    min_value=-100.0,
    max_value=100.0,
    allow_nan=False,
    allow_infinity=False,
    allow_subnormal=False,
    width=32,
)


def draw_array(data, shape):
    size = int(numpy.prod(shape))
    values = data.draw(st.lists(FINITE_FLOATS, min_size=size, max_size=size))
    return numpy.array(values, dtype=float).reshape(shape)


@given(st.data())
def test_numpy_linalg_norm_is_nonnegative(data):
    ndim = data.draw(st.integers(min_value=1, max_value=2))
    shape = tuple(data.draw(st.integers(min_value=1, max_value=5)) for _ in range(ndim))
    x = draw_array(data, shape)

    if ndim == 1:
        ord_value = data.draw(
            st.sampled_from([None, numpy.inf, -numpy.inf, 0, 1, 2, 3])
        )
    else:
        ord_value = data.draw(
            st.sampled_from(
                [None, "fro", "nuc", numpy.inf, -numpy.inf, 1, -1, 2, -2]
            )
        )

    result = numpy.linalg.norm(x, ord=ord_value)

    assert numpy.isfinite(result)
    assert result >= 0


@given(st.data())
def test_numpy_linalg_norm_vector_homogeneity_for_valid_norms(data):
    length = data.draw(st.integers(min_value=1, max_value=20))
    x = draw_array(data, (length,))
    scalar = data.draw(FINITE_FLOATS)
    ord_value = data.draw(st.sampled_from([1, 2, 3, numpy.inf]))

    left = numpy.linalg.norm(scalar * x, ord=ord_value)
    right = abs(scalar) * numpy.linalg.norm(x, ord=ord_value)

    numpy.testing.assert_allclose(left, right, rtol=1e-10, atol=1e-10)


@given(st.data())
def test_numpy_linalg_norm_vector_triangle_inequality_for_valid_norms(data):
    length = data.draw(st.integers(min_value=1, max_value=20))
    x = draw_array(data, (length,))
    y = draw_array(data, (length,))
    ord_value = data.draw(st.sampled_from([1, 2, 3, numpy.inf]))

    left = numpy.linalg.norm(x + y, ord=ord_value)
    right = numpy.linalg.norm(x, ord=ord_value) + numpy.linalg.norm(y, ord=ord_value)

    assert left <= right + 1e-10 * (1.0 + right)


@given(st.data())
def test_numpy_linalg_norm_ord_none_axis_none_equals_flattened_euclidean_norm(data):
    ndim = data.draw(st.integers(min_value=1, max_value=4))
    shape = tuple(data.draw(st.integers(min_value=1, max_value=4)) for _ in range(ndim))
    x = draw_array(data, shape)

    result = numpy.linalg.norm(x, ord=None, axis=None)
    expected = numpy.sqrt(numpy.sum(numpy.abs(x.ravel()) ** 2))

    numpy.testing.assert_allclose(result, expected, rtol=1e-12, atol=1e-12)


@given(st.data())
def test_numpy_linalg_norm_keepdims_preserves_reduced_axes_as_size_one(data):
    ndim = data.draw(st.integers(min_value=1, max_value=4))
    shape = tuple(data.draw(st.integers(min_value=1, max_value=4)) for _ in range(ndim))
    x = draw_array(data, shape)

    use_matrix_axes = ndim >= 2 and data.draw(st.booleans())

    if use_matrix_axes:
        first_axis = data.draw(st.integers(min_value=0, max_value=ndim - 1))
        second_axis = data.draw(
            st.sampled_from([axis for axis in range(ndim) if axis != first_axis])
        )
        axis = (first_axis, second_axis)
        ord_value = data.draw(
            st.sampled_from([None, "fro", "nuc", numpy.inf, -numpy.inf, 1, -1])
        )
        expected_shape = list(shape)
        expected_shape[first_axis] = 1
        expected_shape[second_axis] = 1
    else:
        axis = data.draw(st.integers(min_value=0, max_value=ndim - 1))
        ord_value = data.draw(
            st.sampled_from([None, numpy.inf, -numpy.inf, 0, 1, 2, 3])
        )
        expected_shape = list(shape)
        expected_shape[axis] = 1

    result = numpy.linalg.norm(x, ord=ord_value, axis=axis, keepdims=True)

    assert result.shape == tuple(expected_shape)
    numpy.broadcast_to(result, x.shape)


# End program