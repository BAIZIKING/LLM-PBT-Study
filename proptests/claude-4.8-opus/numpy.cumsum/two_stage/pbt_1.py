from hypothesis import given, strategies as st, assume
import numpy as np
import hypothesis.extra.numpy as npst

# Strategy for shapes (1-D up to 3-D, modest sizes to avoid huge inputs)
shapes = npst.array_shapes(min_dims=1, max_dims=3, min_side=1, max_side=10)

# Integer dtypes (use platform default int and smaller, but bounded to avoid overflow surprises)
int_dtypes = st.sampled_from([np.int32, np.int64])
float_dtypes = st.sampled_from([np.float32, np.float64])


@given(st.data())
def test_numpy_cumsum_property():
    # ---------------------------------------------------------------
    # Generate a base array.  We bound integer element values so that
    # the cumulative sum does not overflow the accumulator dtype.
    # ---------------------------------------------------------------
    shape = data.draw(shapes) if False else st.just(None)  # placeholder, replaced below

    # Draw a dtype and a corresponding array.
    dtype = data.draw(st.one_of(int_dtypes, float_dtypes))

    shp = data.draw(shapes)
    total_elems = int(np.prod(shp))

    if np.issubdtype(dtype, np.integer):
        # Bound element magnitude so total sum cannot overflow.
        # For int64 accumulator: keep |sum| well within range.
        info = np.iinfo(np.int64)
        # max per-element magnitude so that total_elems * mag < int64 max
        safe_mag = max(1, min(10**6, info.max // max(1, total_elems) // 2))
        elements = st.integers(min_value=-int(safe_mag), max_value=int(safe_mag))
    else:
        elements = st.floats(
            min_value=-1e6, max_value=1e6,
            allow_nan=False, allow_infinity=False, width=32
        )

    a = data.draw(npst.arrays(dtype=dtype, shape=shp, elements=elements))

    # Choose axis: either None or a valid axis for the array.
    axis = data.draw(st.one_of(st.none(), st.integers(min_value=0, max_value=a.ndim - 1)))

    result = np.cumsum(a, axis=axis)

    # ---------------------------------------------------------------
    # Property 1: Shape preservation / flattening behavior
    # ---------------------------------------------------------------
    if axis is None:
        assert result.shape == (a.size,)
    else:
        assert result.shape == a.shape

    # ---------------------------------------------------------------
    # Property 5: Output dtype rules (no explicit dtype given)
    # ---------------------------------------------------------------
    if np.issubdtype(a.dtype, np.integer):
        default_int = np.dtype(np.intp)
        if a.dtype.itemsize < default_int.itemsize:
            expected_dtype = default_int
        else:
            expected_dtype = a.dtype
    else:
        expected_dtype = a.dtype
    assert result.dtype == expected_dtype

    # ---------------------------------------------------------------
    # Property 2: Last element equals total sum (along axis / flattened)
    # Use integer-safe comparison for ints, approximate for floats.
    # ---------------------------------------------------------------
    if axis is None:
        flat = a.ravel()
        if flat.size > 0:
            if np.issubdtype(a.dtype, np.integer):
                assert int(result[-1]) == int(flat.sum(dtype=np.int64))
            else:
                np.testing.assert_allclose(
                    result[-1], flat.astype(np.float64).sum(), rtol=1e-3, atol=1e-3
                )
    else:
        last = np.take(result, indices=result.shape[axis] - 1, axis=axis)
        total = a.sum(axis=axis)
        if np.issubdtype(a.dtype, np.integer):
            assert np.array_equal(last.astype(np.int64), total.astype(np.int64))
        else:
            np.testing.assert_allclose(
                last, total, rtol=1e-3, atol=1e-3
            )

    # ---------------------------------------------------------------
    # Property 3: First element equals first input element
    # ---------------------------------------------------------------
    if axis is None:
        flat = a.ravel()
        if flat.size > 0:
            assert result[0] == flat[0]
    else:
        first_out = np.take(result, indices=0, axis=axis)
        first_in = np.take(a, indices=0, axis=axis)
        if np.issubdtype(a.dtype, np.integer):
            assert np.array_equal(first_out, first_in.astype(result.dtype))
        else:
            np.testing.assert_allclose(first_out, first_in, rtol=1e-5, atol=1e-5)

    # ---------------------------------------------------------------
    # Property 4: np.diff of cumsum recovers original elements
    # ---------------------------------------------------------------
    if axis is None:
        flat = a.ravel().astype(result.dtype)
        if flat.size > 1:
            recovered = np.diff(result)
            if np.issubdtype(a.dtype, np.integer):
                assert np.array_equal(recovered, flat[1:])
            else:
                np.testing.assert_allclose(recovered, flat[1:], rtol=1e-3, atol=1e-3)
    else:
        if a.shape[axis] > 1:
            recovered = np.diff(result, axis=axis)
            expected = np.take(
                a.astype(result.dtype),
                indices=range(1, a.shape[axis]),
                axis=axis,
            )
            if np.issubdtype(a.dtype, np.integer):
                assert np.array_equal(recovered, expected)
            else:
                np.testing.assert_allclose(recovered, expected, rtol=1e-3, atol=1e-3)
# End program