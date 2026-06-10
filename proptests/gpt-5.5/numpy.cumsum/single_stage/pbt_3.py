from hypothesis import given, strategies as st
import numpy as np
import hypothesis.extra.numpy as hnp
import warnings

# Summary: Generate small 0-D to 3-D NumPy arrays with empty and non-empty shapes,
# booleans, signed/unsigned integers, and floats including NaN/inf. Randomly choose
# valid axis values, optional accumulator dtype, and optional out arrays with possibly
# different dtype. Check documented shape behavior, dtype/out behavior, and that values
# equal a simple sequential cumulative-sum model, including integer wraparound.

@given(st.data())
def test_numpy_cumsum(data):
    input_dtypes = [
        np.dtype("bool"),
        np.dtype("int8"),
        np.dtype("int16"),
        np.dtype("int32"),
        np.dtype("uint8"),
        np.dtype("uint16"),
        np.dtype("uint32"),
        np.dtype("float32"),
        np.dtype("float64"),
    ]

    accumulator_dtypes = [
        np.dtype("int8"),
        np.dtype("int16"),
        np.dtype("int64"),
        np.dtype("uint8"),
        np.dtype("uint16"),
        np.dtype("uint64"),
        np.dtype("float32"),
        np.dtype("float64"),
    ]

    out_dtypes = [
        np.dtype("bool"),
        np.dtype("int8"),
        np.dtype("int16"),
        np.dtype("int64"),
        np.dtype("uint8"),
        np.dtype("uint16"),
        np.dtype("uint64"),
        np.dtype("float32"),
        np.dtype("float64"),
    ]

    def elements_for(dtype):
        if np.issubdtype(dtype, np.bool_):
            return st.booleans()

        if np.issubdtype(dtype, np.signedinteger):
            info = np.iinfo(dtype)
            return st.integers(
                min_value=max(info.min, -20),
                max_value=min(info.max, 20),
            )

        if np.issubdtype(dtype, np.unsignedinteger):
            info = np.iinfo(dtype)
            return st.integers(
                min_value=0,
                max_value=min(info.max, 40),
            )

        if np.issubdtype(dtype, np.floating):
            width = 32 if dtype == np.dtype("float32") else 64
            finite = st.floats(
                min_value=-1e6,
                max_value=1e6,
                allow_nan=False,
                allow_infinity=False,
                width=width,
            )
            special = st.sampled_from([np.nan, np.inf, -np.inf, 0.0, -0.0])
            return st.one_of(finite, special)

        raise AssertionError(f"unsupported dtype: {dtype}")

    def default_cumsum_dtype(arr_dtype):
        arr_dtype = np.dtype(arr_dtype)
        default_int = np.dtype(np.int_)

        if (
            np.issubdtype(arr_dtype, np.integer)
            or np.issubdtype(arr_dtype, np.bool_)
        ) and arr_dtype.itemsize < default_int.itemsize:
            return default_int

        return arr_dtype

    def cast_scalar_to_dtype(value, dtype):
        return np.asarray(value).astype(dtype, casting="unsafe", copy=False)

    def manual_cumsum(arr, axis, accumulator_dtype):
        arr = np.asarray(arr)
        accumulator_dtype = np.dtype(accumulator_dtype)

        with np.errstate(all="ignore"):
            if axis is None:
                flat = arr.ravel()
                expected = np.empty(flat.shape, dtype=accumulator_dtype)
                total = np.zeros((), dtype=accumulator_dtype)

                for i, value in enumerate(flat):
                    term = cast_scalar_to_dtype(value, accumulator_dtype)
                    total[...] = np.add(total, term)
                    expected[i] = total

                return expected

            axis = np.core.numeric.normalize_axis_index(axis, arr.ndim)
            moved = np.moveaxis(arr, axis, 0)
            expected_moved = np.empty(moved.shape, dtype=accumulator_dtype)

            for rest_index in np.ndindex(moved.shape[1:]):
                total = np.zeros((), dtype=accumulator_dtype)

                for i in range(moved.shape[0]):
                    full_index = (i,) + rest_index
                    term = cast_scalar_to_dtype(moved[full_index], accumulator_dtype)
                    total[...] = np.add(total, term)
                    expected_moved[full_index] = total

            return np.moveaxis(expected_moved, 0, axis)

    ndim = data.draw(st.integers(min_value=0, max_value=3))
    shape = tuple(
        data.draw(st.lists(st.integers(min_value=0, max_value=4), min_size=ndim, max_size=ndim))
    )

    input_dtype = data.draw(st.sampled_from(input_dtypes))
    a = data.draw(
        hnp.arrays(
            dtype=input_dtype,
            shape=shape,
            elements=elements_for(input_dtype),
        )
    )

    if ndim == 0:
        axis = None
    else:
        axis = data.draw(st.one_of(st.none(), st.integers(min_value=-ndim, max_value=ndim - 1)))

    dtype = data.draw(st.one_of(st.none(), st.sampled_from(accumulator_dtypes)))

    expected_shape = (a.size,) if axis is None else a.shape
    accumulator_dtype = np.dtype(dtype) if dtype is not None else default_cumsum_dtype(a.dtype)

    use_out = data.draw(st.booleans())
    if use_out:
        out_dtype = data.draw(st.sampled_from(out_dtypes))
        out = np.empty(expected_shape, dtype=out_dtype)
    else:
        out = None

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        result = np.cumsum(a, axis=axis, dtype=dtype, out=out)
        expected = manual_cumsum(a, axis=axis, accumulator_dtype=accumulator_dtype)

        if out is not None:
            assert result is out
            assert result.dtype == out.dtype
            expected = expected.astype(out.dtype, casting="unsafe", copy=False)
        else:
            assert result.dtype == accumulator_dtype

    assert result.shape == expected_shape

    if np.issubdtype(result.dtype, np.floating):
        np.testing.assert_allclose(result, expected, rtol=0, atol=0, equal_nan=True)
    else:
        np.testing.assert_array_equal(result, expected)

# End program