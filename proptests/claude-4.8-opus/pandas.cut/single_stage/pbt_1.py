from hypothesis import given, strategies as st
import numpy as np
import pandas as pd

# Summary:
# Generate a 1-D list of finite floats (with possible duplicates / varied magnitude)
# as input x. The `bins` argument is either a positive integer (equal-width bins) or
# a sorted, unique sequence of scalar edges spanning the data range. Booleans control
# right/include_lowest/retbins, and labels is chosen from {None, False} to exercise
# both the Categorical/Interval and integer-ndarray return paths. We then verify:
#  - output length equals input length,
#  - the documented return-type contract for labels and retbins,
#  - the bins edge array length when integer bins are used,
#  - that each non-NA value actually lies within its assigned interval.
@given(st.data())
def test_pandas_cut(data):
    # ---- Generate input array x ----
    x_list = data.draw(
        st.lists(
            st.floats(
                min_value=-1e6,
                max_value=1e6,
                allow_nan=False,
                allow_infinity=False,
            ),
            min_size=1,
            max_size=30,
        )
    )
    x = np.array(x_list, dtype=float)

    # ---- Choose bins: integer or sequence of scalars ----
    use_int_bins = data.draw(st.booleans())
    lo, hi = float(np.min(x)), float(np.max(x))

    if use_int_bins:
        n_bins = data.draw(st.integers(min_value=1, max_value=10))
        bins = n_bins
    else:
        # Build a sorted, unique edge sequence that fully spans the data.
        # Extend slightly beyond the data so all values fall inside.
        span = (hi - lo) if hi > lo else 1.0
        n_edges = data.draw(st.integers(min_value=2, max_value=8))
        edges = sorted(
            np.linspace(lo - 0.01 * span - 1.0, hi + 0.01 * span + 1.0, n_edges)
        )
        # Ensure uniqueness (linspace already gives unique values here)
        bins = list(edges)
        n_bins = n_edges - 1

    # ---- Other parameters ----
    right = data.draw(st.booleans())
    include_lowest = data.draw(st.booleans())
    retbins = data.draw(st.booleans())
    labels = data.draw(st.sampled_from([None, False]))
    precision = data.draw(st.integers(min_value=1, max_value=6))

    result = pd.cut(
        x,
        bins,
        right=right,
        labels=labels,
        retbins=retbins,
        precision=precision,
        include_lowest=include_lowest,
    )

    # ---- Property 3 (part): retbins contract ----
    if retbins:
        assert isinstance(result, tuple) and len(result) == 2
        out, out_bins = result
        assert isinstance(out_bins, np.ndarray)
        # For integer bins, edges count = n_bins + 1
        assert len(out_bins) == n_bins + 1
    else:
        out = result

    # ---- Property 1: length preservation ----
    assert len(out) == len(x)

    # ---- Property 2: return-type contract ----
    if labels is False:
        assert isinstance(out, np.ndarray)
    else:  # labels is None
        assert isinstance(out, pd.Categorical)

    # ---- Properties 4 & 5: bin membership / NA handling ----
    if labels is None:
        # out is a Categorical of Intervals; check membership for non-NA values.
        for val, interval in zip(x, out):
            if interval is None or (isinstance(interval, float) and np.isnan(interval)):
                # NA -> value was out of bounds; that's allowed.
                continue
            # pandas Interval supports `in`
            assert val in interval, (
                f"value {val} not contained in assigned interval {interval}"
            )
    else:
        # labels is False -> integer codes; non-NA codes must be valid bin indices.
        for code in out:
            if np.isnan(code):
                continue
            assert 0 <= int(code) < n_bins, (
                f"bin code {code} out of valid range [0, {n_bins})"
            )
# End program