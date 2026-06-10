from hypothesis import given, strategies as st
import warnings
import numpy as np
import hypothesis.extra.numpy as hnp


NUMERIC_DTYPES = [
    np.dtype(bool),
    np.dtype(np.int8),
    np.dtype(np.int16),
    np.dtype(np.int64),
    np.dtype(np.uint8),
    np.dtype(np.uint16),
    np.dtype(np.uint64),
    np.dtype(np.float32),
    np.dtype(np.float64),
    np.dtype(np.complex64),
    np.dtype(np.complex128),
]


def _unique_dtypes(dtypes):
    out = []
    for dt in map(np.dtype, dtypes):
        if dt not in out:
            out.append(dt)
    return out


def _effective_accumulator_dtype(input_dtype, requested_dtype):
    if requested_dtype is not None:
        return np.dtype(requested_dtype)

    input_dtype = np.dtype(input_dtype)

    if input_dtype.kind == "b":
        return np.dtype(np.int_)

    if input_dtype.kind == "i" and input_dtype.itemsize < np.dtype(np.int_).itemsize:
        return np.dtype(np.int_)

    if input_dtype.kind == "u" and input_dtype.itemsize < np.dtype(np.uint).itemsize:
        return np.dtype(np.uint)

    return input_dtype


def _dtype_choices_for(input_dtype):
    input_dtype = np.dtype(input_dtype)

    if input_dtype.kind == "b":
        return _unique_dtypes([None, np.int64, np.float64, np.complex128])

    if input_dtype.kind == "i":
        return _unique_dtypes([None, input_dtype, np.int64, np.float64, np.complex128])

    if input_dtype.kind == "u":
        return _unique_dtypes([None, input_dtype, np.uint64, np.float64, np.complex128])

    if input_dtype.kind == "f":
        return _unique_dtypes([None, input_dtype, np.float64, np.complex128])

    if input_dtype.kind == "c":
        return _unique_dtypes([None, input_dtype, np.complex128])

    raise AssertionError(f"unexpected dtype: {input_dtype}")


def _out_dtype_choices(accumulator_dtype):
    accumulator_dtype = np.dtype(accumulator_dtype)

    if accumulator_dtype.kind in "biu":
        return _unique_dtypes([accumulator_dtype, np.float64, np.complex128])

    if accumulator_dtype.kind == "f":
        return _unique_dtypes([accumulator_dtype, np.float64, np.complex128])

    if accumulator_dtype.kind == "c":
        return _unique_dtypes([accumulator_dtype, np.complex128])

    raise AssertionError(f"unexpected accumulator dtype: {accumulator_dtype}")


def _reference_cumsum(a, axis, accumulator_dtype):
    accumulator_dtype = np.dtype(accumulator_dtype)
    expected_shape = (a.size,) if axis is None else a.shape
    expected = np.empty(expected_shape, dtype=accumulator_dtype)

    with np.errstate(all="ignore"):
        if axis is None:
            total = accumulator_dtype.type(0)
            for i, value in enumerate(np.ravel(a)):
                total = total + accumulator_dtype.type(value)
                expected[i] = total
            return expected

        if axis < 0:
            axis += a.ndim

        outer_shape = a.shape[:axis] + a.shape[axis + 1 :]

        for outer_index in np.ndindex(outer_shape):
            total = accumulator_dtype.type(0)
            for axis_index in range(a.shape[axis]):
                full_index = list(outer_index)
                full_index.insert(axis, axis_index)
                full_index = tuple(full_index)

                total = total + accumulator_dtype.type(a[full_index])
                expected[full_index] = total

        return expected


def _assert_same_values(actual, expected):
    if np.asarray(actual).dtype.kind in "fc" or np.asarray(expected).dtype.kind in "fc":
        np.testing.assert_allclose(actual, expected, rtol=0, atol=0, equal_nan=True)
    else:
        assert np.array_equal(actual, expected)


# Summary: Generate numeric arrays with 0 to 3 dimensions, including scalar arrays, empty axes,
# small shapes, booleans, signed/unsigned integers, floats, and complex numbers. Generate valid
# axis values including None and negative axes. Generate dtype=None plus compatible explicit
# accumulator dtypes, including smaller integer dtypes to exercise documented modular overflow.
# Sometimes generate an out array with the documented expected output shape and a safely castable
# dtype. Properties checked: result shape follows axis=None flattening or preserves shape for an
# explicit axis; result dtype follows dtype/default accumulator rules unless out is supplied;
# values equal an independent sequential cumulative-sum reference; integer overflow is accepted
# as modular NumPy scalar arithmetic; and when out is supplied, numpy.cumsum returns that same
# object and stores the cast result in it.
@given(st.data())
def test_numpy_cumsum(data):
    ndim = data.draw(st.integers(min_value=0, max_value=3), label="ndim")
    if ndim == 0:
        shape = ()
    else:
        shape = tuple(
            data.draw(
                st.lists(
                    st.integers(min_value=0, max_value=4),
                    min_size=ndim,
                    max_size=ndim,
                ),
                label="shape",
            )
        )

    input_dtype = data.draw(st.sampled_from(NUMERIC_DTYPES), label="input_dtype")
    a = data.draw(hnp.arrays(dtype=input_dtype, shape=shape), label="a")

    if ndim == 0:
        axis = None
    else:
        axis = data.draw(
            st.sampled_from([None] + list(range(-ndim, ndim))),
            label="axis",
        )

    requested_dtype = data.draw(
        st.sampled_from(_dtype_choices_for(input_dtype)),
        label="dtype",
    )

    accumulator_dtype = _effective_accumulator_dtype(input_dtype, requested_dtype)
    expected = _reference_cumsum(a, axis, accumulator_dtype)
    expected_shape = expected.shape

    use_out = data.draw(st.booleans(), label="use_out")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with np.errstate(all="ignore"):
            if use_out:
                out_dtype = data.draw(
                    st.sampled_from(_out_dtype_choices(accumulator_dtype)),
                    label="out_dtype",
                )
                out = np.empty(expected_shape, dtype=out_dtype)

                result = np.cumsum(a, axis=axis, dtype=requested_dtype, out=out)

                assert result is out
                assert result.shape == expected_shape
                assert result.dtype == out_dtype
                _assert_same_values(result, expected.astype(out_dtype, copy=False))
            else:
                result = np.cumsum(a, axis=axis, dtype=requested_dtype)

                assert result.shape == expected_shape
                assert result.dtype == accumulator_dtype
                _assert_same_values(result, expected)
# End program