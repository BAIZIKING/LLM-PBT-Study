from hypothesis import given, strategies as st, assume
import numpy as np
import math

# Summary: Generate 1-D or 2-D float arrays (small shapes, bounded finite values)
# and a valid `ord` chosen according to whether the input is a vector or matrix.
# Check non-negativity for true norms, zero-array gives zero, absolute homogeneity,
# and the explicit definition for finite positive vector orders.
@given(st.data())
def test_numpy_linalg_norm(data):
    ndim = data.draw(st.sampled_from([1, 2]))
    if ndim == 1:
        n = data.draw(st.integers(min_value=1, max_value=5))
        shape = (n,)
        # valid vector orders (restrict to true norms with finite positive ord here)
        ord_choice = data.draw(st.sampled_from(
            [None, 1, 2, 3, np.inf, "vec_def"]))
    else:
        r = data.draw(st.integers(min_value=1, max_value=4))
        c = data.draw(st.integers(min_value=1, max_value=4))
        shape = (r, c)
        ord_choice = data.draw(st.sampled_from(
            [None, "fro", "nuc", 1, 2, np.inf]))

    elem = st.floats(min_value=-1e3, max_value=1e3,
                     allow_nan=False, allow_infinity=False)
    flat = data.draw(st.lists(elem, min_size=int(np.prod(shape)),
                              max_size=int(np.prod(shape))))
    x = np.array(flat, dtype=float).reshape(shape)

    # Resolve the special "vec_def" marker to ord=3 for definition check
    is_vec_def = (ord_choice == "vec_def")
    ord_val = 3 if is_vec_def else ord_choice

    result = np.linalg.norm(x, ord=ord_val)

    # Property 1: non-negativity (all chosen orders are true norms => >= 0)
    assert result >= -1e-9, f"norm should be non-negative, got {result}"

    # Property 2: zero array -> zero norm
    zero_norm = np.linalg.norm(np.zeros_like(x), ord=ord_val)
    assert math.isclose(zero_norm, 0.0, abs_tol=1e-9), \
        f"norm of zeros should be 0, got {zero_norm}"

    # Property 3: absolute homogeneity: norm(s*x) == |s| * norm(x)
    s = data.draw(st.floats(min_value=-10, max_value=10,
                            allow_nan=False, allow_infinity=False))
    scaled = np.linalg.norm(s * x, ord=ord_val)
    expected_scaled = abs(s) * result
    assert math.isclose(scaled, expected_scaled, rel_tol=1e-6, abs_tol=1e-6), \
        f"homogeneity failed: norm(s*x)={scaled}, |s|*norm(x)={expected_scaled}"

    # Property 4: explicit definition for finite positive vector ord
    if is_vec_def:
        manual = np.sum(np.abs(x) ** 3) ** (1.0 / 3.0)
        assert math.isclose(result, manual, rel_tol=1e-6, abs_tol=1e-6), \
            f"definition mismatch: norm={result}, manual={manual}"
# End program