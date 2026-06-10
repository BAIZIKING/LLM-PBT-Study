from hypothesis import given, strategies as st
import numpy as np

# Summary: This test generates random arrays of varying shapes, data types, and orders to test the `numpy.linalg.norm` function. It ensures that the calculated norm is always non-negative and that the Frobenius and nuclear norms are only calculated for 2D matrices.

@given(
    x=st.arrays(
        dtype=st.floats(allow_nan=False, allow_infinity=False),  # Avoid NaN and infinity for numerical stability
        shape=st.tuples(st.integers(min_value=0, max_value=3), st.integers(min_value=0, max_value=3)),  # Generate arrays of up to 3 dimensions
        elements=st.floats(allow_nan=False, allow_infinity=False)
    ),
    ord=st.sampled_from([None, 2, -2, np.inf, -np.inf, 1, -1, 'fro', 'nuc']),  # Test various ord values
    axis=st.one_of(st.none(), st.integers(), st.tuples(st.integers(), st.integers())),  # Test different axis options
    keepdims=st.booleans()
)
def test_numpy_linalg_norm(x, ord, axis, keepdims):
    try:
        norm = np.linalg.norm(x, ord=ord, axis=axis, keepdims=keepdims)
        assert np.all(norm >= 0)  # Norm should always be non-negative

        if ord in ('fro', 'nuc'):
            assert x.ndim == 2, "Frobenius and nuclear norms are only defined for 2D matrices"
    except ValueError as e:
        if ord in ('fro', 'nuc') and x.ndim != 2:
            pass  # Expected ValueError for Frobenius and nuclear norms with non-2D arrays
        else:
            raise e  # Raise other ValueErrors
# End program