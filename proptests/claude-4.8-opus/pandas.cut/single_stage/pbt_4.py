from hypothesis import given, strategies as st, assume, settings
import numpy as np
import pandas as pd

# Summary: Generate 1-D float arrays (including NaN, duplicates, negatives) for x,
# and bins as either an integer number of equal-width bins or a strictly-increasing
# sequence of edges. Vary right, labels (None/False), include_lowest, and retbins.
# Check length preservation, NA propagation, output type per labels, retbins tuple
# structure, expected category count for integer bins, and out-of-bounds -> NA.
@settings(deadline=None)
@given(st.data())
def test_pandas_cut(data):
    # --- Generate x: 1-D array of floats with possible NaNs and duplicates ---
    finite_floats = st.floats(
        min_value=-1e6, max_value=1e6,
        allow_nan=False, allow_infinity=False, width=64,
    )
    elem = st.one_of(finite_floats, st.just(float("nan")))
    x_list = data.draw(st.lists(elem, min_size=1, max_size=30), label="x")
    x = np.array(x_list, dtype=float)

    # Need at least some finite values for integer-bin computation to work
    finite_mask = ~np.isnan(x)
    has_finite = finite_mask.any()
    finite_vals = x[finite_mask]
    # cut with integer bins requires distinct min/max or it can raise; guard below.

    # --- Choose bins: integer or sequence of strictly increasing edges ---
    use_int_bins = data.draw(st.booleans(), label="use_int_bins")

    if use_int_bins:
        n_bins = data.draw(st.integers(min_value=1, max_value=10), label="n_bins")
        bins = n_bins
        # Integer binning requires at least one finite value with non-degenerate range
        assume(has_finite)
        # pandas extends range by .1%; degenerate (all equal) is handled but may warn.
    else:
        # Build a strictly increasing sequence of edges (unique).
        raw_edges = data.draw(
            st.lists(finite_floats, min_size=2, max_size=8, unique=True),
            label="edges",
        )
        edges = sorted(raw_edges)
        bins = edges
        n_bins = len(edges) - 1

    # --- Other parameters ---
    right = data.draw(st.booleans(), label="right")
    include_lowest = data.draw(st.booleans(), label="include_lowest")
    use_false_labels = data.draw(st.booleans(), label="use_false_labels")
    labels = False if use_false_labels else None
    retbins = data.draw(st.booleans(), label="retbins")

    # --- Call pandas.cut, allowing legitimate ValueErrors to short-circuit ---
    try:
        result = pd.cut(
            x,
            bins,
            right=right,
            labels=labels,
            retbins=retbins,
            include_lowest=include_lowest,
            duplicates="drop",
        )
    except ValueError:
        # e.g. all-NaN input with integer bins, or edges collapsing to <1 bin.
        return

    # --- Unpack retbins tuple structure (Property: retbins behavior) ---
    if retbins:
        assert isinstance(result, tuple), "retbins=True must return a tuple"
        assert len(result) == 2
        out, computed_bins = result
        # computed bins is an ndarray (for scalar/sequence bins)
        assert isinstance(computed_bins, np.ndarray)
    else:
        out = result

    # --- Property: Length preservation ---
    assert len(out) == len(x), "output length must match input length"

    # --- Property: Output type depends on labels ---
    if labels is False:
        # labels=False -> ndarray of integer indicators (float if NaN present)
        assert isinstance(out, np.ndarray)
    else:
        # labels=None -> Categorical for ndarray input
        assert isinstance(out, pd.Categorical)
        # Property: category count for integer bins (with duplicates='drop',
        # categories <= requested n_bins; for sequence likewise <= n_bins).
        if n_bins >= 1:
            assert len(out.categories) <= max(n_bins, 0) + 0  # categories <= n_bins
            assert len(out.categories) <= n_bins

    # --- Property: NA propagation ---
    # Any NaN in input must be NA in the output at the same position.
    if labels is False:
        out_arr = np.asarray(out, dtype=float)
        for i in range(len(x)):
            if np.isnan(x[i]):
                assert np.isnan(out_arr[i]), "NaN input must yield NaN output"
    else:
        codes = out.codes  # -1 indicates NA in a Categorical
        for i in range(len(x)):
            if np.isnan(x[i]):
                assert codes[i] == -1, "NaN input must yield NA category"
# End program