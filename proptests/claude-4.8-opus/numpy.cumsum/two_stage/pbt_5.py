from hypothesis import given, strategies as st, settings
import hypothesis.extra.numpy as hnp
import numpy as np


# ---------- Strategies ----------

safe_float_dtypes = st.sampled_from([np.float32, np.float64])
safe_int_dtypes = st.sampled_from([np.int32, np.int64])
all_safe_dtypes = st.one_of(safe_float_dtypes, safe_int_dtypes)


def array_strategy(dtype):
    if np.issubdtype(np.dtype(dtype), np.floating):
        elements = st.floats(
            min_value=-1e6, max_value=1e6,
            allow_nan=False, allow_infinity=False,
        )
    else:
        # Keep integers small so the cumulative sum cannot overflow.
        elements = st.integers(min_value=-1000, max_value=1000)
    return hnp.arrays(
        dtype=dtype,
        shape=hnp.array_shapes(min_dims=1, max_dims=3, min_side=1, max_side=8),
        elements=elements,
    )


def axis_for(arr):
    return st.one_of(
        st.none(),
        st.integers(min_value=0, max_value=arr.ndim - 1),
    )


# ---------- Tests ----------

@given(st.data())
@settings(max_examples=200)
def test_numpy_cumsum_property_size_preserved(data):
    dtype = data.draw(all_safe_dtypes)
    a = data.draw(array_strategy(dtype))
    axis = data.draw(axis_for(a))
    result = np.cumsum(a, axis=axis)
    assert result.size == a.size


@given(st.data())
@settings(max_examples=200)
def test_numpy_cumsum_property_last_equals_total_sum(data):
    dtype = data.draw(all_safe_dtypes)
    a = data.draw(array_strategy(dtype))
    axis = data.draw(axis_for(a))
    result = np.cumsum(a, axis=axis)
    total = np.sum(a, axis=axis)
    if axis is None:
        last = result[-1]
    else:
        last = np.take(result, indices=result.shape[axis] - 1, axis=axis)
    if np.issubdtype(np.dtype(dtype), np.floating):
        assert np.allclose(last, total, rtol=1e-5, atol=1e-3)
    else:
        assert np.array_equal(last, total)


@given(st.data())
@settings(max_examples=200)
def test_numpy_cumsum_property_first_equals_input_first(data):
    dtype = data.draw(all_safe_dtypes)
    a = data.draw(array_strategy(dtype))
    axis = data.draw(axis_for(a))
    result = np.cumsum(a, axis=axis)
    if axis is None:
        flat_a = a.flatten()
        first_result = result[0]
        first_input = flat_a[0]
    else:
        first_result = np.take(result, indices=0, axis=axis)
        first_input = np.take(a, indices=0, axis=axis)
    if np.issubdtype(np.dtype(dtype), np.floating):
        assert np.allclose(first_result, first_input, rtol=1e-5, atol=1e-3)
    else:
        assert np.array_equal(first_result, first_input)


@given(st.data())
@settings(max_examples=200)
def test_numpy_cumsum_property_diff_recovers_input(data):
    dtype = data.draw(all_safe_dtypes)
    a = data.draw(array_strategy(dtype))
    axis = data.draw(axis_for(a))
    result = np.cumsum(a, axis=axis)
    if axis is None:
        flat_a = a.flatten()
        recovered = np.diff(result)
        expected = flat_a[1:]
    else:
        recovered = np.diff(result, axis=axis)
        # expected is a with the first slice along axis removed
        idx = [slice(None)] * a.ndim
        idx[axis] = slice(1, None)
        expected = a[tuple(idx)]
    if np.issubdtype(np.dtype(dtype), np.floating):
        assert np.allclose(recovered, expected, rtol=1e-4, atol=1e-2)
    else:
        assert np.array_equal(recovered, expected)


@given(st.data())
@settings(max_examples=200)
def test_numpy_cumsum_property_dtype_handling(data):
    dtype = data.draw(all_safe_dtypes)
    a = data.draw(array_strategy(dtype))
    axis = data.draw(axis_for(a))
    # Explicit dtype case
    out_dtype = data.draw(st.sampled_from([None, np.float64, np.int64]))
    if out_dtype is None:
        result = np.cumsum(a, axis=axis)
        # Output dtype matches input, except low-precision integers get promoted
        # to the platform default integer.
        if np.issubdtype(a.dtype, np.integer) and a.dtype.itemsize < np.dtype(np.intp).itemsize:
            assert result.dtype == np.dtype(np.intp)
        else:
            assert result.dtype == a.dtype
    else:
        result = np.cumsum(a, axis=axis, dtype=out_dtype)
        assert result.dtype == np.dtype(out_dtype)
# End program