from hypothesis import given, strategies as st
import pandas as pd
import numpy as np
import pandas.api.types as ptypes

# Summary: Generate a 1-D list of finite floats as `x`, and bins as either an
# integer (>=1) number of equal-width bins or a sorted, unique sequence of edges.
# Randomly vary `right`, `include_lowest`, `labels` (None/False), and `retbins`.
# Check: length preservation, output type by `labels`, category count for int
# bins, retbins tuple structure, and out-of-bounds -> NaN for sequence bins.
@given(st.data())
def test_pandas_cut(data):
    # Generate input array x: 1-D finite floats
    x = data.draw(
        st.lists(
            st.floats(min_value=-1e6, max_value=1e6,
                      allow_nan=False, allow_infinity=False),
            min_size=1, max_size=30,
        )
    )

    # Decide bins type: integer vs. sequence of scalars
    use_int_bins = data.draw(st.booleans())
    if use_int_bins:
        bins = data.draw(st.integers(min_value=1, max_value=10))
    else:
        edges = data.draw(
            st.lists(
                st.floats(min_value=-1e6, max_value=1e6,
                          allow_nan=False, allow_infinity=False),
                min_size=2, max_size=8, unique=True,
            )
        )
        edges = sorted(edges)
        bins = edges

    right = data.draw(st.booleans())
    include_lowest = data.draw(st.booleans())
    labels = data.draw(st.sampled_from([None, False]))
    retbins = data.draw(st.booleans())

    # cut requires len(x) > 0 and, for integer bins, x cannot be all-equal
    # without producing degenerate behavior; pandas handles it, so just call.
    try:
        result = pd.cut(
            x, bins, right=right, labels=labels,
            retbins=retbins, include_lowest=include_lowest,
        )
    except ValueError:
        # e.g. duplicate bin edges with default duplicates='raise',
        # or other invalid configurations. These are documented behaviors.
        return

    # Unpack retbins
    if retbins:
        assert isinstance(result, tuple) and len(result) == 2, \
            "retbins=True must return a 2-tuple"
        out, computed_bins = result
        # Property: bins array is an ndarray of edges
        computed_bins = np.asarray(computed_bins)
        # Property (integer bins): n bins => n+1 edges
        if use_int_bins:
            assert len(computed_bins) == bins + 1, \
                "integer bins should produce bins+1 edges"
    else:
        out = result

    # Property 1: Length preservation
    assert len(out) == len(x), "output length must equal input length"

    # Property 2 & 3: output type by `labels`
    if labels is False:
        # Returns ndarray of integer indicators (NaN -> float dtype)
        out_arr = np.asarray(out)
        assert isinstance(out_arr, np.ndarray), \
            "labels=False must yield an ndarray"
    elif labels is None:
        # Non-Series input -> Categorical
        assert isinstance(out, pd.Categorical), \
            "labels=None on array input must yield a Categorical"
        # Property: integer bins => exactly that many categories
        if use_int_bins:
            assert len(out.categories) == bins, \
                "integer bins should yield that many categories"
        # Property: default ordered=True yields an ordered Categorical
        assert out.ordered is True, \
            "default ordered=True should produce ordered Categorical"

    # Property: Out-of-bounds -> NaN (only meaningful for explicit edges)
    if not use_int_bins and labels is None:
        lo, hi = bins[0], bins[-1]
        codes = out.codes
        for val, code in zip(x, codes):
            if val < lo or val > hi:
                assert code == -1, \
                    "values strictly out of bounds must be NaN (code -1)"
# End program