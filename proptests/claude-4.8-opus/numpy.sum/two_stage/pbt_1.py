from hypothesis import given, strategies as st, assume, settings
import numpy as np
import hypothesis.extra.numpy as npst

# Use bounded, finite float64 values to avoid overflow and NaN/inf propagation.
# Magnitudes and array sizes are limited so accumulated sums stay safe in float64.
safe_floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)


def array_strategy(data, min_dims=0, max_dims=3, max_side=6):
    return data.draw(
        npst.arrays(
            dtype=np.float64,
            shape=npst.array_shapes(min_dims=min_dims, max_dims=max_dims, max_side=max_side),
            elements=safe_floats,
        )
    )


@given(st.data())
@settings(max_examples=200)
def test_numpy_sum_reconstruction(data):
    # Property 1: Summing all elements equals manually adding each element,
    # within floating-point tolerance.
    arr = array_strategy(data)
    result = np.sum(arr)
    manual = 0.0
    for x in arr.flatten():
        manual += float(x)
    # Tolerance scales with size and magnitude of the data.
    tol = 1e-6 * (abs(manual) + arr.size + 1.0)
    assert np.isclose(result, manual, atol=tol, rtol=1e-6)


@given(st.data())
@settings(max_examples=200)
def test_numpy_sum_shape_reduction(data):
    # Property 2: Summing along an axis removes that axis from the shape;
    # with keepdims=True the axis is retained with size 1.
    arr = array_strategy(data, min_dims=1, max_dims=4)
    axis = data.draw(st.integers(min_value=0, max_value=arr.ndim - 1))

    result = np.sum(arr, axis=axis)
    expected_shape = arr.shape[:axis] + arr.shape[axis + 1:]
    assert result.shape == expected_shape

    result_keep = np.sum(arr, axis=axis, keepdims=True)
    expected_keep_shape = arr.shape[:axis] + (1,) + arr.shape[axis + 1:]
    assert result_keep.shape == expected_keep_shape


@given(st.data())
@settings(max_examples=200)
def test_numpy_sum_initial_value(data):
    # Property 3: np.sum(a, initial=k) equals np.sum(a) + k.
    arr = array_strategy(data)
    k = data.draw(st.floats(min_value=-1e6, max_value=1e6,
                            allow_nan=False, allow_infinity=False, width=64))

    with_initial = np.sum(arr, initial=k)
    without_initial = np.sum(arr) + k

    tol = 1e-6 * (abs(without_initial) + arr.size + 1.0)
    assert np.isclose(with_initial, without_initial, atol=tol, rtol=1e-6)


@given(st.data())
@settings(max_examples=100)
def test_numpy_sum_neutral_element(data):
    # Property 4: Sum of an empty array is 0; sum of an all-zero array is 0.
    # Empty array case.
    n_empty = data.draw(st.integers(min_value=0, max_value=5))
    empty_arr = np.zeros((0, n_empty), dtype=np.float64)
    assert np.sum(empty_arr) == 0.0

    # All-zeros array case.
    shape = data.draw(npst.array_shapes(min_dims=1, max_dims=3, max_side=6))
    zeros_arr = np.zeros(shape, dtype=np.float64)
    assert np.sum(zeros_arr) == 0.0


@given(st.data())
@settings(max_examples=200)
def test_numpy_sum_axis_decomposition(data):
    # Property 5: For a 2-D array, summing over axis=None equals summing the
    # result of np.sum(a, axis=0), and equals summing np.sum(a, axis=1).
    arr = data.draw(
        npst.arrays(
            dtype=np.float64,
            shape=npst.array_shapes(min_dims=2, max_dims=2, max_side=6),
            elements=safe_floats,
        )
    )

    total = np.sum(arr)
    via_axis0 = np.sum(np.sum(arr, axis=0))
    via_axis1 = np.sum(np.sum(arr, axis=1))

    tol = 1e-6 * (abs(total) + arr.size + 1.0)
    assert np.isclose(total, via_axis0, atol=tol, rtol=1e-6)
    assert np.isclose(total, via_axis1, atol=tol, rtol=1e-6)
# End program