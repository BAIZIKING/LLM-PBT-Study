from hypothesis import given, strategies as st
import numpy


def _draw_int_array(data, shape, min_value=-10, max_value=10):
    size = int(numpy.prod(shape)) if shape else 1
    values = data.draw(
        st.lists(
            st.integers(min_value=min_value, max_value=max_value),
            min_size=size,
            max_size=size,
        )
    )
    return numpy.array(values, dtype=numpy.int64).reshape(shape)


def _draw_complex_array(data, shape, min_value=-5, max_value=5):
    size = int(numpy.prod(shape)) if shape else 1
    real_parts = data.draw(
        st.lists(
            st.integers(min_value=min_value, max_value=max_value),
            min_size=size,
            max_size=size,
        )
    )
    imag_parts = data.draw(
        st.lists(
            st.integers(min_value=min_value, max_value=max_value),
            min_size=size,
            max_size=size,
        )
    )
    values = [complex(r, i) for r, i in zip(real_parts, imag_parts)]
    return numpy.array(values, dtype=numpy.complex128).reshape(shape)


@given(st.data())
def test_numpy_dot_scalar_is_multiply(data):
    ndim = data.draw(st.integers(min_value=0, max_value=3))
    shape = tuple(
        data.draw(st.lists(st.integers(min_value=0, max_value=4), min_size=ndim, max_size=ndim))
    )
    array = _draw_int_array(data, shape)
    scalar = data.draw(st.integers(min_value=-10, max_value=10))

    if data.draw(st.booleans()):
        result = numpy.dot(scalar, array)
        expected = numpy.multiply(scalar, array)
    else:
        result = numpy.dot(array, scalar)
        expected = numpy.multiply(array, scalar)

    numpy.testing.assert_array_equal(result, expected)


@given(st.data())
def test_numpy_dot_1d_is_inner_product_without_complex_conjugation(data):
    length = data.draw(st.integers(min_value=0, max_value=6))
    a = _draw_complex_array(data, (length,))
    b = _draw_complex_array(data, (length,))

    result = numpy.dot(a, b)
    expected = sum(a[i] * b[i] for i in range(length))

    assert result == expected


@given(st.data())
def test_numpy_dot_2d_is_matrix_product(data):
    m = data.draw(st.integers(min_value=0, max_value=4))
    n = data.draw(st.integers(min_value=0, max_value=4))
    p = data.draw(st.integers(min_value=0, max_value=4))

    a = _draw_int_array(data, (m, n), min_value=-5, max_value=5)
    b = _draw_int_array(data, (n, p), min_value=-5, max_value=5)

    result = numpy.dot(a, b)
    expected = numpy.zeros((m, p), dtype=numpy.int64)

    for i in range(m):
        for j in range(p):
            expected[i, j] = sum(a[i, k] * b[k, j] for k in range(n))

    assert result.shape == (m, p)
    numpy.testing.assert_array_equal(result, expected)


@given(st.data())
def test_numpy_dot_nd_sums_last_axis_against_second_to_last_axis(data):
    a_prefix_len = data.draw(st.integers(min_value=0, max_value=2))
    b_prefix_len = data.draw(st.integers(min_value=0, max_value=2))

    a_prefix = tuple(
        data.draw(
            st.lists(
                st.integers(min_value=1, max_value=3),
                min_size=a_prefix_len,
                max_size=a_prefix_len,
            )
        )
    )
    b_prefix = tuple(
        data.draw(
            st.lists(
                st.integers(min_value=1, max_value=3),
                min_size=b_prefix_len,
                max_size=b_prefix_len,
            )
        )
    )

    contracted = data.draw(st.integers(min_value=0, max_value=4))
    b_last = data.draw(st.integers(min_value=1, max_value=3))

    a_shape = a_prefix + (contracted,)
    b_shape = b_prefix + (contracted, b_last)

    a = _draw_int_array(data, a_shape, min_value=-5, max_value=5)
    b = _draw_int_array(data, b_shape, min_value=-5, max_value=5)

    result = numpy.dot(a, b)
    expected_shape = a_prefix + b_prefix + (b_last,)

    assert result.shape == expected_shape

    expected = numpy.zeros(expected_shape, dtype=numpy.int64)
    for out_index in numpy.ndindex(expected_shape):
        a_prefix_index = out_index[:a_prefix_len]
        b_prefix_index = out_index[a_prefix_len:a_prefix_len + b_prefix_len]
        b_last_index = out_index[-1]

        expected[out_index] = sum(
            a[a_prefix_index + (k,)] * b[b_prefix_index + (k, b_last_index)]
            for k in range(contracted)
        )

    numpy.testing.assert_array_equal(result, expected)


@given(st.data())
def test_numpy_dot_is_linear_in_each_argument(data):
    m = data.draw(st.integers(min_value=1, max_value=4))
    n = data.draw(st.integers(min_value=1, max_value=4))
    p = data.draw(st.integers(min_value=1, max_value=4))

    alpha = data.draw(st.integers(min_value=-3, max_value=3))
    beta = data.draw(st.integers(min_value=-3, max_value=3))

    a1 = _draw_int_array(data, (m, n), min_value=-5, max_value=5)
    a2 = _draw_int_array(data, (m, n), min_value=-5, max_value=5)
    b1 = _draw_int_array(data, (n, p), min_value=-5, max_value=5)
    b2 = _draw_int_array(data, (n, p), min_value=-5, max_value=5)

    left_linear_result = numpy.dot(alpha * a1 + beta * a2, b1)
    left_linear_expected = alpha * numpy.dot(a1, b1) + beta * numpy.dot(a2, b1)

    right_linear_result = numpy.dot(a1, alpha * b1 + beta * b2)
    right_linear_expected = alpha * numpy.dot(a1, b1) + beta * numpy.dot(a1, b2)

    numpy.testing.assert_array_equal(left_linear_result, left_linear_expected)
    numpy.testing.assert_array_equal(right_linear_result, right_linear_expected)


# End program