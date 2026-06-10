from hypothesis import given, strategies as st
from hypothesis.extra import numpy as hnp
import numpy as np

# Summary: Generate broadcast-compatible scalar, 0-D, empty, and small multidimensional
# NumPy inputs across bool, signed/unsigned integer, float, and complex dtypes, including
# edge values such as NaN and infinity where supported. Also generate a broadcastable
# boolean `where` mask and a correctly shaped `out` array. Check that np.add matches
# ndarray `+` broadcasting semantics, returns the documented broadcast shape, returns a
# scalar for two scalar inputs, is commutative for addition, and honors `out`/`where` by
# writing only where the mask is True while preserving previous `out` values elsewhere.
@given(st.data())
def test_numpy_add(data):
    dtypes = [
        np.dtype("bool"),
        np.dtype("int8"),
        np.dtype("int16"),
        np.dtype("int64"),
        np.dtype("uint8"),
        np.dtype("uint16"),
        np.dtype("float32"),
        np.dtype("float64"),
        np.dtype("complex64"),
        np.dtype("complex128"),
    ]

    def draw_base_shape():
        ndim = data.draw(st.integers(min_value=0, max_value=3))
        return tuple(data.draw(st.integers(min_value=0, max_value=4)) for _ in range(ndim))

    def draw_broadcastable_shape(base_shape):
        if not base_shape or data.draw(st.booleans()):
            return ()

        start = data.draw(st.integers(min_value=0, max_value=len(base_shape)))
        shape = []
        for dim in base_shape[start:]:
            if dim in (0, 1):
                shape.append(dim)
            else:
                shape.append(data.draw(st.sampled_from([1, dim])))
        return tuple(shape)

    def draw_array(dtype, shape):
        return data.draw(
            hnp.arrays(
                dtype=dtype,
                shape=shape,
                elements=hnp.from_dtype(dtype),
            )
        )

    def maybe_convert_0d_array_to_scalar(value):
        if np.shape(value) == () and data.draw(st.booleans()):
            return value.item()
        return value

    base_shape = draw_base_shape()

    x1_shape = draw_broadcastable_shape(base_shape)
    x2_shape = draw_broadcastable_shape(base_shape)

    x1_dtype = data.draw(st.sampled_from(dtypes))
    x2_dtype = data.draw(st.sampled_from(dtypes))

    x1 = maybe_convert_0d_array_to_scalar(draw_array(x1_dtype, x1_shape))
    x2 = maybe_convert_0d_array_to_scalar(draw_array(x2_dtype, x2_shape))

    expected_shape = np.broadcast_shapes(np.shape(x1), np.shape(x2))

    with np.errstate(all="ignore"):
        actual = np.add(x1, x2)
        expected = np.asarray(x1) + np.asarray(x2)
        reversed_actual = np.add(x2, x1)

    np.testing.assert_array_equal(actual, expected)
    np.testing.assert_array_equal(actual, reversed_actual)
    assert np.asarray(actual).shape == expected_shape

    if np.isscalar(x1) and np.isscalar(x2):
        assert np.isscalar(actual)

    result_dtype = np.asarray(actual).dtype

    where_shape = draw_broadcastable_shape(expected_shape)
    where = draw_array(np.dtype("bool"), where_shape)
    if np.shape(where) == () and data.draw(st.booleans()):
        where = bool(where)

    out = draw_array(result_dtype, expected_shape)
    original_out = out.copy()

    with np.errstate(all="ignore"):
        returned = np.add(x1, x2, out=out, where=where)

    assert returned is out

    broadcast_where = np.broadcast_to(np.asarray(where, dtype=bool), expected_shape)
    expected_out = np.where(broadcast_where, np.asarray(actual), original_out)

    np.testing.assert_array_equal(out, expected_out)

# End program