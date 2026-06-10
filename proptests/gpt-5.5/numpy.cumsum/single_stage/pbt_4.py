from hypothesis import given, strategies as st

# Summary: Generate scalar, empty, 1-D, and small multi-dimensional arrays with bool,
# signed/unsigned integer, and floating dtypes; include boundary integer values and
# float edge values such as +/-0 and tiny magnitudes. Generate axis=None or any valid
# positive/negative axis, optional dtype accumulators, and optional out arrays with
# varied dtypes. Check documented properties: output shape, dtype behavior, returning
# out by identity when supplied, and element values against an independent sequential
# cumulative-sum reference that respects accumulator dtype and casts to out if needed.
@given(st.data())
def test_numpy_cumsum(data):
    import numpy as np

    input_dtype = np.dtype(
        data.draw(
            st.sampled_from(
                ["bool", "int8", "int16", "int32", "int64",
                 "uint8", "uint16", "uint32", "uint64",
                 "float32", "float64"]
            )
        )
    )

    ndim = data.draw(st.integers(min_value=0, max_value=3))
    if ndim == 0:
        shape = ()
    else:
        shape = tuple(
            data.draw(
                st.lists(
                    st.integers(min_value=0, max_value=4),
                    min_size=ndim,
                    max_size=ndim,
                )
            )
        )

    size = 1
    for dim in shape:
        size *= dim

    def element_strategy(dtype):
        if dtype.kind == "b":
            return st.booleans()

        if dtype.kind in "iu":
            info = np.iinfo(dtype)
            specials = [x for x in [info.min, info.max, -1, 0, 1] if info.min <= x <= info.max]
            return st.one_of(
                st.integers(min_value=int(info.min), max_value=int(info.max)),
                st.sampled_from(specials),
            )

        width = 32 if dtype == np.dtype("float32") else 64
        finfo = np.finfo(dtype)
        return st.one_of(
            st.floats(
                min_value=-1.0,
                max_value=1.0,
                allow_nan=False,
                allow_infinity=False,
                width=width,
            ),
            st.sampled_from([0.0, -0.0, 1.0, -1.0, float(finfo.tiny), -float(finfo.tiny)]),
        )

    flat_values = data.draw(
        st.lists(
            element_strategy(input_dtype),
            min_size=size,
            max_size=size,
        )
    )
    a = np.array(flat_values, dtype=input_dtype).reshape(shape)

    if ndim == 0:
        axis = None
    else:
        axis = data.draw(st.one_of(st.none(), st.integers(min_value=-ndim, max_value=ndim - 1)))

    if input_dtype.kind == "f":
        dtype_choices = [None, "int8", "int64", "float32", "float64"]
    else:
        dtype_choices = [None, "int8", "int16", "int64", "uint8", "uint16", "uint64", "float32", "float64"]

    dtype_name = data.draw(st.sampled_from(dtype_choices))
    dtype_arg = None if dtype_name is None else np.dtype(dtype_name)

    def inferred_accumulator_dtype(arr_dtype):
        arr_dtype = np.dtype(arr_dtype)
        if arr_dtype.kind == "b":
            return np.dtype(np.int_)
        if arr_dtype.kind == "i" and arr_dtype.itemsize < np.dtype(np.int_).itemsize:
            return np.dtype(np.int_)
        if arr_dtype.kind == "u" and arr_dtype.itemsize < np.dtype(np.uint).itemsize:
            return np.dtype(np.uint)
        return arr_dtype

    acc_dtype = np.dtype(dtype_arg) if dtype_arg is not None else inferred_accumulator_dtype(a.dtype)

    out_shape = (a.size,) if axis is None else a.shape
    use_out = data.draw(st.booleans())

    out = None
    if use_out:
        out_dtype = np.dtype(
            data.draw(
                st.sampled_from(["bool", "int8", "int64", "uint8", "uint64", "float32", "float64"])
            )
        )
        out = np.empty(out_shape, dtype=out_dtype)

    def cast_scalar(x, dtype):
        return np.asarray(x).astype(dtype, casting="unsafe")[()]

    def sequential_cumsum_reference(arr, axis_value, accumulator_dtype):
        if axis_value is None:
            src = arr.ravel()
            ref = np.empty(src.shape, dtype=accumulator_dtype)
            acc = cast_scalar(0, accumulator_dtype)

            with np.errstate(all="ignore"):
                for i, x in enumerate(src):
                    acc = cast_scalar(acc + cast_scalar(x, accumulator_dtype), accumulator_dtype)
                    ref[i] = acc

            return ref

        normalized_axis = axis_value % arr.ndim
        ref = np.empty(arr.shape, dtype=accumulator_dtype)

        moved_src = np.moveaxis(arr, normalized_axis, 0)
        moved_ref = np.moveaxis(ref, normalized_axis, 0)

        with np.errstate(all="ignore"):
            for trailing_index in np.ndindex(moved_src.shape[1:]):
                acc = cast_scalar(0, accumulator_dtype)
                for i in range(moved_src.shape[0]):
                    full_index = (i,) + trailing_index
                    acc = cast_scalar(
                        acc + cast_scalar(moved_src[full_index], accumulator_dtype),
                        accumulator_dtype,
                    )
                    moved_ref[full_index] = acc

        return ref

    with np.errstate(all="ignore"):
        expected = sequential_cumsum_reference(a, axis, acc_dtype)
        if out is not None:
            expected = expected.astype(out.dtype, casting="unsafe", copy=False)

        result = np.cumsum(a, axis=axis, dtype=dtype_arg, out=out)

    assert result.shape == out_shape

    if out is not None:
        assert result is out
        assert result.dtype == out.dtype
    else:
        assert result.dtype == acc_dtype

    if np.issubdtype(result.dtype, np.floating):
        np.testing.assert_allclose(result, expected, rtol=0, atol=0, equal_nan=True)
    else:
        np.testing.assert_array_equal(result, expected)
# End program