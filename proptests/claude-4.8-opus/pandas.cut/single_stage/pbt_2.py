from hypothesis import given, strategies as st, assume, settings
import numpy as np
import pandas as pd
import math

# Summary: Generate 1-D numeric arrays for `x` (including NaN/out-of-bounds cases),
# and `bins` as either a positive integer (equal-width) or a sorted sequence of
# scalar edges (optionally with duplicates). Pair `duplicates='drop'` with possibly
# non-unique edges. Vary `right`, `include_lowest`, `labels` (None or False), and
# `retbins`. Check: length preservation, NA/out-of-bounds -> NA, labels=False gives
# integer indicators in valid range, correct number of categories, and that retbins
# returns a monotonically increasing ndarray.
@given(st.data())
@settings(max_examples=300)
def test_pandas_cut(data):
    finite_floats = st.floats(
        min_value=-1e6, max_value=1e6,
        allow_nan=False, allow_infinity=False, width=32,
    )
    # Allow some NaNs in the input to test NA propagation.
    x_element = st.one_of(finite_floats, st.just(float("nan")))
    x = data.draw(st.lists(x_element, min_size=1, max_size=50), label="x")

    # Choose bins style: integer or sequence of scalars.
    bins_kind = data.draw(st.sampled_from(["int", "seq"]), label="bins_kind")

    duplicates = data.draw(st.sampled_from(["raise", "drop"]), label="duplicates")

    if bins_kind == "int":
        bins = data.draw(st.integers(min_value=1, max_value=10), label="bins_int")
        n_edges = None
    else:
        # Sorted sequence of edges; optionally non-unique to exercise duplicates.
        raw_edges = data.draw(
            st.lists(finite_floats, min_size=2, max_size=8),
            label="bins_seq",
        )
        edges = sorted(raw_edges)
        bins = edges
        n_edges = len(edges)

    right = data.draw(st.booleans(), label="right")
    include_lowest = data.draw(st.booleans(), label="include_lowest")
    labels = data.draw(st.sampled_from([None, False]), label="labels")
    retbins = data.draw(st.booleans(), label="retbins")

    # Call pandas.cut, tolerating legitimate errors documented by the API.
    try:
        result = pd.cut(
            np.array(x, dtype=float),
            bins,
            right=right,
            labels=labels,
            retbins=retbins,
            include_lowest=include_lowest,
            duplicates=duplicates,
        )
    except ValueError:
        # Legitimate failures: non-unique edges with duplicates='raise',
        # not enough unique edges after dropping, monotonicity issues, etc.
        return

    if retbins:
        out, computed_bins = result
    else:
        out = result
        computed_bins = None

    # Property 1: length preservation.
    assert len(out) == len(x)

    # Convert input to a numpy float array for NA / range reasoning.
    x_arr = np.array(x, dtype=float)
    input_nan_mask = np.isnan(x_arr)

    # Property 5: retbins returns a monotonically increasing ndarray.
    if computed_bins is not None:
        assert isinstance(computed_bins, np.ndarray)
        cb = np.asarray(computed_bins, dtype=float)
        if len(cb) >= 2:
            diffs = np.diff(cb)
            assert np.all(diffs >= 0)

    if labels is False:
        # Property 3: labels=False -> ndarray of integer indicators (NaN allowed).
        assert isinstance(out, np.ndarray)
        out_arr = np.asarray(out, dtype=float)

        # Determine number of bins from computed_bins if available.
        if computed_bins is not None:
            n_bins = max(len(np.asarray(computed_bins)) - 1, 0)
        elif bins_kind == "int":
            n_bins = bins
        else:
            n_bins = None  # unknown without computed bins

        finite_mask = ~np.isnan(out_arr)
        for v in out_arr[finite_mask]:
            # Integer indicator: equals its rounded value.
            assert float(v) == float(int(round(v)))
            assert v >= 0
            if n_bins is not None:
                # Property 6: valid indices within [0, n_bins-1].
                assert v <= n_bins - 1

        # Property 2: NaN inputs must yield NaN outputs.
        for i in range(len(x_arr)):
            if input_nan_mask[i]:
                assert np.isnan(out_arr[i])
    else:
        # labels is None -> Categorical for ndarray input.
        assert isinstance(out, pd.Categorical)

        # Property 4: number of categories matches expectation.
        if computed_bins is not None:
            expected_cats = max(len(np.asarray(computed_bins)) - 1, 0)
            assert len(out.categories) == expected_cats
        elif bins_kind == "int":
            assert len(out.categories) == bins

        # Property 2: NaN inputs must yield NA (codes == -1) outputs.
        codes = out.codes
        for i in range(len(x_arr)):
            if input_nan_mask[i]:
                assert codes[i] == -1
# End program