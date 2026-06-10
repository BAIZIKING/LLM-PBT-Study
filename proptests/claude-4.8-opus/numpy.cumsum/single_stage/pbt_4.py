import numpy as np
from hypothesis import given, strategies as st
from hypothesis.extra.numpy import arrays, array_shapes

# Summary: Generate numpy arrays of varied shapes (incl. empty/1-D/N-D) and
# both integer and float dtypes with finite, bounded values. Then draw a valid
# axis (or None) and verify shape/size invariants, that the last cumsum entry
# equals the sequential total sum, that the first entry equals a's first entry,
# and that differencing the cumsum recovers the original array values.
@given(st.data())
def test_numpy_cumsum(data):
    dtype = data.draw(
        st.sampled_from([np.int32, np.int64, np.float32, np.float64]),
        label="dtype",
    )
    shape = data.draw(array_shapes(min_dims=1, max_dims=3, min_side=0, max_side=5),
                      label="shape")

    if np.issubdtype(dtype, np.integer):
        elements = st.integers(min_value=-1000, max_value=1000)
    else:
        elements = st.floats(min_value=-1e6, max_value=1e6,
                             allow_nan=False, allow_infinity=False, width=32)

    a = data.draw(arrays(dtype=dtype, shape=shape, elements=elements), label="a")

    # Choose axis: None or a valid axis for a.
    axis = data.draw(st.one_of(st.none(),
                               st.integers(min_value=0, max_value=a.ndim - 1)),
                     label="axis")

    result = np.cumsum(a, axis=axis)

    # Property 1 & 2: shape and size invariants.
    assert result.size == a.size
    if axis is None:
        assert result.shape == (a.size,)
        assert result.ndim == 1
    else:
        assert result.shape == a.shape

    # Determine working view to check value-based properties.
    if axis is None:
        flat = a.ravel()
        work_axis = 0
        ref = flat
        res_view = result
    else:
        ref = a
        work_axis = axis
        res_view = result

    # Skip value checks for empty arrays (nothing to compare).
    if a.size == 0:
        return

    is_float = np.issubdtype(dtype, np.floating)

    # Property 5: first element of cumsum equals first element of a along axis.
    first_res = np.take(res_view, 0, axis=work_axis)
    first_ref = np.take(ref, 0, axis=work_axis)
    if is_float:
        np.testing.assert_allclose(first_res, first_ref, rtol=1e-4, atol=1e-3)
    else:
        np.testing.assert_array_equal(first_res, first_ref)

    # Property 3: last cumsum entry equals the plain sequential total sum.
    last_res = np.take(res_view, res_view.shape[work_axis] - 1, axis=work_axis)
    total = np.add.reduce(ref, axis=work_axis)
    if is_float:
        np.testing.assert_allclose(last_res, total, rtol=1e-3, atol=1e-2)
    else:
        np.testing.assert_array_equal(last_res, total)

    # Property 4: differencing cumsum recovers original values along the axis.
    if ref.shape[work_axis] >= 2:
        diffed = np.diff(res_view, axis=work_axis)
        # Original values excluding the first index along the axis.
        original_tail = np.take(ref, range(1, ref.shape[work_axis]), axis=work_axis)
        if is_float:
            np.testing.assert_allclose(diffed, original_tail, rtol=1e-3, atol=1e-2)
        else:
            np.testing.assert_array_equal(diffed, original_tail)
# End program