from hypothesis import given, strategies as st, settings
import hypothesis.extra.numpy as hnp
import numpy


# Strategy for safe float values (avoid inf/nan and very large magnitudes to prevent overflow)
safe_floats = st.floats(
    min_value=-1e6, max_value=1e6,
    allow_nan=False, allow_infinity=False, width=64
)

# Strategy for small integers to avoid modular overflow surprises
safe_ints = st.integers(min_value=-1000, max_value=1000)

# Strategy for non-negative integers (for monotonicity)
nonneg_ints = st.integers(min_value=0, max_value=1000)


def array_strategy(elements, dtype):
    return hnp.arrays(
        dtype=dtype,
        shape=hnp.array_shapes(min_dims=1, max_dims=3, min_side=1, max_side=8),
        elements=elements,
    )


@given(st.data())
@settings(deadline=None)
def test_numpy_cumsum_size_preservation():
    """Property 1: Output has the same number of elements as input, for any axis."""
    data = st.data()

    @given(arr=array_strategy(safe_ints, numpy.int64))
    def inner(arr):
        # Flattened cumsum
        result_flat = numpy.cumsum(arr)
        assert result_flat.size == arr.size

        # Along each axis
        for axis in range(arr.ndim):
            result_axis = numpy.cumsum(arr, axis=axis)
            assert result_axis.size == arr.size
            assert result_axis.shape == arr.shape

    inner()


@given(st.data())
@settings(deadline=None)
def test_numpy_cumsum_last_equals_sum():
    """Property 2: Last cumsum element equals total sum (integers, no overflow concerns)."""

    @given(arr=array_strategy(safe_ints, numpy.int64))
    def inner(arr):
        # Flattened: last element equals sum of all elements
        result_flat = numpy.cumsum(arr)
        assert result_flat[-1] == arr.sum()

        # Along an axis: last slice equals sum over that axis
        for axis in range(arr.ndim):
            result_axis = numpy.cumsum(arr, axis=axis)
            last_slice = numpy.take(result_axis, indices=result_axis.shape[axis] - 1, axis=axis)
            assert numpy.array_equal(last_slice, arr.sum(axis=axis))

    inner()


@given(st.data())
@settings(deadline=None)
def test_numpy_cumsum_monotonic_nonnegative():
    """Property 3: For non-negative inputs, cumsum is non-decreasing along the axis."""

    @given(arr=array_strategy(nonneg_ints, numpy.int64))
    def inner(arr):
        # Flattened
        result_flat = numpy.cumsum(arr)
        assert numpy.all(numpy.diff(result_flat) >= 0)

        # Along each axis
        for axis in range(arr.ndim):
            result_axis = numpy.cumsum(arr, axis=axis)
            assert numpy.all(numpy.diff(result_axis, axis=axis) >= 0)

    inner()


@given(st.data())
@settings(deadline=None)
def test_numpy_cumsum_first_element():
    """Property 4: First cumsum element equals first input element."""

    @given(arr=array_strategy(safe_floats, numpy.float64))
    def inner(arr):
        # Flattened
        result_flat = numpy.cumsum(arr)
        assert result_flat[0] == arr.flat[0]

        # Along each axis: first slice along axis equals first slice of input
        for axis in range(arr.ndim):
            result_axis = numpy.cumsum(arr, axis=axis)
            first_result = numpy.take(result_axis, indices=0, axis=axis)
            first_input = numpy.take(arr, indices=0, axis=axis)
            assert numpy.array_equal(first_result, first_input)

    inner()


@given(st.data())
@settings(deadline=None)
def test_numpy_cumsum_diff_inverse():
    """Property 5: diff of cumsum recovers the original input (excluding first)."""

    @given(arr=array_strategy(safe_ints, numpy.int64))
    def inner(arr):
        for axis in range(arr.ndim):
            result_axis = numpy.cumsum(arr, axis=axis)
            recovered = numpy.diff(result_axis, axis=axis)
            # Take the input excluding the first element along axis
            expected = numpy.take(
                arr, indices=range(1, arr.shape[axis]), axis=axis
            )
            assert numpy.array_equal(recovered, expected)

    inner()
# End program