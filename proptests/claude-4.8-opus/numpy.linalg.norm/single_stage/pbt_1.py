from hypothesis import given, strategies as st, assume, settings
import numpy as np
import hypothesis.extra.numpy as hnp

# Summary: Generate 1-D and 2-D float arrays (bounded magnitude, no nan/inf) along
# with a context-appropriate `ord` value (None, 'fro'/'nuc' for matrices, inf/-inf,
# and positive integers >= 1 which are genuine norms). Then verify the defining
# norm properties: non-negativity and absolute homogeneity norm(c*x) == |c|*norm(x),
# plus the Frobenius/ravel equivalence and keepdims shape behavior.
@given(st.data())
@settings(max_examples=300)
def test_numpy_linalg_norm(data):
    # --- Generate the input array x (1-D or 2-D) ---
    ndim = data.draw(st.sampled_from([1, 2]), label="ndim")
    shape = data.draw(
        hnp.array_shapes(min_dims=ndim, max_dims=ndim, min_side=1, max_side=4),
        label="shape",
    )
    elements = st.floats(
        min_value=-1e6, max_value=1e6,
        allow_nan=False, allow_infinity=False, width=64,
    )
    x = data.draw(hnp.arrays(dtype=np.float64, shape=shape, elements=elements),
                  label="x")

    # --- Generate a context-appropriate `ord` (genuine norms only) ---
    if ndim == 1:
        ord_choices = [None, np.inf, -np.inf, 1, 2, 3]
    else:  # ndim == 2
        ord_choices = [None, 'fro', 'nuc', np.inf, -np.inf, 1, 2]
    ord_val = data.draw(st.sampled_from(ord_choices), label="ord")

    n = np.linalg.norm(x, ord=ord_val)

    # Property 1: Genuine norms are non-negative and finite.
    assert np.isfinite(n)
    assert n >= -1e-9  # allow tiny negative floating error around zero

    # Property 2: Absolute homogeneity: norm(c*x) == |c| * norm(x).
    c = data.draw(
        st.floats(min_value=-100, max_value=100,
                  allow_nan=False, allow_infinity=False, width=64),
        label="c",
    )
    n_scaled = np.linalg.norm(c * x, ord=ord_val)
    expected = abs(c) * n
    assert np.allclose(n_scaled, expected, rtol=1e-6, atol=1e-6)

    # Property 3: Default ord (None) equals 2-norm of the raveled array.
    if ord_val is None:
        n_ravel = np.linalg.norm(x.ravel())
        assert np.allclose(n, n_ravel, rtol=1e-9, atol=1e-9)
        if ndim == 2:
            # For 2-D, default ord (None) is the Frobenius norm.
            n_fro = np.linalg.norm(x, ord='fro')
            assert np.allclose(n, n_fro, rtol=1e-9, atol=1e-9)

    # Property 4: keepdims preserves the number of dimensions of x.
    n_keep = np.linalg.norm(x, ord=ord_val, keepdims=True)
    assert n_keep.ndim == x.ndim
    assert all(s == 1 for s in n_keep.shape)
# End program