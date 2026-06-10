import numpy as np
from hypothesis import given, settings, strategies as st
from hypothesis.extra import numpy as hnp

# Summary: Generate numpy arrays of integer/float dtypes with varied shapes
# (including empty and 0-d). Restrict element magnitudes (and exclude NaN/inf
# for floats) so a wide-accumulator (int64/float64) reference sum is exact and
# comparable. Draw a valid axis (None / int / tuple of distinct ints) plus an
# optional `initial`, then verify equivalence with add.reduce, the empty->0
# rule, keepdims shape semantics, the initial-offset property, scalar return
# for axis=None, and out-parameter behavior.
@given(st.data())
@settings(max_examples=300)
def test_numpy_sum(data):
    # --- choose a dtype ---
    dtype = data.draw(
        st.sampled_from([np.int32, np.int64, np.float32, np.float64]),
        label="dtype",
    )
    is_float = np.issubdtype(dtype, np.floating)

    # --- element strategy (bounded; floats finite) ---
    if is_float:
        elements = st.floats(
            min_value=-1e6, max_value=1e6,
            allow_nan=False, allow_infinity=False, width=32,
        )
    else:
        elements = st.integers(min_value=-10_000, max_value=10_000)

    # --- shape: 0 to 3 dims, sides 0..4 (allows empty and 0-d) ---
    shape = data.draw(
        hnp.array_shapes(min_dims=0, max_dims=3, min_side=0, max_side=4),
        label="shape",
    )

    a = data.draw(hnp.arrays(dtype=dtype, shape=shape, elements=elements), label="a")
    ndim = a.ndim

    # --- choose a valid axis: None, single int, or tuple of distinct ints ---
    if ndim == 0:
        axis = None
    else:
        axis_kind = data.draw(st.sampled_from(["none", "int", "tuple"]), label="axis_kind")
        if axis_kind == "none":
            axis = None
        elif axis_kind == "int":
            axis = data.draw(st.integers(min_value=-ndim, max_value=ndim - 1), label="axis_int")
        else:
            k = data.draw(st.integers(min_value=1, max_value=ndim), label="naxes")
            chosen = data.draw(
                st.lists(st.integers(0, ndim - 1), min_size=k, max_size=k, unique=True),
                label="axis_tuple",
            )
            axis = tuple(chosen)

    # Reference accumulator dtype (wide enough to be exact for our bounds).
    acc = np.float64 if is_float else np.int64

    result = np.sum(a, axis=axis)

    # Property 1: equivalent to np.add.reduce
    reduced = np.add.reduce(a, axis=axis)
    np.testing.assert_array_equal(result, reduced)

    # Property 2: empty array -> neutral element 0
    if a.size == 0 and axis is None:
        assert np.sum(a) == 0

    # Reference value (computed in a wide accumulator, then cast back like numpy).
    ref = np.add.reduce(a.astype(acc), axis=axis).astype(result.dtype)
    if is_float:
        np.testing.assert_allclose(result, ref, rtol=1e-5, atol=1e-3)
    else:
        np.testing.assert_array_equal(result, ref)

    # Property 3: keepdims shape semantics
    result_kd = np.sum(a, axis=axis, keepdims=True)
    if axis is None:
        assert result_kd.shape == tuple(1 for _ in range(ndim))
    else:
        ax = (axis,) if isinstance(axis, int) else axis
        norm = {x % ndim for x in ax}
        expected_shape = tuple(
            1 if i in norm else s for i, s in enumerate(a.shape)
        )
        assert result_kd.shape == expected_shape
    # Squeezing the kept dims reproduces the non-keepdims result.
    np.testing.assert_array_equal(np.squeeze(result_kd, axis=axis), result)

    # Property 4: `initial` offsets the sum by exactly `initial`.
    init = data.draw(st.integers(min_value=-5, max_value=5), label="initial")
    result_init = np.sum(a, axis=axis, initial=init)
    if is_float:
        np.testing.assert_allclose(result_init, result + init, rtol=1e-5, atol=1e-3)
    else:
        np.testing.assert_array_equal(result_init, result + init)

    # Property 5: axis=None (or 0-d input) returns a scalar (0-d) result.
    if axis is None:
        assert np.ndim(result) == 0

    # Property 6: `out` returns a reference to itself with correct values.
    out = np.empty_like(np.asarray(result))
    returned = np.sum(a, axis=axis, out=out)
    assert returned is out
    np.testing.assert_array_equal(out, result)
# End program