from hypothesis import given, strategies as st, assume, settings
import hypothesis.extra.numpy as npst
import numpy as np
import math


# Strategy for "safe" floating point values that avoid overflow/nan issues
# when summed. We bound magnitude and use float64.
def safe_floats():
    return st.floats(
        min_value=-1e6,
        max_value=1e6,
        allow_nan=False,
        allow_infinity=False,
        width=64,
    )


# Strategy for small integer values that avoid overflow when summed
# using the default platform integer accumulator.
def safe_ints():
    return st.integers(min_value=-(10**6), max_value=10**6)


def float_arrays(min_dims=0, max_dims=4):
    # Keep array sizes modest to avoid huge accumulation errors and slow tests.
    return npst.arrays(
        dtype=np.float64,
        shape=npst.array_shapes(min_dims=min_dims, max_dims=max_dims,
                                min_side=0, max_side=6),
        elements=safe_floats(),
    )


def int_arrays(min_dims=0, max_dims=4):
    return npst.arrays(
        dtype=np.int64,
        shape=npst.array_shapes(min_dims=min_dims, max_dims=max_dims,
                                min_side=0, max_side=6),
        elements=safe_ints(),
    )


def axis_for(arr):
    """Strategy producing a valid axis (None, int, or tuple of ints) for arr."""
    ndim = arr.ndim
    if ndim == 0:
        return st.just(None)
    single = st.integers(min_value=-ndim, max_value=ndim - 1)
    tuples = st.lists(
        st.integers(min_value=0, max_value=ndim - 1),
        min_size=1, max_size=ndim, unique=True,
    ).map(tuple)
    return st.one_of(st.none(), single, tuples)


# ---------------------------------------------------------------------------
# Property 1: Identity/equivalence with manual summation (axis=None).
# np.sum over all elements should equal manual iteration (within tolerance).
# ---------------------------------------------------------------------------
@given(st.data())
@settings(deadline=None)
def test_numpy_sum_property_manual_equivalence():
    data = st.data()
    arr = data.example() if False else None  # placeholder, real draw below


@given(arr=float_arrays(), data=st.data())
@settings(deadline=None)
def test_numpy_sum_manual_equivalence(arr, data):
    result = np.sum(arr)
    # Manual summation in float64.
    manual = 0.0
    for x in arr.ravel():
        manual += float(x)
    # Allow tolerance because summation order/precision may differ.
    assert math.isclose(result, manual, rel_tol=1e-6, abs_tol=1e-3)
# End program


# ---------------------------------------------------------------------------
# Property 2: Shape correctness for axis / keepdims / axis=None.
# ---------------------------------------------------------------------------
@given(arr=float_arrays(), data=st.data())
@settings(deadline=None)
def test_numpy_sum_shape_correctness(arr, data):
    axis = data.draw(axis_for(arr))

    res = np.sum(arr, axis=axis)
    res_keep = np.sum(arr, axis=axis, keepdims=True)

    if axis is None:
        # Scalar (0-d) result.
        assert np.ndim(res) == 0
        # keepdims=True with axis=None -> all dims size 1.
        assert res_keep.shape == tuple(1 for _ in arr.shape)
    else:
        axes = (axis,) if isinstance(axis, int) else axis
        # Normalize negative axes.
        norm = tuple(a % arr.ndim for a in axes)
        expected = tuple(s for i, s in enumerate(arr.shape) if i not in norm)
        assert res.shape == expected
        expected_keep = tuple(1 if i in norm else s
                              for i, s in enumerate(arr.shape))
        assert res_keep.shape == expected_keep
# End program


# ---------------------------------------------------------------------------
# Property 3: Initial value offset.
# np.sum(a, initial=k) == np.sum(a) + k.
# ---------------------------------------------------------------------------
@given(arr=float_arrays(), initial=safe_floats())
@settings(deadline=None)
def test_numpy_sum_initial_offset(arr, initial):
    with_initial = np.sum(arr, initial=initial)
    without = np.sum(arr)
    expected = without + initial
    assert math.isclose(with_initial, expected, rel_tol=1e-6, abs_tol=1e-3)
# End program


# ---------------------------------------------------------------------------
# Property 4: Empty array / fully-excluded selection returns 0 (plus initial).
# ---------------------------------------------------------------------------
@given(
    shape=npst.array_shapes(min_dims=1, max_dims=3, min_side=0, max_side=6),
    initial=st.one_of(st.just(0.0), safe_floats()),
    data=st.data(),
)
@settings(deadline=None)
def test_numpy_sum_empty_neutral_element(shape, initial, data):
    # Build a non-empty array but exclude everything via where=False.
    use_empty = data.draw(st.booleans())
    if use_empty:
        # Force an empty array by making at least one dimension zero.
        # If none are zero, replace the first dim with 0.
        if 0 not in shape:
            shape = (0,) + shape[1:]
        arr = np.zeros(shape, dtype=np.float64)
        result = np.sum(arr, initial=initial)
    else:
        arr = data.draw(npst.arrays(
            dtype=np.float64, shape=shape, elements=safe_floats()))
        result = np.sum(arr, where=False, initial=initial)
    # Neutral element 0, offset by initial.
    assert math.isclose(result, initial, rel_tol=1e-9, abs_tol=1e-9)
# End program


# ---------------------------------------------------------------------------
# Property 5: Additivity / decomposition over axes.
# Summing over a tuple of axes equals successive single-axis reductions,
# and summing over all axes equals axis=None (exactly, using integers).
# ---------------------------------------------------------------------------
@given(arr=int_arrays(min_dims=1, max_dims=4), data=st.data())
@settings(deadline=None)
def test_numpy_sum_axis_decomposition(arr, data):
    ndim = arr.ndim
    # Draw a non-empty subset of axes (as positive indices, unique).
    axes = data.draw(st.lists(
        st.integers(min_value=0, max_value=ndim - 1),
        min_size=1, max_size=ndim, unique=True,
    ))
    axes_tuple = tuple(axes)

    # Sum over the whole tuple at once.
    combined = np.sum(arr, axis=axes_tuple)

    # Successively reduce one axis at a time. Reduce from highest axis to
    # lowest so that earlier reductions don't shift later axis indices.
    stepwise = arr
    for ax in sorted(axes_tuple, reverse=True):
        stepwise = np.sum(stepwise, axis=ax)

    # Integer arithmetic => should be exactly equal.
    assert np.array_equal(combined, stepwise)

    # Summing over all axes equals axis=None.
    all_axes_sum = np.sum(arr, axis=tuple(range(ndim)))
    none_sum = np.sum(arr)
    assert np.array_equal(all_axes_sum, none_sum)
# End program