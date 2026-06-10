from hypothesis import given, strategies as st, assume
import numpy as np
import math

# Summary: Generate small 1-D vectors or 2-D matrices of finite floats (no NaN/inf,
# bounded magnitude), then pick an `ord` value that is valid AND a genuine norm
# for that dimensionality. Check absolute homogeneity (norm(c*x) == |c|*norm(x)),
# non-negativity, zero-array gives 0, and keepdims consistency.
@given(st.data())
def test_numpy_linalg_norm(data):
    # --- choose dimensionality ---
    ndim = data.draw(st.sampled_from([1, 2]), label="ndim")

    finite_floats = st.floats(
        min_value=-1e6, max_value=1e6,
        allow_nan=False, allow_infinity=False, width=64,
    )

    if ndim == 1:
        n = data.draw(st.integers(min_value=1, max_value=5), label="n")
        shape = (n,)
        # genuine vector norms (ord >= 1 or inf): 1, 2, 3, inf
        ord_val = data.draw(st.sampled_from([None, 1, 2, 3, np.inf]), label="ord")
        axis = None
    else:
        r = data.draw(st.integers(min_value=1, max_value=4), label="r")
        c = data.draw(st.integers(min_value=1, max_value=4), label="c")
        shape = (r, c)
        # genuine matrix norms: 'fro', 'nuc', 1, 2, inf
        ord_val = data.draw(
            st.sampled_from([None, "fro", "nuc", 1, 2, np.inf]), label="ord"
        )
        axis = None

    elems = data.draw(
        st.lists(finite_floats, min_size=int(np.prod(shape)),
                 max_size=int(np.prod(shape))),
        label="elems",
    )
    x = np.array(elems, dtype=np.float64).reshape(shape)

    # --- compute base norm ---
    base = np.linalg.norm(x, ord=ord_val, axis=axis)

    # Property 1: non-negativity (genuine norms only)
    assert base >= -1e-9, f"norm should be non-negative, got {base}"

    # Property 2: zero array -> 0
    zeros = np.zeros(shape, dtype=np.float64)
    zn = np.linalg.norm(zeros, ord=ord_val, axis=axis)
    assert math.isclose(zn, 0.0, abs_tol=1e-9), f"norm of zeros should be 0, got {zn}"

    # Property 3: absolute homogeneity: norm(s*x) == |s| * norm(x)
    s = data.draw(
        st.floats(min_value=-10, max_value=10, allow_nan=False,
                  allow_infinity=False, width=64),
        label="scalar",
    )
    scaled = np.linalg.norm(s * x, ord=ord_val, axis=axis)
    expected = abs(s) * base
    assert math.isclose(scaled, expected, rel_tol=1e-6, abs_tol=1e-6), (
        f"homogeneity failed: norm({s}*x)={scaled}, |{s}|*norm(x)={expected}"
    )

    # Property 4: keepdims consistency (axis=None normed over all axes)
    kd = np.linalg.norm(x, ord=ord_val, axis=axis, keepdims=True)
    assert kd.ndim == x.ndim, f"keepdims should preserve ndim, got {kd.ndim}"
    assert all(d == 1 for d in kd.shape), f"keepdims dims should be 1, got {kd.shape}"
    assert math.isclose(float(np.squeeze(kd)), float(base),
                        rel_tol=1e-9, abs_tol=1e-9), (
        f"keepdims value {float(np.squeeze(kd))} != base {float(base)}"
    )
# End program