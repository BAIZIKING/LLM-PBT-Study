from hypothesis import given, strategies as st
from hypothesis.extra import numpy as hnp
import numpy as np

# Summary: Generate broadcast-compatible scalar/array inputs with ranks 0-3, dimensions including 0 and 1,
# mixed integer and floating dtypes, bounded integer values to avoid accidental Python-vs-NumPy overflow
# differences, and float edge cases including NaN and infinity. Randomly exercise default output allocation,
# explicit out arrays, and where masks broadcastable to the result. Check that np.add is equivalent to x1 + x2,
# that broadcasting determines the output shape, that out is returned and filled, and that where=False locations
# preserve the original out values.
@given(st.data())
def test_numpy_add(data):
    dtypes = st.sampled_from([
        np.dtype(np.int8),
        np.dtype(np.int16),
        np.dtype(np.int64),
        np.dtype(np.float16),
        np.dtype(np.float32),
        np.dtype(np.float64),
    ])

    def elements_for(dtype):
        if np.issubdtype(dtype, np.integer):
            info = np.iinfo(dtype)
            return st.integers(
                min_value=max(int(info.min) // 4, -1_000_000),
                max_value=min(int(info.max) // 4, 1_000_000),
            )

        width = {
            np.dtype(np.float16): 16,
            np.dtype(np.float32): 32,
            np.dtype(np.float64): 64,
        }[dtype]
        return st.floats(width=width, allow_nan=True, allow_infinity=True)

    def shape_broadcastable_to(target_shape):
        if not target_shape:
            return ()

        start = data.draw(
            st.integers(min_value=0, max_value=len(target_shape)),
            label="number_of_leading_dimensions_to_omit",
        )
        tail = target_shape[start:]

        result = []
        for dim in tail:
            if dim == 1:
                result.append(1)
            else:
                result.append(data.draw(st.sampled_from([1, dim]), label="broadcast_dimension"))
        return tuple(result)

    def draw_value(dtype, shape, label):
        arr = data.draw(
            hnp.arrays(dtype=dtype, shape=shape, elements=elements_for(dtype)),
            label=label,
        )

        if shape == () and data.draw(st.booleans(), label=f"{label}_as_python_scalar"):
            return arr.item()
        return arr

    target_shape = data.draw(
        st.lists(st.integers(min_value=0, max_value=4), min_size=0, max_size=3).map(tuple),
        label="target_broadcast_shape",
    )

    x1_dtype = data.draw(dtypes, label="x1_dtype")
    x2_dtype = data.draw(dtypes, label="x2_dtype")

    x1_shape = shape_broadcastable_to(target_shape)
    x2_shape = shape_broadcastable_to(target_shape)

    x1 = draw_value(x1_dtype, x1_shape, "x1")
    x2 = draw_value(x2_dtype, x2_shape, "x2")

    with np.errstate(all="ignore"):
        expected = x1 + x2
        result_shape = np.broadcast_shapes(np.shape(x1), np.shape(x2))

    use_where = data.draw(st.booleans(), label="use_where")
    use_out = use_where or data.draw(st.booleans(), label="use_out")

    def assert_same_array_like(actual, expected_value):
        actual_arr = np.asarray(actual)
        expected_arr = np.asarray(expected_value)

        assert actual_arr.shape == expected_arr.shape

        if np.issubdtype(actual_arr.dtype, np.floating) or np.issubdtype(expected_arr.dtype, np.floating):
            np.testing.assert_allclose(actual_arr, expected_arr, rtol=0, atol=0, equal_nan=True)
        else:
            np.testing.assert_array_equal(actual_arr, expected_arr)

    if use_out:
        out_dtype = np.asarray(expected).dtype
        out = data.draw(
            hnp.arrays(dtype=out_dtype, shape=result_shape, elements=elements_for(out_dtype)),
            label="out",
        )
        out_before = out.copy()

        if use_where:
            where_shape = shape_broadcastable_to(result_shape)
            where = data.draw(
                hnp.arrays(dtype=np.bool_, shape=where_shape),
                label="where",
            )
            if where_shape == () and data.draw(st.booleans(), label="where_as_python_bool"):
                where = bool(where)

            expected_out = out_before.copy()
            with np.errstate(all="ignore"):
                np.copyto(expected_out, expected, where=where)
                result = np.add(x1, x2, out=out, where=where)

            assert result is out
            assert_same_array_like(result, expected_out)
        else:
            with np.errstate(all="ignore"):
                result = np.add(x1, x2, out=out)

            assert result is out
            assert_same_array_like(result, expected)
    else:
        with np.errstate(all="ignore"):
            result = np.add(x1, x2)

        assert np.shape(result) == result_shape
        assert_same_array_like(result, expected)
# End program