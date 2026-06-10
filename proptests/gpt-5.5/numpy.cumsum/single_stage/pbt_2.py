from hypothesis import given, strategies as st
import hypothesis.extra.numpy as hnp
import numpy as np


ALL_DTYPES = [
    np.dtype(np.bool_),
    np.dtype(np.int8),
    np.dtype(np.uint8),
    np.dtype(np.int16),
    np.dtype(np.uint16),
    np.dtype(np.int32),
    np.dtype(np.uint32),
    np.dtype(np.int64),
    np.dtype(np.uint64),
    np.dtype(np.float16),
    np.dtype(np.float32),
    np.dtype(np.float64),
]


def _default_cumsum_dtype(dtype):
    dtype = np.dtype(dtype)
    int_dtype = np.dtype(np.int_)
    uint_dtype = np.dtype(np.uint)

    if dtype.kind == "b":
        return int_dtype
    if dtype.kind == "i" and dtype.itemsize < int_dtype.itemsize:
        return int_dtype
    if dtype.kind == "u" and dtype.itemsize < uint_dtype.itemsize:
        return uint_dtype
    return dtype


def _dtype_parameter_choices(input_dtype):
    input_dtype = np.dtype(input_dtype)
    default_dtype = _default_cumsum_dtype(input_dtype)

    if input_dtype.kind == "b":
        choices = [None, input_dtype, default_dtype, np.dtype(np.int8), np.dtype(np.float64)]
    elif input_dtype.kind == "i":
        choices = [
            None,
            input_dtype,
            default_dtype,
            np.dtype(np.int8),
            np.dtype(np.int16),
            np.dtype(np.int32),
            np.dtype(np.int64),
            np.dtype(np.float32),
            np.dtype(np.float64),
        ]
    elif input_dtype.kind == "u":
        choices = [
            None,
            input_dtype,
            default_dtype,
            np.dtype(np.uint8),
            np.dtype(np.uint16),
            np.dtype(np.uint32),
            np.dtype(np.uint64),
            np.dtype(np.float32),
            np.dtype(np.float64),
        ]
    else:
        choices = [
            None,
            input_dtype,
            np.dtype(np.float16),
            np.dtype(np.float32),
            np.dtype(np.float64),
        ]

    deduped = []
    for choice in choices:
        if choice not in deduped:
            deduped.append(choice)
    return deduped


def _safe_out_dtype_choices(acc_dtype):
    acc_dtype = np.dtype(acc_dtype)
    choices = [dt for dt in ALL_DTYPES if np.can_cast(acc_dtype, dt, casting="safe")]
    return choices or [acc_dtype]


def _reference_cumsum(a, axis, acc_dtype, out_dtype):
    a = np.asarray(a)
    acc_dtype = np.dtype(acc_dtype)
    out_dtype = np.dtype(out_dtype)

    if axis is None:
        values = a.ravel()
        result = np.empty(values.shape, dtype=out_dtype)
        total = np.zeros((), dtype=acc_dtype)[()]

        for i, value in enumerate(values):
            value = np.asarray(value, dtype=acc_dtype)[()]
            total = np.asarray(total + value, dtype=acc_dtype)[()]
            result[i] = total

        return result

    axis = axis % a.ndim
    result = np.empty(a.shape, dtype=out_dtype)
    prefix_shape = a.shape[:axis] + a.shape[axis + 1 :]

    for prefix in np.ndindex(prefix_shape):
        total = np.zeros((), dtype=acc_dtype)[()]

        for i in range(a.shape[axis]):
            index = prefix[:axis] + (i,) + prefix[axis:]
            value = np.asarray(a[index], dtype=acc_dtype)[()]
            total = np.asarray(total + value, dtype=acc_dtype)[()]
            result[index] = total

    return result


# Summary: Generates small scalar, empty, 1-D, and multi-D arrays across bool, signed/unsigned integer, and floating dtypes; draws axis=None or valid positive/negative axes, optional compatible dtype values, and optional out arrays. Checks documented shape behavior, dtype/out behavior, and cumulative sequential-sum values including integer overflow and NaN handling.
@given(st.data())
def test_numpy_cumsum(data):
    input_dtype = data.draw(st.sampled_from(ALL_DTYPES))
    shape = data.draw(st.lists(st.integers(0, 4), min_size=0, max_size=3).map(tuple))

    if input_dtype.kind == "f":
        elements = hnp.from_dtype(input_dtype, allow_nan=True, allow_infinity=True)
    else:
        elements = hnp.from_dtype(input_dtype)

    a = data.draw(hnp.arrays(dtype=input_dtype, shape=shape, elements=elements))

    if a.ndim == 0:
        axis = None
    else:
        axis = data.draw(st.one_of(st.none(), st.integers(-a.ndim, a.ndim - 1)))

    dtype_arg = data.draw(st.sampled_from(_dtype_parameter_choices(input_dtype)))
    acc_dtype = np.dtype(dtype_arg) if dtype_arg is not None else _default_cumsum_dtype(input_dtype)

    expected_shape = (a.size,) if axis is None else a.shape

    use_out = data.draw(st.booleans())
    if use_out:
        out_dtype = data.draw(st.sampled_from(_safe_out_dtype_choices(acc_dtype)))
        out = np.empty(expected_shape, dtype=out_dtype)
    else:
        out_dtype = acc_dtype
        out = None

    with np.errstate(over="ignore", invalid="ignore", under="ignore"):
        result = np.cumsum(a, axis=axis, dtype=dtype_arg, out=out)
        expected = _reference_cumsum(a, axis=axis, acc_dtype=acc_dtype, out_dtype=out_dtype)

    assert result.shape == expected_shape

    if use_out:
        assert result is out
        assert result.dtype == out_dtype
    else:
        assert result.dtype == acc_dtype

    if np.issubdtype(result.dtype, np.floating):
        np.testing.assert_allclose(result, expected, rtol=0, atol=0, equal_nan=True)
    else:
        np.testing.assert_array_equal(result, expected)
# End program