from hypothesis import given, strategies as st
from hypothesis.extra import numpy as hnp
import numpy as np

# Summary: Generate int64 and float64 inputs as Python scalars, 0-d arrays, and
# ndarrays with ranks 0..3, including empty dimensions, singleton dimensions,
# NaN, infinities, and signed/large floats. Operand shapes are constructed to be
# broadcastable to a shared result shape. The test sometimes supplies an `out`
# array and a broadcastable `where` mask to cover the documented optional
# behavior.
#
# Properties checked: np.add(x1, x2) has the same elementwise values as x1 + x2,
# uses the documented broadcasted shape, and returns a scalar when both inputs
# are scalars. When `out` and `where` are supplied, np.add returns the same `out`
# object, writes sums where `where` is True, and preserves the original `out`
# values where `where` is False.
@given(st.data())
def test_numpy_add(data):
    dtype = data.draw(st.sampled_from([np.int64, np.float64]))

    if np.issubdtype(dtype, np.integer):
        elements = st.integers(min_value=-10**6, max_value=10**6)
    else:
        elements = st.floats(width=64, allow_nan=True, allow_infinity=True)

    rank = data.draw(st.integers(min_value=0, max_value=3))
    result_shape = tuple(
        data.draw(st.integers(min_value=0, max_value=4))
        for _ in range(rank)
    )

    x1_dims = []
    x2_dims = []
    for dim in result_shape:
        if dim == 0:
            d1, d2 = 0, 0
        elif dim == 1:
            d1, d2 = 1, 1
        else:
            d1, d2 = data.draw(st.sampled_from([(dim, dim), (dim, 1), (1, dim)]))
        x1_dims.append(d1)
        x2_dims.append(d2)

    x1_shape = tuple(x1_dims)
    x2_shape = tuple(x2_dims)

    def draw_array_like(shape):
        if shape == () and data.draw(st.booleans()):
            return data.draw(elements)
        return data.draw(hnp.arrays(dtype=dtype, shape=shape, elements=elements))

    x1 = draw_array_like(x1_shape)
    x2 = draw_array_like(x2_shape)

    def assert_same_values(actual, expected):
        assert np.array_equal(np.asarray(actual), np.asarray(expected), equal_nan=True)

    use_out = data.draw(st.booleans())

    with np.errstate(all="ignore"):
        if not use_out:
            result = np.add(x1, x2)
            expected = x1 + x2

            assert np.shape(result) == np.broadcast_shapes(np.shape(x1), np.shape(x2))
            assert_same_values(result, expected)

            if np.isscalar(x1) and np.isscalar(x2):
                assert np.isscalar(result)

        else:
            out = data.draw(hnp.arrays(dtype=dtype, shape=result_shape, elements=elements))
            original_out = np.array(out, copy=True)

            if result_shape == () or data.draw(st.booleans()):
                where_shape = ()
            else:
                where_shape = tuple(
                    0 if dim == 0 else data.draw(st.sampled_from([1, dim]))
                    for dim in result_shape
                )

            if where_shape == () and data.draw(st.booleans()):
                where = data.draw(st.booleans())
            else:
                where = data.draw(
                    hnp.arrays(dtype=np.bool_, shape=where_shape, elements=st.booleans())
                )

            result = np.add(x1, x2, out=out, where=where)

            raw_sum = x1 + x2
            mask = np.broadcast_to(where, result_shape)
            expected_out = np.where(mask, raw_sum, original_out)

            assert result is out
            assert out.shape == result_shape
            assert_same_values(out, expected_out)

# End program