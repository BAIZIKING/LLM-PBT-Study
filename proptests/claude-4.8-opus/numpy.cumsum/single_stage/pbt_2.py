from hypothesis import given, strategies as st, settings
from hypothesis.extra import numpy as hnp
import numpy as np

# Summary: Generate arrays of varied shapes (incl. empty/scalar-ish), integer and
# float dtypes (no nan/inf), a valid axis (None or in [-ndim, ndim)), and an
# optional explicit dtype. Check shape/size invariants, the recurrence relation
# (diff of cumsum recovers input), that the last slice equals the full sum, and
# that the first slice equals the input's first slice.
@given(st.data())
@settings(max_examples=300)
def test_numpy_cumsum(data):
    # Choose a dtype: integers (modular, exact) or floats (approximate).
    dtype = data.draw(st.sampled_from([
        np.int8, np.int16, np.int32, np.int64,
        np.uint8, np.uint16, np.uint32, np.uint64,
        np.float32, np.float64,
    ]))
    is_float = np.issubdtype(dtype, np.floating)

    if is_float:
        elements = st.floats(min_value=-1e3, max_value=1e3,
                             allow_nan=False, allow_infinity=False,
                             width=32 if dtype == np.float32 else 64)
    else:
        info = np.iinfo(dtype)
        # Keep values modest to make modular arithmetic predictable but still exercised.
        lo = max(info.min, -1000)
        hi = min(info.max, 1000)
        elements = st.integers(min_value=lo, max_value=hi)

    a = data.draw(hnp.arrays(
        dtype=dtype,
        shape=hnp.array_shapes(min_dims=1, max_dims=4, min_side=0, max_side=5),
        elements=elements,
    ))

    ndim = a.ndim
    # Choose axis: None or a valid integer (positive or negative).
    axis = data.draw(st.one_of(
        st.none(),
        st.integers(min_value=-ndim, max_value=ndim - 1),
    ))

    result = np.cumsum(a, axis=axis)

    # Property 1: size is preserved.
    assert result.size == a.size

    # Property 2: shape behavior.
    if axis is None:
        assert result.shape == (a.size,)
    else:
        assert result.shape == a.shape

    # Skip value-based checks on empty arrays (no elements to compare).
    if a.size == 0:
        return

    # Work with a normalized version for the value-based checks.
    if axis is None:
        flat = a.ravel()
        cum = result
        ax = 0
        ref = flat
    else:
        cum = result
        ax = axis
        ref = a

    # Property 3: first slice along axis equals input's first slice.
    first_cum = np.take(cum, 0, axis=ax)
    first_ref = np.take(ref, 0, axis=ax)
    if is_float:
        np.testing.assert_allclose(first_cum, first_ref, rtol=1e-5, atol=1e-5)
    else:
        np.testing.assert_array_equal(first_cum, first_ref)

    # Property 4: recurrence relation — diff of cumsum recovers the input
    # (along the axis), modulo integer wraparound / float tolerance.
    if ref.shape[ax] >= 2:
        diffs = np.diff(cum, axis=ax)
        rest = np.take(ref, range(1, ref.shape[ax]), axis=ax)
        if is_float:
            np.testing.assert_allclose(diffs, rest, rtol=1e-4, atol=1e-4)
        else:
            # Compare in the result dtype using modular arithmetic.
            expected = rest.astype(cum.dtype)
            np.testing.assert_array_equal(diffs.astype(cum.dtype), expected)

    # Property 5: last cumulative slice equals the total sum along the axis.
    last_cum = np.take(cum, cum.shape[ax] - 1, axis=ax)
    total = np.sum(ref, axis=ax, dtype=cum.dtype)
    if is_float:
        # sum may use pairwise summation, so only approximate equality holds.
        np.testing.assert_allclose(last_cum, total, rtol=1e-3, atol=1e-3)
    else:
        np.testing.assert_array_equal(last_cum, total)
# End program