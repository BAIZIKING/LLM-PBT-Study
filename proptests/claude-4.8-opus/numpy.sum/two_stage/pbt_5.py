from hypothesis import given, strategies as st, settings, assume
import hypothesis.extra.numpy as hnp
import numpy
import math

# Bounded element strategies to avoid overflow, NaN and infinity in accumulation.
safe_floats = st.floats(
    min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False, width=64
)
safe_ints = st.integers(min_value=-(10**6), max_value=10**6)


def float_arrays(min_dims=0, max_dims=3, max_side=6):
    return hnp.arrays(
        dtype=numpy.float64,
        shape=hnp.array_shapes(min_dims=min_dims, max_dims=max_dims, max_side=max_side),
        elements=safe_floats,
    )


def int_arrays(min_dims=1, max_dims=3, max_side=6):
    return hnp.arrays(
        dtype=numpy.int64,
        shape=hnp.array_shapes(min_dims=min_dims, max_dims=max_dims, max_side=max_side),
        elements=safe_ints,
    )


# --- Property 1: axis=None => scalar equal to total (flat) sum ---
@given(st.data())
@settings(max_examples=200)
def test_numpy_sum_axis_none_equals_flat_sum(data):
    arr = data.draw(float_arrays())
    result = numpy.sum(arr)
    # Output must be a 0-d scalar.
    assert numpy.ndim(result) == 0
    expected = math.fsum(arr.ravel().tolist()) if arr.size else 0.0
    assert math.isclose(float(result), expected, rel_tol=1e-9, abs_tol=1e-6)


# --- Property 2: shape reduction along an axis (with / without keepdims) ---
@given(st.data())
@settings(max_examples=200)
def test_numpy_sum_shape_reduction(data):
    arr = data.draw(float_arrays(min_dims=1, max_dims=4))
    ndim = arr.ndim
    # Pick a valid axis.
    axis = data.draw(st.integers(min_value=-ndim, max_value=ndim - 1))
    norm_axis = axis % ndim

    # Without keepdims: that axis is removed.
    res = numpy.sum(arr, axis=axis)
    expected_shape = tuple(
        s for i, s in enumerate(arr.shape) if i != norm_axis
    )
    assert res.shape == expected_shape

    # With keepdims: that axis becomes size 1 and result broadcasts against input.
    res_kd = numpy.sum(arr, axis=axis, keepdims=True)
    expected_kd_shape = tuple(
        1 if i == norm_axis else s for i, s in enumerate(arr.shape)
    )
    assert res_kd.shape == expected_kd_shape
    # Broadcastability check.
    numpy.broadcast_shapes(res_kd.shape, arr.shape)


# --- Property 3: empty array / all-False where => neutral element 0 (+ initial) ---
@given(st.data())
@settings(max_examples=200)
def test_numpy_sum_identity_empty_and_where(data):
    # Empty array case.
    empty = numpy.array([], dtype=numpy.float64)
    assert float(numpy.sum(empty)) == 0.0

    initial = data.draw(safe_floats)
    assert math.isclose(
        float(numpy.sum(empty, initial=initial)), initial, rel_tol=1e-9, abs_tol=1e-9
    )

    # All-False where mask on a non-empty array => 0 (+ initial).
    arr = data.draw(float_arrays(min_dims=1, max_dims=2))
    mask = numpy.zeros(arr.shape, dtype=bool)
    assert float(numpy.sum(arr, where=mask)) == 0.0
    assert math.isclose(
        float(numpy.sum(arr, where=mask, initial=initial)),
        initial,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )


# --- Property 4: initial value additivity: sum(a, initial=k) == sum(a) + k ---
@given(st.data())
@settings(max_examples=200)
def test_numpy_sum_initial_additivity(data):
    arr = data.draw(float_arrays(min_dims=0, max_dims=3))
    k = data.draw(safe_floats)
    base = float(numpy.sum(arr))
    with_initial = float(numpy.sum(arr, initial=k))
    assert math.isclose(with_initial, base + k, rel_tol=1e-9, abs_tol=1e-6)


# --- Property 5: where-mask consistency: masked sum == sum of selected elements ---
@given(st.data())
@settings(max_examples=200)
def test_numpy_sum_where_consistency(data):
    arr = data.draw(int_arrays(min_dims=1, max_dims=3))
    mask = data.draw(
        hnp.arrays(dtype=numpy.bool_, shape=arr.shape, elements=st.booleans())
    )
    masked_sum = numpy.sum(arr, where=mask)
    # Reference: explicitly sum only the selected elements.
    selected = arr[mask]
    expected = int(numpy.sum(selected)) if selected.size else 0
    assert int(masked_sum) == expected
# End program