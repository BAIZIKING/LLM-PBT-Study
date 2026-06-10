from hypothesis import given, strategies as st
import numpy

def _prod(shape):
    result = 1
    for dim in shape:
        result *= dim
    return result

def _indices(shape):
    if shape == ():
        yield ()
    else:
        for index in numpy.ndindex(shape):
            yield index

def _draw_shape(data, max_dims=3, min_dim=1, max_dim=4):
    ndim = data.draw(st.integers(min_value=0, max_value=max_dims))
    return tuple(
        data.draw(st.integers(min_value=min_dim, max_value=max_dim))
        for _ in range(ndim)
    )

def _draw_array(data, shape, min_value=-1_000_000, max_value=1_000_000):
    size = _prod(shape)
    values = data.draw(
        st.lists(
            st.integers(min_value=min_value, max_value=max_value),
            min_size=size,
            max_size=size,
        )
    )
    return numpy.array(values, dtype=numpy.int64).reshape(shape)

def _draw_bool_array(data, shape):
    size = _prod(shape)
    values = data.draw(
        st.lists(st.booleans(), min_size=size, max_size=size)
    )
    return numpy.array(values, dtype=bool).reshape(shape)

def _draw_broadcastable_arrays(data):
    ndim = data.draw(st.integers(min_value=0, max_value=3))
    common_shape = tuple(
        data.draw(st.integers(min_value=1, max_value=4))
        for _ in range(ndim)
    )

    shape1 = []
    shape2 = []
    for dim in common_shape:
        if dim == 1:
            shape1.append(1)
            shape2.append(1)
        else:
            shape1.append(data.draw(st.sampled_from([1, dim])))
            shape2.append(data.draw(st.sampled_from([1, dim])))

    shape1 = tuple(shape1)
    shape2 = tuple(shape2)

    x1 = _draw_array(data, shape1)
    x2 = _draw_array(data, shape2)
    return x1, x2, common_shape

def _operand_index(common_index, operand_shape):
    if operand_shape == ():
        return ()
    return tuple(
        0 if dim == 1 else idx
        for idx, dim in zip(common_index, operand_shape)
    )

@given(st.data())
def test_numpy_add_elementwise_sum_property(data):
    x1, x2, common_shape = _draw_broadcastable_arrays(data)

    result = numpy.add(x1, x2)

    for index in _indices(common_shape):
        index1 = _operand_index(index, x1.shape)
        index2 = _operand_index(index, x2.shape)
        assert int(result[index]) == int(x1[index1]) + int(x2[index2])

@given(st.data())
def test_numpy_add_broadcast_output_shape_property(data):
    x1, x2, common_shape = _draw_broadcastable_arrays(data)

    result = numpy.add(x1, x2)

    assert result.shape == common_shape

@given(st.data())
def test_numpy_add_scalar_output_property(data):
    x1 = data.draw(st.integers(min_value=-1_000_000, max_value=1_000_000))
    x2 = data.draw(st.integers(min_value=-1_000_000, max_value=1_000_000))

    result = numpy.add(x1, x2)

    assert numpy.isscalar(result)
    assert int(result) == x1 + x2

@given(st.data())
def test_numpy_add_out_return_and_where_true_property(data):
    shape = _draw_shape(data)
    x1 = _draw_array(data, shape)
    x2 = _draw_array(data, shape)
    out = _draw_array(data, shape)
    where = _draw_bool_array(data, shape)
    where.flat[0] = True

    result = numpy.add(x1, x2, out=out, where=where)

    assert result is out
    for index in _indices(shape):
        if bool(where[index]):
            assert int(out[index]) == int(x1[index]) + int(x2[index])

@given(st.data())
def test_numpy_add_where_false_retains_out_property(data):
    shape = _draw_shape(data)
    x1 = _draw_array(data, shape)
    x2 = _draw_array(data, shape)
    out = _draw_array(data, shape)
    original_out = out.copy()
    where = _draw_bool_array(data, shape)
    where.flat[0] = False

    numpy.add(x1, x2, out=out, where=where)

    for index in _indices(shape):
        if not bool(where[index]):
            assert int(out[index]) == int(original_out[index])

# End program