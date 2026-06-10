from hypothesis import given, strategies as st, settings
from hypothesis.extra import numpy as hnp
import numpy as np

# Summary: Generate numeric numpy arrays of varied dtype/shape (including empty),
# pick a valid axis (None / int / tuple), and optionally use keepdims, initial,
# and a broadcastable boolean `where` mask. We verify result shape correctness
# and numerical equivalence against an independent reference computation built
# from masked elements, accounting for initial value, while handling integer
# modular/overflow behavior by comparing in float64 with tolerance.
@settings(deadline=None, max_examples=300)
@given(st.data())
def test_numpy_sum(data):
    # ---- Build the input array ----
    dtype = data.draw(
        st.sampled_from([np.int8, np.int32, np.int64,
                         np.uint8, np.uint32,
                         np.float32, np.float64]),
        label="dtype",
    )
    shape = data.draw(hnp.array_shapes(min_dims=0, max_dims=4,
                                       min_side=0, max_side=4),
                      label="shape")

    if np.issubdtype(dtype, np.floating):
        elements = st.floats(min_value=-1e3, max_value=1e3,
                             allow_nan=False, allow_infinity=False,
                             width=32 if dtype == np.float32 else 64)
    else:
        # Keep values small to keep reference math sane
        info = np.iinfo(dtype)
        lo = max(int(info.min), -100)
        hi = min(int(info.max), 100)
        elements = st.integers(min_value=lo, max_value=hi)

    a = data.draw(hnp.arrays(dtype=dtype, shape=shape, elements=elements),
                  label="a")

    # ---- Choose axis ----
    ndim = a.ndim
    if ndim == 0:
        axis = None
    else:
        axis_kind = data.draw(st.sampled_from(["none", "int", "tuple"]),
                              label="axis_kind")
        if axis_kind == "none":
            axis = None
        elif axis_kind == "int":
            axis = data.draw(st.integers(min_value=-ndim, max_value=ndim - 1),
                            label="axis_int")
        else:
            k = data.draw(st.integers(min_value=1, max_value=ndim),
                         label="axis_count")
            axis = tuple(data.draw(
                st.lists(st.integers(0, ndim - 1), min_size=k, max_size=k,
                         unique=True),
                label="axis_tuple"))

    keepdims = data.draw(st.booleans(), label="keepdims")
    use_initial = data.draw(st.booleans(), label="use_initial")
    initial = data.draw(st.integers(-10, 10), label="initial") if use_initial else None

    use_where = data.draw(st.booleans(), label="use_where")
    if use_where:
        where = data.draw(hnp.arrays(dtype=bool, shape=shape), label="where")
    else:
        where = None

    # ---- Call np.sum with the assembled kwargs ----
    kwargs = {"axis": axis, "keepdims": keepdims}
    if initial is not None:
        kwargs["initial"] = initial
    if where is not None:
        kwargs["where"] = where

    result = np.sum(a, **kwargs)

    # ---- Property 1: shape correctness ----
    # Compute expected reduced-axis set
    if axis is None:
        reduced = set(range(ndim))
    elif isinstance(axis, tuple):
        reduced = {ax % ndim for ax in axis}
    else:
        reduced = {axis % ndim}

    if keepdims:
        expected_shape = tuple(1 if i in reduced else s
                               for i, s in enumerate(a.shape))
    else:
        expected_shape = tuple(s for i, s in enumerate(a.shape)
                               if i not in reduced)
    assert np.shape(result) == expected_shape, (
        f"shape mismatch: got {np.shape(result)}, expected {expected_shape}")

    # ---- Property 2: numerical equivalence vs independent reference ----
    # Build reference in float64, applying mask and initial value.
    a64 = a.astype(np.float64)
    if where is not None:
        masked = np.where(where, a64, 0.0)
    else:
        masked = a64

    ref_axis = axis  # numpy accepts same axis arg for np.add.reduce / sum
    ref = np.sum(masked, axis=ref_axis, keepdims=keepdims)
    if initial is not None:
        ref = ref + np.float64(initial)

    result64 = np.asarray(result, dtype=np.float64)

    # For integer dtypes, numpy may wrap/overflow; we kept values tiny so the
    # accumulator (default platform int) won't overflow here, making the
    # float64 reference exact. Use a tolerance for float accumulation order.
    np.testing.assert_allclose(result64, np.asarray(ref, dtype=np.float64),
                               rtol=1e-5, atol=1e-4)
# End program