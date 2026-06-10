from hypothesis import given, strategies as st, settings
from hypothesis.extra.numpy import arrays, array_shapes, floating_dtypes, integer_dtypes
import numpy as np

# Summary: Generate n-dimensional int/float arrays (no NaN/inf, bounded magnitude)
# with a valid axis (or None), optionally specifying an output dtype. Check size,
# shape, the cumulative recurrence, last-element-equals-sum, and dtype properties.
@given(st.data())
@settings(max_examples=500)
def test_numpy_cumsum(data):
    # Choose a dtype: mix of integer and floating types.
    dtype = data.draw(
        st.one_of(
            integer_dtypes(endianness="="),
            floating_dtypes(endianness="=", sizes=(32, 64)),
        ),
        label="dtype",
    )

    is_float = np.issubdtype(dtype, np.floating)

    if is_float:
        elements = st.floats(
            min_value=-1e6, max_value=1e6,
            allow_nan=False, allow_infinity=False, width=32,
        )
    else:
        info = np.iinfo(dtype)
        lo = max(int(info.min), -10000)
        hi = min(int(info.max), 10000)
        elements = st.integers(min_value=lo, max_value=hi)

    shape = data.draw(array_shapes(min_dims=1, max_dims=3, min_side=1, max_side=5),
                      label="shape")
    a = data.draw(arrays(dtype=dtype, shape=shape, elements=elements), label="a")

    ndim = a.ndim
    axis = data.draw(
        st.one_of(st.none(), st.integers(min_value=0, max_value=ndim - 1)),
        label="axis",
    )

    # Optionally specify an output dtype.
    out_dtype = data.draw(st.one_of(st.none(), st.just(np.float64)), label="out_dtype")

    result = np.cumsum(a, axis=axis, dtype=out_dtype)

    # Property 1: total size is preserved.
    assert result.size == a.size

    # Property: shape behavior depending on axis.
    if axis is None:
        assert result.ndim == 1
    else:
        assert result.shape == a.shape

    # Property 4: explicit dtype is respected.
    if out_dtype is not None:
        assert result.dtype == np.dtype(out_dtype)

    # Determine a tolerance for floating-point comparisons.
    use_float = is_float or out_dtype is not None

    if a.size > 0:
        # Property 2: last element of flattened cumsum equals total sum.
        flat_cumsum = np.cumsum(a, axis=None, dtype=out_dtype)
        total = np.sum(a, dtype=out_dtype)
        if use_float:
            assert np.allclose(flat_cumsum[-1], total, rtol=1e-3, atol=1e-3)
        else:
            assert flat_cumsum[-1] == total

        # Property 3: cumulative recurrence -- diff of cumsum recovers input.
        recovered = np.diff(result, axis=(0 if axis is None else axis), prepend=0)
        if axis is None:
            expected = a.flatten().astype(result.dtype)
        else:
            expected = a.astype(result.dtype)

        if use_float:
            assert np.allclose(recovered, expected, rtol=1e-3, atol=1e-3)
        else:
            assert np.array_equal(recovered, expected)
# End program