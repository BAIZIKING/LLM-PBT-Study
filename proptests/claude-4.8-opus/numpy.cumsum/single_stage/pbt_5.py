from hypothesis import given, strategies as st, settings
from hypothesis.extra import numpy as hnp
import numpy as np

# Summary: Generate n-dimensional arrays of integer/float dtypes with finite values,
# random valid axis (or None), and optional output dtype. Check shape/size preservation,
# that cumsum's last element equals the total sum, that consecutive differences recover
# the input (the defining cumulative property), and that specified dtype is honored.
@given(st.data())
@settings(max_examples=300)
def test_numpy_cumsum(data):
    # Choose a dtype for the input array
    in_dtype = data.draw(st.sampled_from([
        np.int8, np.int16, np.int32, np.int64,
        np.float32, np.float64,
    ]), label="in_dtype")

    is_float = np.issubdtype(in_dtype, np.floating)

    # Build element strategy: finite values only (to keep numeric checks meaningful)
    if is_float:
        elements = st.floats(min_value=-1e3, max_value=1e3,
                             allow_nan=False, allow_infinity=False,
                             width=32 if in_dtype == np.float32 else 64)
    else:
        # Keep integer values small to avoid distracting modular-overflow cases
        elements = st.integers(min_value=-100, max_value=100)

    # Generate the array (allow 1-d up to 3-d, dims can be 0 to include empties)
    arr = data.draw(hnp.arrays(
        dtype=in_dtype,
        shape=hnp.array_shapes(min_dims=1, max_dims=3, min_side=0, max_side=5),
        elements=elements,
    ), label="arr")

    # Choose axis: None or a valid axis in [-ndim, ndim-1]
    axis = data.draw(st.one_of(
        st.none(),
        st.integers(min_value=-arr.ndim, max_value=arr.ndim - 1),
    ), label="axis")

    # Optionally specify an output dtype
    out_dtype = data.draw(st.sampled_from([None, np.float64, np.int64]),
                          label="out_dtype")

    result = np.cumsum(arr, axis=axis, dtype=out_dtype)

    # --- Property 1 & 2: size and shape preservation ---
    assert result.size == arr.size
    if axis is None:
        # Flattened: result is 1-d
        assert result.ndim == 1
        assert result.shape == (arr.size,)
    else:
        assert result.shape == arr.shape

    # --- Property 5: specified dtype is honored ---
    if out_dtype is not None:
        assert result.dtype == np.dtype(out_dtype)

    # Determine whether the accumulation is exact (integers) for tighter checks.
    exact = np.issubdtype(result.dtype, np.integer) and not is_float

    if arr.size == 0:
        return  # nothing further to check for empty arrays

    # --- Property 3: last cumsum element equals total sum ---
    flat_result = result if axis is None else np.cumsum(arr, axis=None, dtype=out_dtype)
    total = np.sum(arr, dtype=out_dtype)
    if exact:
        assert flat_result[-1] == total
    else:
        assert np.allclose(flat_result[-1], total, rtol=1e-3, atol=1e-3)

    # --- Property 4: consecutive differences along axis recover the input ---
    ax = axis if axis is not None else 0
    work = arr if axis is not None else arr.ravel()
    cs = np.cumsum(work, axis=ax, dtype=out_dtype)
    if work.shape[ax] >= 2:
        recovered = np.diff(cs, axis=ax)
        original_tail = np.take(work, range(1, work.shape[ax]), axis=ax).astype(cs.dtype)
        if exact:
            assert np.array_equal(recovered, original_tail)
        else:
            assert np.allclose(recovered, original_tail, rtol=1e-3, atol=1e-3)
# End program