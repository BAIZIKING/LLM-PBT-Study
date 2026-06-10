from hypothesis import given, strategies as st
from hypothesis.extra import numpy as hnp
import numpy as np

numpy_sum = np.sum

_NUMERIC_DTYPES = [
    np.dtype(np.bool_),
    np.dtype(np.int8),
    np.dtype(np.int16),
    np.dtype(np.int32),
    np.dtype(np.int64),
    np.dtype(np.uint8),
    np.dtype(np.uint16),
    np.dtype(np.uint32),
    np.dtype(np.uint64),
    np.dtype(np.float32),
    np.dtype(np.float64),
]


def _elements_for(dtype):
    dtype = np.dtype(dtype)
    if dtype.kind == "b":
        return st.booleans()
    if dtype.kind == "i":
        info = np.iinfo(dtype)
        return st.integers(info.min, info.max)
    if dtype.kind == "u":
        info = np.iinfo(dtype)
        return st.integers(0, info.max)
    if dtype.kind == "f":
        width = 32 if dtype == np.dtype(np.float32) else 64
        return st.floats(
            min_value=-1_000_000,
            max_value=1_000_000,
            allow_nan=False,
            allow_infinity=False,
            width=width,
        )
    raise AssertionError(f"unsupported dtype: {dtype}")


def _axis_strategy(ndim):
    if ndim == 0:
        return st.none()

    axes = list(range(-ndim, ndim))
    tuple_axes = st.lists(
        st.sampled_from(axes),
        min_size=1,
        max_size=ndim,
        unique_by=lambda axis: axis % ndim,
    ).map(tuple)

    return st.one_of(st.none(), st.sampled_from(axes), tuple_axes)


def _dtype_parameter_strategy(array_dtype):
    array_dtype = np.dtype(array_dtype)

    if array_dtype.kind == "b":
        choices = [None, np.dtype(np.int64), np.dtype(np.float64)]
    elif array_dtype.kind == "u":
        choices = [None, np.dtype(np.uint64), np.dtype(np.float64)]
    elif array_dtype.kind == "i":
        choices = [None, np.dtype(np.int64), np.dtype(np.float64)]
    elif array_dtype.kind == "f":
        choices = [None, np.dtype(np.float32), np.dtype(np.float64), np.dtype(np.int32)]
    else:
        choices = [None]

    return st.sampled_from(choices)


def _initial_strategy(effective_dtype):
    effective_dtype = np.dtype(effective_dtype)

    if effective_dtype.kind == "u":
        return st.integers(0, 10)
    if effective_dtype.kind == "f":
        return st.one_of(
            st.integers(-10, 10),
            st.floats(
                min_value=-10,
                max_value=10,
                allow_nan=False,
                allow_infinity=False,
            ),
        )
    return st.integers(-10, 10)


def _expected_shape(shape, axis, keepdims):
    ndim = len(shape)

    if axis is None:
        return (1,) * ndim if keepdims else ()

    if isinstance(axis, tuple):
        normalized_axes = tuple(sorted(axis_i % ndim for axis_i in axis))
    else:
        normalized_axes = (axis % ndim,)

    if keepdims:
        return tuple(1 if i in normalized_axes else size for i, size in enumerate(shape))

    return tuple(size for i, size in enumerate(shape) if i not in normalized_axes)


def _assert_same_values(actual, expected):
    actual_array = np.asarray(actual)
    expected_array = np.asarray(expected)

    if actual_array.dtype.kind == "f" or expected_array.dtype.kind == "f":
        np.testing.assert_allclose(
            actual_array,
            expected_array,
            rtol=1e-6,
            atol=1e-6,
            equal_nan=True,
        )
    else:
        np.testing.assert_array_equal(actual_array, expected_array)


# Summary: Generate 0-D through 4-D numeric arrays, including empty shapes, booleans,
# signed/unsigned integers, floats, dtype overrides, negative and tuple axes,
# keepdims, initial values, where masks, and optional out arrays. Check documented
# properties: equivalence to add.reduce, correct reduced shape, dtype override behavior,
# out identity/contents, and neutral-element behavior for empty/all-False reductions.
@given(st.data())
def test_numpy_sum(data):
    ndim = data.draw(st.integers(min_value=0, max_value=4))
    shape = data.draw(
        hnp.array_shapes(
            min_dims=ndim,
            max_dims=ndim,
            min_side=0,
            max_side=4,
        )
    )

    array_dtype = data.draw(st.sampled_from(_NUMERIC_DTYPES))
    a = data.draw(
        hnp.arrays(
            dtype=array_dtype,
            shape=shape,
            elements=_elements_for(array_dtype),
        )
    )

    axis = data.draw(_axis_strategy(ndim))
    dtype = data.draw(_dtype_parameter_strategy(array_dtype))
    keepdims = data.draw(st.booleans())

    use_initial = data.draw(st.booleans())
    effective_dtype = dtype if dtype is not None else array_dtype
    initial = data.draw(_initial_strategy(effective_dtype)) if use_initial else None

    use_where = data.draw(st.booleans())
    where = (
        data.draw(hnp.arrays(dtype=np.bool_, shape=shape))
        if use_where
        else None
    )

    kwargs = {
        "axis": axis,
        "dtype": dtype,
        "keepdims": keepdims,
    }
    if use_initial:
        kwargs["initial"] = initial
    if use_where:
        kwargs["where"] = where

    expected_shape = _expected_shape(shape, axis, keepdims)

    with np.errstate(all="ignore"):
        result = numpy_sum(a, **kwargs)
        reference = np.add.reduce(a, **kwargs)

    assert np.asarray(result).shape == expected_shape
    _assert_same_values(result, reference)

    if dtype is not None:
        assert np.asarray(result).dtype == np.dtype(dtype)

    if a.size == 0 and axis is None and not use_initial and not use_where:
        np.testing.assert_array_equal(np.asarray(result), np.zeros(expected_shape))

    if use_where and not np.any(where):
        neutral = initial if use_initial else 0
        np.testing.assert_array_equal(
            np.asarray(result),
            np.full(expected_shape, neutral, dtype=np.asarray(result).dtype),
        )

    if data.draw(st.booleans()):
        out = np.empty(expected_shape, dtype=np.asarray(result).dtype)

        with np.errstate(all="ignore"):
            returned = numpy_sum(a, out=out, **kwargs)

        assert returned is out
        _assert_same_values(out, result)


# End program