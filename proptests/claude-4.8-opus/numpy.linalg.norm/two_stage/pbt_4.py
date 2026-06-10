from hypothesis import given, strategies as st, assume, settings
import numpy as np
import hypothesis.extra.numpy as hnp

# Strategy for finite floats in a moderate range to avoid overflow.
safe_floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)

def array_1d_or_2d(elements=safe_floats):
    """Generate a 1-D or 2-D float array with moderate sizes."""
    shape_1d = hnp.array_shapes(min_dims=1, max_dims=1, min_side=1, max_side=8)
    shape_2d = hnp.array_shapes(min_dims=2, max_dims=2, min_side=1, max_side=8)
    return st.one_of(
        hnp.arrays(dtype=np.float64, shape=shape_1d, elements=elements),
        hnp.arrays(dtype=np.float64, shape=shape_2d, elements=elements),
    )

# Valid norm orders that obey standard norm properties (ord >= 1, inf, 'fro').
def valid_ords_for(x):
    if x.ndim == 1:
        return st.sampled_from([None, 1, 2, np.inf])
    else:  # 2-D
        return st.sampled_from([None, 'fro', 'nuc', 1, 2, np.inf])


@given(st.data())
@settings(max_examples=300)
def test_numpy_linalg_norm_property(data):
    # ---------------------------------------------------------------
    # Property 1: Non-negativity for standard norms.
    # ---------------------------------------------------------------
    x = data.draw(array_1d_or_2d(), label="x_nonneg")
    ord1 = data.draw(valid_ords_for(x), label="ord_nonneg")
    n1 = np.linalg.norm(x, ord=ord1)
    assert np.all(n1 >= -1e-9), f"Norm should be non-negative, got {n1}"

    # ---------------------------------------------------------------
    # Property 2: Absolute homogeneity (scaling).
    # norm(c * x) == |c| * norm(x)
    # ---------------------------------------------------------------
    x2 = data.draw(array_1d_or_2d(), label="x_scale")
    ord2 = data.draw(valid_ords_for(x2), label="ord_scale")
    c = data.draw(
        st.floats(min_value=-1e3, max_value=1e3, allow_nan=False,
                  allow_infinity=False, width=64),
        label="scale_c",
    )
    base = np.linalg.norm(x2, ord=ord2)
    scaled = np.linalg.norm(c * x2, ord=ord2)
    expected = abs(c) * base
    assert np.allclose(scaled, expected, rtol=1e-6, atol=1e-6), (
        f"Homogeneity failed: norm(c*x)={scaled}, |c|*norm(x)={expected}"
    )

    # ---------------------------------------------------------------
    # Property 3: Triangle inequality.
    # norm(x + y) <= norm(x) + norm(y)
    # ---------------------------------------------------------------
    # Generate a shape first, then two arrays of that shape.
    is_2d = data.draw(st.booleans(), label="tri_is_2d")
    if is_2d:
        shape = data.draw(
            hnp.array_shapes(min_dims=2, max_dims=2, min_side=1, max_side=8),
            label="tri_shape_2d",
        )
        ord3 = data.draw(st.sampled_from([None, 'fro', 1, 2, np.inf]),
                         label="ord_tri_2d")
    else:
        shape = data.draw(
            hnp.array_shapes(min_dims=1, max_dims=1, min_side=1, max_side=8),
            label="tri_shape_1d",
        )
        ord3 = data.draw(st.sampled_from([None, 1, 2, np.inf]),
                         label="ord_tri_1d")
    xa = data.draw(hnp.arrays(dtype=np.float64, shape=shape, elements=safe_floats),
                   label="tri_x")
    ya = data.draw(hnp.arrays(dtype=np.float64, shape=shape, elements=safe_floats),
                   label="tri_y")
    lhs = np.linalg.norm(xa + ya, ord=ord3)
    rhs = np.linalg.norm(xa, ord=ord3) + np.linalg.norm(ya, ord=ord3)
    assert lhs <= rhs + 1e-6 * (1 + abs(rhs)), (
        f"Triangle inequality failed: norm(x+y)={lhs} > norm(x)+norm(y)={rhs}"
    )

    # ---------------------------------------------------------------
    # Property 4: Zero norm iff zero input (for valid norm orders).
    # ---------------------------------------------------------------
    x4 = data.draw(array_1d_or_2d(), label="x_zero")
    ord4 = data.draw(valid_ords_for(x4), label="ord_zero")
    n4 = np.linalg.norm(x4, ord=ord4)
    all_zero = np.all(x4 == 0)
    if all_zero:
        assert np.allclose(n4, 0.0, atol=1e-9), (
            f"Norm of zero array should be 0, got {n4}"
        )
    else:
        assert n4 > 1e-12 * max(1.0, np.max(np.abs(x4))), (
            f"Norm of nonzero array should be positive, got {n4}"
        )

    # ---------------------------------------------------------------
    # Property 5a: Default (ord=None, axis=None) equals 2-norm of ravel.
    # Property 5b: keepdims preserves broadcastable shape.
    # ---------------------------------------------------------------
    x5 = data.draw(array_1d_or_2d(), label="x_default")
    default_norm = np.linalg.norm(x5)
    flat_2norm = np.linalg.norm(x5.ravel(), ord=2)
    assert np.allclose(default_norm, flat_2norm, rtol=1e-9, atol=1e-9), (
        f"Default norm {default_norm} != 2-norm of ravel {flat_2norm}"
    )

    # keepdims shape consistency along an axis.
    axis = data.draw(st.integers(min_value=0, max_value=x5.ndim - 1),
                     label="keepdims_axis")
    res_keep = np.linalg.norm(x5, axis=axis, keepdims=True)
    expected_shape = list(x5.shape)
    expected_shape[axis] = 1
    assert res_keep.shape == tuple(expected_shape), (
        f"keepdims shape {res_keep.shape} != expected {tuple(expected_shape)}"
    )
    # Result with keepdims must broadcast against original x.
    broadcasted = np.broadcast_shapes(res_keep.shape, x5.shape)
    assert broadcasted == x5.shape, (
        f"keepdims result {res_keep.shape} does not broadcast to {x5.shape}"
    )
# End program