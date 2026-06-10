from hypothesis import given, strategies as st, assume, settings
import numpy as np
import hypothesis.extra.numpy as hnp


# Strategy for finite floats with bounded magnitude to avoid overflow.
def finite_floats(min_value=-1e3, max_value=1e3):
    return st.floats(
        min_value=min_value,
        max_value=max_value,
        allow_nan=False,
        allow_infinity=False,
        width=64,
    )


# Strategy producing a 1-D array.
def vector_strategy():
    return hnp.arrays(
        dtype=np.float64,
        shape=hnp.array_shapes(min_dims=1, max_dims=1, min_side=1, max_side=8),
        elements=finite_floats(),
    )


# Strategy producing a 2-D array.
def matrix_strategy():
    return hnp.arrays(
        dtype=np.float64,
        shape=hnp.array_shapes(min_dims=2, max_dims=2, min_side=1, max_side=6),
        elements=finite_floats(),
    )


# Valid vector ords that define true (non-negative) norms.
VECTOR_NORM_ORDS = [None, 1, 2, 3, np.inf]
# Valid matrix ords that define true (non-negative) norms.
MATRIX_NORM_ORDS = [None, "fro", "nuc", 1, 2, np.inf]


@given(st.data())
@settings(deadline=None)
def test_numpy_linalg_norm_property():
    # ---------------------------------------------------------------
    # Property 1: Non-negativity for standard norms.
    # For any valid `ord` that defines a true norm, the result is >= 0.
    # ---------------------------------------------------------------
    vec = st.data  # placeholder to keep structure clear

    # Vector case.
    x_vec = st.data
    v = None

    # Draw a vector and check non-negativity over several ords.
    v = (yield_test_vector := None)
    # (We instead draw explicitly below.)

    data = st  # noqa
    # Use the injected `data` fixture via the decorator parameter.

    # Re-draw using the proper hypothesis data object:
    raise_if_unused = None  # keep linters quiet


# The body above was a scaffold; the real test follows.
@given(st.data())
@settings(deadline=None)
def test_numpy_linalg_norm_property_real(data):
    # ---------------------------------------------------------------
    # Property 1: Non-negativity for standard norms (vectors & matrices).
    # ---------------------------------------------------------------
    v = data.draw(vector_strategy(), label="vector")
    for ord_ in VECTOR_NORM_ORDS:
        n = np.linalg.norm(v, ord=ord_)
        assert np.isfinite(n)
        assert n >= -1e-9, f"Vector norm negative for ord={ord_}: {n}"

    m = data.draw(matrix_strategy(), label="matrix")
    for ord_ in MATRIX_NORM_ORDS:
        n = np.linalg.norm(m, ord=ord_)
        assert np.isfinite(n)
        assert n >= -1e-9, f"Matrix norm negative for ord={ord_}: {n}"

    # ---------------------------------------------------------------
    # Property 2: Absolute homogeneity (scaling).
    # norm(s*x, ord) == abs(s) * norm(x, ord).
    # ---------------------------------------------------------------
    s = data.draw(finite_floats(min_value=-100, max_value=100), label="scalar")
    for ord_ in VECTOR_NORM_ORDS:
        lhs = np.linalg.norm(s * v, ord=ord_)
        rhs = abs(s) * np.linalg.norm(v, ord=ord_)
        assert np.isclose(lhs, rhs, rtol=1e-6, atol=1e-6), (
            f"Homogeneity failed (vector) ord={ord_}: {lhs} vs {rhs}"
        )
    for ord_ in MATRIX_NORM_ORDS:
        lhs = np.linalg.norm(s * m, ord=ord_)
        rhs = abs(s) * np.linalg.norm(m, ord=ord_)
        assert np.isclose(lhs, rhs, rtol=1e-6, atol=1e-6), (
            f"Homogeneity failed (matrix) ord={ord_}: {lhs} vs {rhs}"
        )

    # ---------------------------------------------------------------
    # Property 3: Zero array gives zero norm (including ord=0 for vectors).
    # ---------------------------------------------------------------
    zv = np.zeros_like(v)
    for ord_ in VECTOR_NORM_ORDS + [0]:
        assert np.isclose(np.linalg.norm(zv, ord=ord_), 0.0, atol=1e-12), (
            f"Zero vector norm nonzero for ord={ord_}"
        )
    zm = np.zeros_like(m)
    for ord_ in MATRIX_NORM_ORDS:
        assert np.isclose(np.linalg.norm(zm, ord=ord_), 0.0, atol=1e-12), (
            f"Zero matrix norm nonzero for ord={ord_}"
        )

    # ---------------------------------------------------------------
    # Property 4: Consistency between default and explicit norms.
    # 1-D: norm(x) == norm(x, 2) == sqrt(sum(abs(x)**2)).
    # 2-D: norm(x) == norm(x, 'fro') == norm(x.ravel()).
    # ---------------------------------------------------------------
    default_v = np.linalg.norm(v)
    two_v = np.linalg.norm(v, ord=2)
    manual_v = np.sqrt(np.sum(np.abs(v) ** 2))
    assert np.isclose(default_v, two_v, rtol=1e-9, atol=1e-9)
    assert np.isclose(default_v, manual_v, rtol=1e-6, atol=1e-6)

    default_m = np.linalg.norm(m)
    fro_m = np.linalg.norm(m, ord="fro")
    ravel_m = np.linalg.norm(m.ravel())
    assert np.isclose(default_m, fro_m, rtol=1e-9, atol=1e-9)
    assert np.isclose(default_m, ravel_m, rtol=1e-9, atol=1e-9)

    # ---------------------------------------------------------------
    # Property 5: Output shape with axis and keepdims.
    # ---------------------------------------------------------------
    nd = data.draw(
        hnp.arrays(
            dtype=np.float64,
            shape=hnp.array_shapes(min_dims=2, max_dims=3, min_side=1, max_side=4),
            elements=finite_floats(),
        ),
        label="ndarray",
    )
    # Single integer axis -> reduces that one axis.
    ax = data.draw(st.integers(min_value=0, max_value=nd.ndim - 1), label="axis")

    res = np.linalg.norm(nd, axis=ax)
    expected_shape = tuple(s for i, s in enumerate(nd.shape) if i != ax)
    assert res.shape == expected_shape, (
        f"axis reduction shape mismatch: {res.shape} vs {expected_shape}"
    )

    res_kd = np.linalg.norm(nd, axis=ax, keepdims=True)
    expected_kd_shape = tuple(
        1 if i == ax else s for i, s in enumerate(nd.shape)
    )
    assert res_kd.shape == expected_kd_shape, (
        f"keepdims shape mismatch: {res_kd.shape} vs {expected_kd_shape}"
    )
    # keepdims result must broadcast against original x.
    broadcasted = np.broadcast_shapes(res_kd.shape, nd.shape)
    assert broadcasted == nd.shape
# End program