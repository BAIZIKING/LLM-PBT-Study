from hypothesis import given, strategies as st
import numpy


def _size(shape):
    result = 1
    for dim in shape:
        result *= dim
    return result


def _indices(shape):
    if len(shape) == 0:
        yield ()
    else:
        yield from numpy.ndindex(*shape)


@given(st.data())
def test_numpy_dot_1d_vectors_are_inner_product_without_conjugation(data):
    n = data.draw(st.integers(min_value=0, max_value=5))

    complex_int = st.tuples(
        st.integers(min_value=-10, max_value=10),
        st.integers(min_value=-10, max_value=10),
    )

    a_values = data.draw(st.lists(complex_int, min_size=n, max_size=n))
    b_values = data.draw(st.lists(complex_int, min_size=n, max_size=n))

    a = numpy.array([real + 1j * imag for real, imag in a_values])
    b = numpy.array([real + 1j * imag for real, imag in b_values])

    result = numpy.dot(a, b)
    expected = sum((a[i] * b[i] for i in range(n)), 0j)

    assert numpy.shape(result) == ()
    assert result == expected


@given(st.data())
def test_numpy_dot_2d_arrays_are_matrix_product(data):
    m = data.draw(st.integers(min_value=0, max_value=4))
    n = data.draw(st.integers(min_value=0, max_value=4))
    p = data.draw(st.integers(min_value=0, max_value=4))

    a_values = data.draw(
        st.lists(
            st.integers(min_value=-10, max_value=10),
            min_size=m * n,
            max_size=m * n,
        )
    )
    b_values = data.draw(
        st.lists(
            st.integers(min_value=-10, max_value=10),
            min_size=n * p,
            max_size=n * p,
        )
    )

    a = numpy.array(a_values, dtype=numpy.int64).reshape((m, n))
    b = numpy.array(b_values, dtype=numpy.int64).reshape((n, p))

    result = numpy.dot(a, b)

    assert result.shape == (m, p)

    for i in range(m):
        for j in range(p):
            expected = sum(int(a[i, k]) * int(b[k, j]) for k in range(n))
            assert result[i, j] == expected


@given(st.data())
def test_numpy_dot_with_scalar_is_equivalent_to_multiply(data):
    scalar = data.draw(st.integers(min_value=-10, max_value=10))

    ndim = data.draw(st.integers(min_value=0, max_value=3))
    shape = tuple(
        data.draw(st.lists(st.integers(min_value=0, max_value=4), min_size=ndim, max_size=ndim))
    )

    values = data.draw(
        st.lists(
            st.integers(min_value=-10, max_value=10),
            min_size=_size(shape),
            max_size=_size(shape),
        )
    )

    scalar_array = numpy.array(scalar, dtype=numpy.int64)
    array = numpy.array(values, dtype=numpy.int64).reshape(shape)

    left_result = numpy.dot(scalar_array, array)
    right_result = numpy.dot(array, scalar_array)

    expected = numpy.multiply(scalar_array, array)

    assert numpy.array_equal(left_result, expected)
    assert numpy.array_equal(right_result, expected)


@given(st.data())
def test_numpy_dot_nd_array_and_1d_array_sums_over_last_axis(data):
    prefix_ndim = data.draw(st.integers(min_value=0, max_value=3))
    prefix_shape = tuple(
        data.draw(
            st.lists(
                st.integers(min_value=0, max_value=4),
                min_size=prefix_ndim,
                max_size=prefix_ndim,
            )
        )
    )
    shared_dim = data.draw(st.integers(min_value=0, max_value=4))

    a_shape = prefix_shape + (shared_dim,)

    a_values = data.draw(
        st.lists(
            st.integers(min_value=-10, max_value=10),
            min_size=_size(a_shape),
            max_size=_size(a_shape),
        )
    )
    b_values = data.draw(
        st.lists(
            st.integers(min_value=-10, max_value=10),
            min_size=shared_dim,
            max_size=shared_dim,
        )
    )

    a = numpy.array(a_values, dtype=numpy.int64).reshape(a_shape)
    b = numpy.array(b_values, dtype=numpy.int64)

    result = numpy.dot(a, b)

    assert numpy.shape(result) == prefix_shape

    for index in _indices(prefix_shape):
        expected = sum(int(a[index + (k,)]) * int(b[k]) for k in range(shared_dim))
        if prefix_shape == ():
            assert result == expected
        else:
            assert result[index] == expected


@given(st.data())
def test_numpy_dot_nd_and_md_arrays_sum_over_last_and_second_to_last_axes(data):
    a_prefix_ndim = data.draw(st.integers(min_value=0, max_value=3))
    b_prefix_ndim = data.draw(st.integers(min_value=0, max_value=3))

    a_prefix_shape = tuple(
        data.draw(
            st.lists(
                st.integers(min_value=0, max_value=3),
                min_size=a_prefix_ndim,
                max_size=a_prefix_ndim,
            )
        )
    )
    b_prefix_shape = tuple(
        data.draw(
            st.lists(
                st.integers(min_value=0, max_value=3),
                min_size=b_prefix_ndim,
                max_size=b_prefix_ndim,
            )
        )
    )

    shared_dim = data.draw(st.integers(min_value=0, max_value=3))
    trailing_dim = data.draw(st.integers(min_value=0, max_value=3))

    a_shape = a_prefix_shape + (shared_dim,)
    b_shape = b_prefix_shape + (shared_dim, trailing_dim)

    a_values = data.draw(
        st.lists(
            st.integers(min_value=-10, max_value=10),
            min_size=_size(a_shape),
            max_size=_size(a_shape),
        )
    )
    b_values = data.draw(
        st.lists(
            st.integers(min_value=-10, max_value=10),
            min_size=_size(b_shape),
            max_size=_size(b_shape),
        )
    )

    a = numpy.array(a_values, dtype=numpy.int64).reshape(a_shape)
    b = numpy.array(b_values, dtype=numpy.int64).reshape(b_shape)

    result = numpy.dot(a, b)
    expected_shape = a_prefix_shape + b_prefix_shape + (trailing_dim,)

    assert numpy.shape(result) == expected_shape

    for a_index in _indices(a_prefix_shape):
        for b_index in _indices(b_prefix_shape):
            for j in range(trailing_dim):
                expected = sum(
                    int(a[a_index + (k,)]) * int(b[b_index + (k, j)])
                    for k in range(shared_dim)
                )
                assert result[a_index + b_index + (j,)] == expected


# End program