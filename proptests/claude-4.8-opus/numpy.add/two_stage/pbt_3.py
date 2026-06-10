from hypothesis import given, settings, strategies as st
import numpy as np
import hypothesis.extra.numpy as hnp


# Bounded, finite float64 elements to avoid overflow / NaN / inf in sums.
safe_floats = st.floats(
    min_value=-1e150,
    max_value=1e150,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)


def _array(d, shape):
    return d.draw(hnp.arrays(dtype=np.float64, shape=shape, elements=safe_floats))


@given(st.data())
@settings(max_examples=300)
def test_numpy_add_property(data):
    # --- Draw two broadcastable shapes ---
    bshapes = data.draw(
        hnp.mutually_broadcastable_shapes(num_shapes=2, max_dims=3, max_side=5)
    )
    shape1, shape2 = bshapes.input_shapes
    broadcast_shape = bshapes.result_shape

    x1 = _array(data, shape1)
    x2 = _array(data, shape2)

    # === Property 1: Commutativity ===
    r1 = np.add(x1, x2)
    r2 = np.add(x2, x1)
    assert np.array_equal(r1, r2), "add is not commutative"

    # === Property 2: Equivalence to the + operator ===
    r_plus = x1 + x2
    assert np.array_equal(np.add(x1, x2), r_plus), "np.add differs from + operator"

    # === Property 3: Output shape matches broadcast shape ===
    out = np.add(x1, x2)
    assert out.shape == broadcast_shape, (
        f"output shape {out.shape} != broadcast shape {broadcast_shape}"
    )
    # Scalar-in -> scalar-out behaviour
    s1 = data.draw(safe_floats)
    s2 = data.draw(safe_floats)
    scalar_result = np.add(s1, s2)
    assert np.isscalar(scalar_result) or np.ndim(scalar_result) == 0, (
        "adding two scalars should yield a scalar"
    )

    # === Property 4: Identity element (adding zero) ===
    zero = np.zeros_like(x1)
    id_result = np.add(x1, zero)
    assert np.array_equal(id_result, x1), "adding zero changed the array"

    # === Property 5: Selective assignment with `where` ===
    # Allocate a pre-filled out array of the broadcast shape.
    sentinel = data.draw(safe_floats)
    out_arr = np.full(broadcast_shape, sentinel, dtype=np.float64)
    where_mask = data.draw(
        hnp.arrays(dtype=np.bool_, shape=broadcast_shape, elements=st.booleans())
    )

    expected_full = np.add(x1, x2)  # full element-wise sum
    np.add(x1, x2, out=out_arr, where=where_mask)

    # Where mask is True -> equals the sum; where False -> retains sentinel.
    assert np.array_equal(out_arr[where_mask], expected_full[where_mask]), (
        "masked-True locations do not hold the sum"
    )
    retained = np.full(broadcast_shape, sentinel, dtype=np.float64)
    assert np.array_equal(out_arr[~where_mask], retained[~where_mask]), (
        "masked-False locations did not retain original out values"
    )
# End program