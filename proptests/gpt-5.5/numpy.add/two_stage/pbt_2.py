from hypothesis import given, strategies as st
import numpy

_FINITE_FLOATS = st.floats(
    min_value=-1_000_000,
    max_value=1_000_000,
    allow_nan=False,
    allow_infinity=False,
    width=32,
)


def _size(shape):
    result = 1
    for dim in shape:
        result *= dim
    return result


def _shape(data, min_dims=0, max_dims=3, max_side=4):
    ndim = data.draw(st.integers(min_value=min_dims, max_value=max_dims))
    return tuple(
        data.draw(st.integers(min_value=1, max_value=max_side))
        for _ in range(ndim)
    )


def _broadcastable_shape(data, result_shape):
    if not result_shape:
        return ()

    kept_dims = data.draw(st.integers(min_value=0, max_value=len(result_shape)))
    trailing = result_shape[len(result_shape) - kept_dims:]

    return tuple(
        data.draw(st.sampled_from([1, dim])) if dim != 1 else 1
        for dim in trailing
    )


def _float_array_or_scalar(data, shape):
    values = data.draw(
        st.lists(_FINITE_FLOATS, min_size=_size(shape), max_size=_size(shape))
    )
    if shape == ():
        return float(values[0])
    return numpy.array(values, dtype=numpy.float64).reshape(shape)


def _bool_array_or_scalar(data, shape):
    values = data.draw(
        st.lists(st.booleans(), min_size=_size(shape), max_size=_size(shape))
    )
    if shape == ():
        return bool(values[0])
    return numpy.array(values, dtype=bool).reshape(shape)


def _broadcastable_pair(data):
    result_shape = _shape(data)
    shape1 = _broadcastable_shape(data, result_shape)
    shape2 = _broadcastable_shape(data, result_shape)
    x1 = _float_array_or_scalar(data, shape1)
    x2 = _float_array_or_scalar(data, shape2)
    return x1, x2


@given(st.data())
def test_numpy_add_output_has_broadcast_shape(data):
    x1, x2 = _broadcastable_pair(data)

    result = numpy.add(x1, x2)
    expected_shape = numpy.broadcast(numpy.empty(numpy.shape(x1)), numpy.empty(numpy.shape(x2))).shape

    assert numpy.shape(result) == expected_shape
    if numpy.isscalar(x1) and numpy.isscalar(x2):
        assert numpy.isscalar(result)


@given(st.data())
def test_numpy_add_output_values_are_elementwise_sums(data):
    x1, x2 = _broadcastable_pair(data)

    result = numpy.add(x1, x2)
    broadcast_x1, broadcast_x2 = numpy.broadcast_arrays(x1, x2)

    result_array = numpy.asarray(result)
    for index in numpy.ndindex(result_array.shape):
        assert result_array[index] == broadcast_x1[index] + broadcast_x2[index]


@given(st.data())
def test_numpy_add_is_commutative_for_finite_numeric_inputs(data):
    x1, x2 = _broadcastable_pair(data)

    forward = numpy.add(x1, x2)
    reverse = numpy.add(x2, x1)

    assert numpy.array_equal(numpy.asarray(forward), numpy.asarray(reverse))


@given(st.data())
def test_numpy_add_zero_preserves_values(data):
    shape = _shape(data)
    x = _float_array_or_scalar(data, shape)

    result = numpy.add(x, 0.0)

    assert numpy.shape(result) == numpy.shape(x)
    assert numpy.array_equal(numpy.asarray(result), numpy.asarray(x))


@given(st.data())
def test_numpy_add_where_updates_only_true_positions(data):
    shape = _shape(data, min_dims=1)
    x1 = _float_array_or_scalar(data, shape)
    x2 = _float_array_or_scalar(data, shape)

    out = _float_array_or_scalar(data, shape)
    original_out = out.copy()

    where_shape = _broadcastable_shape(data, shape)
    where = _bool_array_or_scalar(data, where_shape)
    broadcast_where = numpy.broadcast_to(where, shape)

    result = numpy.add(x1, x2, out=out, where=where)

    expected = original_out.copy()
    sums = numpy.add(x1, x2)
    expected[broadcast_where] = sums[broadcast_where]

    assert result is out
    assert numpy.array_equal(out, expected)
# End program