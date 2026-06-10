from hypothesis import given, strategies as st
import numpy as np
import pandas as pd

# Summary: Generate a 1-D list of finite floats as `x`, an integer number of
# `bins`, plus boolean/None flags (right, include_lowest, labels in {None, False}),
# and a small precision. Then verify: (1) output length equals input length,
# (2) labels=False yields integer bin indices within [0, bins-1] for all finite
# values with no NaN introduced, (3) retbins returns bins+1 monotonically
# increasing edges, and (4) labels=None yields a Categorical with `bins` categories.
@given(st.data())
def test_pandas_cut(data):
    # Generate input array x of finite, bounded floats
    x = data.draw(
        st.lists(
            st.floats(
                min_value=-1e6,
                max_value=1e6,
                allow_nan=False,
                allow_infinity=False,
                width=64,
            ),
            min_size=1,
            max_size=50,
        ),
        label="x",
    )

    # Number of equal-width bins
    n_bins = data.draw(st.integers(min_value=1, max_value=10), label="n_bins")

    # Other parameters
    right = data.draw(st.booleans(), label="right")
    include_lowest = data.draw(st.booleans(), label="include_lowest")
    labels = data.draw(st.sampled_from([None, False]), label="labels")
    precision = data.draw(st.integers(min_value=1, max_value=6), label="precision")

    arr = np.array(x, dtype=float)

    result, bins = pd.cut(
        arr,
        bins=n_bins,
        right=right,
        labels=labels,
        retbins=True,
        precision=precision,
        include_lowest=include_lowest,
    )

    # Property 1: Length preservation
    assert len(result) == len(arr), (
        f"Output length {len(result)} != input length {len(arr)}"
    )

    # Property 3: retbins returns bins+1 monotonically increasing edges
    assert len(bins) == n_bins + 1, (
        f"Expected {n_bins + 1} bin edges, got {len(bins)}"
    )
    diffs = np.diff(bins)
    assert np.all(diffs > 0), f"Bin edges not strictly increasing: {bins}"

    if labels is False:
        # Property 2: integer bin indicators, in range, no NaN introduced
        res_arr = np.asarray(result, dtype=float)

        # No finite input value should produce NaN (range is extended by 0.1%)
        finite_mask = np.isfinite(arr)
        assert not np.any(np.isnan(res_arr[finite_mask])), (
            "Finite input values unexpectedly mapped to NaN"
        )

        # All non-NaN indices must be integers within [0, n_bins - 1]
        valid = res_arr[~np.isnan(res_arr)]
        assert np.all(valid == np.floor(valid)), "Bin indicators are not integers"
        assert np.all(valid >= 0), "Found negative bin index"
        assert np.all(valid <= n_bins - 1), (
            f"Bin index exceeds maximum allowed {n_bins - 1}"
        )
    else:
        # labels is None: result should be a Categorical with n_bins categories
        assert isinstance(result, pd.Categorical), (
            f"Expected Categorical, got {type(result)}"
        )
        assert len(result.categories) == n_bins, (
            f"Expected {n_bins} categories, got {len(result.categories)}"
        )
        # No finite input value should map to NaN
        finite_mask = np.isfinite(arr)
        codes = np.asarray(result.codes)
        assert not np.any(codes[finite_mask] == -1), (
            "Finite input values unexpectedly mapped to NaN category"
        )
# End program