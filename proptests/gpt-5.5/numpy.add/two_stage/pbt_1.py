from hypothesis import given, strategies as st
import numpy

def _prod(shape):
    size = 1
    for dim in shape:
        size *= dim
    return size

def _draw_broadcastable_shape(data, target_shape):
    if len(target_shape) == 0:
        return ()

    kept_dims = data.draw(st.integers(min_value=0, max_value=len(target_shape)))
    if kept_dims == 0:
        return ()

    shape = []
    for dim in target_shape[-kept_dims:]:
        if dim == 1:
            shape.append(1)
        else:
            shape.append(data.draw(st.sampled_from([1, dim])))
    return tuple(shape)

def _draw_array(data, shape):
    size = _prod(shape)
    values = data.draw(
        st.lists(
            st.integers(min_value=-1_000_000, max_value=1_000_000),
            min_size=size,
            max_size=size,
        )
    )
    return numpy.array(values, dtype=numpy.int64).reshape(shape)

def _draw_operands(data):
    rank = data.draw(st.integers(min_value=0, max_value=3))
    target_shape = tuple(
        data.draw(
            st.lists(
                st.integers(min_value=1, max_value=4),
                min_size=rank,
                max_size=rank,
            )
        )
    )

    shape1 = _draw_broadcastable_shape(data, target_shape)
    shape2 = _draw_broadcastable_shape(data, target_shape)

    x1 = _draw_array(data, shape1)
    x2 = _draw_array(data, shape2)

    expected_shape = numpy.broadcast_arrays(x1, x2)[0].shape
    return x1, x2, expected_shape

def _assert_elementwise_sum(result, x1, x2):
    b1, b2 = numpy.broadcast_arrays(x1, x2)
    result_array = numpy.asarray(result)

    assert result_array.shape == b1.shape

    result_flat = numpy.ravel(result_array)
    b1_flat = numpy.ravel(b1)
    b2_flat = numpy.ravel(b2)

    for i in range(result_flat.size):
        assert int(result_flat[i]) == int(b1_flat[i]) + int(b2_flat[i])

@given(st.data())
def test_numpy_add_output_has_broadcast_shape_or_scalar_for_scalar_inputs(data):
    if data.draw(st.booleans()):
        x1 = data.draw(st.integers(min_value=-1_000_000, max_value=1_000_000))
        x2 = data.draw(st.integers(min_value=-1_000_000, max_value=1_000_000))

        result = numpy.add(x1, x2)

        assert numpy.isscalar(result)
    else:
        x1, x2, expected_shape = _draw_operands(data)

        result = numpy.add(x1, x2)

        assert numpy.shape(result) == expected_shape

@given(st.data())
def test_numpy_add_output_elements_equal_elementwise_sums(data):
    x1, x2, _ = _draw_operands(data)

    result = numpy.add(x1, x2)

    _assert_elementwise_sum(result, x1, x2)

@given(st.data())
def test_numpy_add_is_commutative_for_safe_integer_inputs(data):
    x1, x2, _ = _draw_operands(data)

    result_forward = numpy.add(x1, x2)
    result_reverse = numpy.add(x2, x1)

    assert numpy.array_equal(result_forward, result_reverse)

@given(st.data())
def test_numpy_add_writes_result_to_out_array(data):
    x1, x2, expected_shape = _draw_operands(data)

    out = numpy.full(expected_shape, -123456789, dtype=numpy.int64)

    returned = numpy.add(x1, x2, out=out)

    assert returned is out
    _assert_elementwise_sum(out, x1, x2)

@given(st.data())
def test_numpy_add_where_controls_which_out_values_are_updated(data):
    x1, x2, expected_shape = _draw_operands(data)

    where_shape = _draw_broadcastable_shape(data, expected_shape)
    where_size = _prod(where_shape)
    where_values = data.draw(
        st.lists(st.booleans(), min_size=where_size, max_size=where_size)
    )
    where = numpy.array(where_values, dtype=bool).reshape(where_shape)

    sentinel = -123456789
    out = numpy.full(expected_shape, sentinel, dtype=numpy.int64)
    original_out = out.copy()

    returned = numpy.add(x1, x2, out=out, where=where)

    assert returned is out

    b1, b2 = numpy.broadcast_arrays(x1, x2)
    broadcast_where = numpy.broadcast_to(where, expected_shape)

    out_flat = numpy.ravel(out)
    original_flat = numpy.ravel(original_out)
    b1_flat = numpy.ravel(b1)
    b2_flat = numpy.ravel(b2)
    where_flat = numpy.ravel(broadcast_where)

    for i in range(out_flat.size):
        if bool(where_flat[i]):
            assert int(out_flat[i]) == int(b1_flat[i]) + int(b2_flat[i])
        else:
            assert int(out_flat[i]) == int(original_flat[i]) == sentinel
# End program