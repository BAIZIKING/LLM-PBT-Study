from hypothesis import given, strategies as st, settings
import numpy as np
import hypothesis.extra.numpy as hnp

# Safe finite floats to avoid overflow/inf/nan complications.
SAFE_FLOATS = st.floats(
    min_value=-1e150,
    max_value=1e150,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)

SHAPES = hnp.array_shapes(min_dims=0, max_dims=4, min_side=0, max_side=5)


def arrays_of_shape(shape):
    return hnp.arrays(dtype=np.float64, shape=shape, elements=SAFE_FLOATS)


@given(st.data())
@settings(max_examples=300)
def test_numpy_add_property(data):
    # Draw a common shape and arrays for the various properties.
    shape = data.draw(SHAPES, label="shape")
    x1 = data.draw(arrays_of_shape(shape), label="x1")
    x2 = data.draw(arrays_of_shape(shape), label="x2")
    x3 = data.draw(arrays_of_shape(shape), label="x3")

    # ---- Property 1: Commutativity ----
    np.testing.assert_array_equal(np.add(x1, x2), np.add(x2, x1))

    # ---- Property 2: Equivalence to the + operator ----
    np.testing.assert_array_equal(np.add(x1, x2), x1 + x2)

    # ---- Property 3: Identity with zero ----
    zeros = np.zeros(shape, dtype=np.float64)
    np.testing.assert_array_equal(np.add(x1, zeros), x1)

    # ---- Property 4: Output shape equals broadcasted shape ----
    result = np.add(x1, x2)
    expected_shape = np.broadcast_shapes(x1.shape, x2.shape)
    assert result.shape == expected_shape

    # Scalar case: both inputs scalars -> scalar output.
    s1 = data.draw(SAFE_FLOATS, label="s1")
    s2 = data.draw(SAFE_FLOATS, label="s2")
    scalar_result = np.add(s1, s2)
    assert np.isscalar(scalar_result) or scalar_result.ndim == 0

    # ---- Property 5: Associativity (approximate for floats) ----
    left = np.add(np.add(x1, x2), x3)
    right = np.add(x1, np.add(x2, x3))
    np.testing.assert_allclose(left, right, rtol=1e-9, atol=1e-12)
# End program