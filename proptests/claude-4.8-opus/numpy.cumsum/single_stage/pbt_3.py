from hypothesis import given, strategies as st, settings
import numpy as np
from hypothesis.extra.numpy import arrays, array_shapes, floating_dtypes, integer_dtypes

# Summary: Generate numpy arrays of varied shapes (1D-3D) and dtypes (ints/floats)
# with bounded element values, plus a valid axis (None or a real axis index).
# Verify cumsum's shape/size guarantees, that the last cumulative value equals
# the total sum, and that taking discrete differences of the cumsum recovers
# the original array, all with tolerance for floating-point roundoff.
@given(st.data())
@settings(max_examples=300)
def test_numpy_cumsum(data):
    # Choose dtype: integers or floats
    dtype = data.draw(st.one_of(
        integer_dtypes(endianness="=", sizes=(32, 64)),
        floating_dtypes(endianness="=", sizes=(32, 64)),
    ))
    shape = data.draw(array_shapes(min_dims=1, max_dims=3, min_side=1, max_side=5))

    is_float = np.issubdtype(dtype, np.floating)
    if is_float:
        elements = st.floats(min_value=-1e3, max_value=1e3,
                             allow_nan=False, allow_infinity=False, width=32)
    else:
        elements = st.integers(min_value=-1000, max_value=1000)

    a = data.draw(arrays(dtype=dtype, shape=shape, elements=elements))

    ndim = a.ndim
    axis = data.draw(st.one_of(st.none(), st.integers(min_value=0, max_value=ndim - 1)))

    result = np.cumsum(a, axis=axis)

    # Property 1: size is preserved
    assert result.size == a.size

    # Property 2: shape behavior depends on axis
    if axis is None:
        assert result.ndim == 1
        assert result.shape == (a.size,)
    else:
        assert result.shape == a.shape

    # Tolerance setup
    rtol, atol = (1e-3, 1e-3) if is_float else (0, 0)

    # Property 3: last cumulative value equals the total sum
    flat_cumsum = np.cumsum(a)  # always flattened
    if a.size > 0:
        total = np.sum(a, dtype=flat_cumsum.dtype)
        assert np.allclose(flat_cumsum[-1], total, rtol=rtol, atol=atol)

    # Property 4: differences of cumsum recover original array along the axis
    if axis is not None:
        recovered = np.diff(result, axis=axis)
        original_tail = np.take(a, indices=range(1, a.shape[axis]), axis=axis)
        assert np.allclose(recovered, original_tail, rtol=rtol, atol=atol)

        # Property 5: first element along axis equals original first element
        first_cumsum = np.take(result, indices=0, axis=axis)
        first_orig = np.take(a, indices=0, axis=axis)
        assert np.allclose(first_cumsum, first_orig, rtol=rtol, atol=atol)
    else:
        # For flattened, first element equals first flattened element
        if a.size > 0:
            assert np.allclose(flat_cumsum[0], a.flatten()[0], rtol=rtol, atol=atol)
# End program