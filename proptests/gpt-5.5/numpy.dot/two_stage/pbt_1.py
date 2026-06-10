from hypothesis import given, strategies as st
import numpy

_SMALL_INTS = st.integers(min_value=-10, max_value=10)
_SMALL_COMPLEX = st.builds(
    complex,
    st.integers(min_value=-5, max_value=5),
    st.integers(min_value=-5, max_value=5),
)


def _prod(shape):
    result = 1
    for dim in shape:
        result *= dim
    return result


def _draw_array(data, shape, elements=_SMALL_INTS):
    size = _prod(shape)
    values = data.draw(st.lists(elements, min_size=size, max_size=size))
    return numpy.array(values).reshape(shape)


@given(st.data())
def test_numpy_dot_output_shape_property(data):
    case = data.draw(st.integers(min_value=0, max_value=4))

    if case == 0:
        a = data.draw(_SMALL_INTS)
        b = data.draw(_SMALL_INTS)
        expected_shape = ()

    elif case == 1:
        n = data.draw(st.integers(min_value=0, max_value=5))
        a = _draw_array(data, (n,))
        b = _draw_array(data, (n,))
        expected_shape = ()

    elif case == 2:
        n = data.draw(st.integers(min_value=0, max_value=5))
        prefix = tuple(
            data.draw(st.lists(st.integers(min_value=0, max_value=3), min_size=1, max_size=3))
        )
        a = _draw_array(data, prefix + (n,))
        b = _draw_array(data, (n,))
        expected_shape = prefix

    elif case == 3:
        n = data.draw(st.integers(min_value=0, max_value=5))
        a_prefix = tuple(
            data.draw(st.lists(st.integers(min_value=0, max_value=3), min_size=0, max_size=3))
        )
        b_prefix = tuple(
            data.draw(st.lists(st.integers(min_value=0, max_value=3), min_size=0, max_size=3))
        )
        b_last = data.draw(st.integers(min_value=0, max_value=3))
        a = _draw_array(data, a_prefix + (n,))
        b = _draw_array(data, b_prefix + (n, b_last))
        expected_shape = a_prefix + b_prefix + (b_last,)

    else:
        scalar = data.draw(_SMALL_INTS)
        shape = tuple(
            data.draw(st.lists(st.integers(min_value=0, max_value=3), min_size=1, max_size=3))
        )
        a = scalar
        b = _draw_array(data, shape)
        expected_shape = shape

    result = numpy.dot(a, b)
    assert numpy.shape(result) == expected_shape


@given(st.data())
def test_numpy_dot_one_dimensional_inner_product_without_conjugation_property(data):
    n = data.draw(st.integers(min_value=0, max_value=5))
    a = _draw_array(data, (n,), _SMALL_COMPLEX)
    b = _draw_array(data, (n,), _SMALL_COMPLEX)

    result = numpy.dot(a, b)
    expected = sum((a[i] * b[i] for i in range(n)), 0j)

    assert result == expected


@given(st.data())
def test_numpy_dot_two_dimensional_matrix_multiplication_property(data):
    rows = data.draw(st.integers(min_value=0, max_value=4))
    inner = data.draw(st.integers(min_value=0, max_value=4))
    cols = data.draw(st.integers(min_value=0, max_value=4))

    a = _draw_array(data, (rows, inner), _SMALL_COMPLEX)
    b = _draw_array(data, (inner, cols), _SMALL_COMPLEX)

    result = numpy.dot(a, b)
    expected = numpy.zeros((rows, cols), dtype=complex)

    for i in range(rows):
        for j in range(cols):
            expected[i, j] = sum((a[i, k] * b[k, j] for k in range(inner)), 0j)

    assert numpy.array_equal(result, expected)


@given(st.data())
def test_numpy_dot_scalar_argument_is_multiplication_property(data):
    scalar_on_left = data.draw(st.booleans())
    scalar = data.draw(_SMALL_COMPLEX)
    shape = tuple(
        data.draw(st.lists(st.integers(min_value=0, max_value=3), min_size=0, max_size=3))
    )

    if shape == ():
        array = numpy.array(data.draw(_SMALL_COMPLEX))
    else:
        array = _draw_array(data, shape, _SMALL_COMPLEX)

    if scalar_on_left:
        result = numpy.dot(numpy.array(scalar), array)
        expected = numpy.array(scalar) * array
    else:
        result = numpy.dot(array, numpy.array(scalar))
        expected = array * numpy.array(scalar)

    assert numpy.array_equal(numpy.asarray(result), numpy.asarray(expected))


@given(st.data())
def test_numpy_dot_nd_by_md_sum_product_axes_property(data):
    contracted = data.draw(st.integers(min_value=0, max_value=4))

    a_prefix = tuple(
        data.draw(st.lists(st.integers(min_value=1, max_value=3), min_size=1, max_size=3))
    )
    b_prefix = tuple(
        data.draw(st.lists(st.integers(min_value=1, max_value=3), min_size=0, max_size=2))
    )
    b_last = data.draw(st.integers(min_value=1, max_value=3))

    a_shape = a_prefix + (contracted,)
    b_shape = b_prefix + (contracted, b_last)

    a = _draw_array(data, a_shape, _SMALL_COMPLEX)
    b = _draw_array(data, b_shape, _SMALL_COMPLEX)

    result = numpy.dot(a, b)

    a_index = tuple(data.draw(st.integers(min_value=0, max_value=dim - 1)) for dim in a_prefix)
    b_prefix_index = tuple(data.draw(st.integers(min_value=0, max_value=dim - 1)) for dim in b_prefix)
    b_last_index = data.draw(st.integers(min_value=0, max_value=b_last - 1))

    result_index = a_index + b_prefix_index + (b_last_index,)
    expected = sum(
        (
            a[a_index + (k,)] * b[b_prefix_index + (k, b_last_index)]
            for k in range(contracted)
        ),
        0j,
    )

    assert result[result_index] == expected
# End program