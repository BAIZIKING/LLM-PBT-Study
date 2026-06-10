from hypothesis import given, strategies as st, assume, settings
import numpy as np
import numpy.linalg as LA
import math

# Summary: Generate 1-D and 2-D float arrays (including zeros, single elements),
# pick an `ord` valid for the array's dimensionality from the documented set, and a
# random `keepdims`. Check: (1) finiteness/realness, (2) non-negativity for true-norm
# orders, (3) absolute homogeneity norm(s*x) == |s|*norm(x), and (4) keepdims consistency.
@settings(deadline=None)
@given(st.data())
def test_numpy_linalg_norm(data):
    # Choose dimensionality (1-D or 2-D so `ord` is well-defined with axis=None)
    ndim = data.draw(st.sampled_from([1, 2]), label="ndim")

    finite_floats = st.floats(
        min_value=-1e6, max_value=1e6,
        allow_nan=False, allow_infinity=False, width=64,
    )

    if ndim == 1:
        n = data.draw(st.integers(min_value=1, max_value=8), label="n")
        x = np.array(
            data.draw(st.lists(finite_floats, min_size=n, max_size=n), label="x1d"),
            dtype=float,
        )
        ord_choices = [None, 1, -1, 2, -2, 3, -3, 0, np.inf, -np.inf]
    else:
        rows = data.draw(st.integers(min_value=1, max_value=5), label="rows")
        cols = data.draw(st.integers(min_value=1, max_value=5), label="cols")
        flat = data.draw(
            st.lists(finite_floats, min_size=rows * cols, max_size=rows * cols),
            label="x2d",
        )
        x = np.array(flat, dtype=float).reshape(rows, cols)
        ord_choices = [None, "fro", "nuc", 1, -1, 2, -2, np.inf, -np.inf]

    ord_ = data.draw(st.sampled_from(ord_choices), label="ord")
    keepdims = data.draw(st.booleans(), label="keepdims")

    # Orders that constitute true (sub-)norms -> guaranteed non-negative.
    def is_true_norm(o):
        if o is None or o == "fro" or o == "nuc":
            return True
        if o == np.inf:
            return True
        if isinstance(o, (int, float)) and not isinstance(o, bool):
            # ord >= 1 (and not inf-special handled above) gives a true norm
            return o >= 1
        return False

    result = LA.norm(x, ord=ord_, keepdims=keepdims)
    res_arr = np.asarray(result)

    # Property 1: result is finite and real
    assert np.all(np.isfinite(res_arr)), f"Non-finite result {result} for ord={ord_}"
    assert np.isrealobj(res_arr), "Norm should be real for real input"

    # Property 2: non-negativity for true norms
    if is_true_norm(ord_):
        assert np.all(res_arr >= -1e-9), f"Norm negative {result} for ord={ord_}"

    # Property 4: keepdims consistency (compare squeezed values)
    result_nokeep = LA.norm(x, ord=ord_, keepdims=False)
    np.testing.assert_allclose(
        np.squeeze(res_arr),
        np.squeeze(np.asarray(result_nokeep)),
        rtol=1e-6, atol=1e-9,
    )

    # Property 3: absolute homogeneity  norm(s*x) == |s| * norm(x)
    s = data.draw(
        st.floats(min_value=-100, max_value=100,
                  allow_nan=False, allow_infinity=False),
        label="scalar",
    )
    base = LA.norm(x, ord=ord_, keepdims=False)
    scaled = LA.norm(s * x, ord=ord_, keepdims=False)
    expected = abs(s) * np.asarray(base)
    # Tolerances scaled to magnitude to absorb floating point error.
    np.testing.assert_allclose(
        np.asarray(scaled), expected,
        rtol=1e-5,
        atol=1e-6 + 1e-6 * np.max(np.abs(expected)),
    )
# End program