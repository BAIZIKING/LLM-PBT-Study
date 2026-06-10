from hypothesis import given, strategies as st, assume, settings
import numpy as np
import pandas as pd
import math

finite_floats = st.floats(
    min_value=-1e6, max_value=1e6,
    allow_nan=False, allow_infinity=False, width=64,
)
floats_with_nan = st.one_of(finite_floats, st.just(float("nan")))
input_arrays = st.lists(floats_with_nan, min_size=1, max_size=50)


def _increasing_bins(draw, min_edges=2, max_edges=8):
    edges = draw(st.lists(finite_floats, min_size=min_edges,
                          max_size=max_edges, unique=True))
    edges = sorted(edges)
    assume(all((edges[i + 1] - edges[i]) > 1e-3 for i in range(len(edges) - 1)))
    return edges


# Property 1: Output length preservation
@given(st.data())
@settings(max_examples=200)
def test_pandas_cut_output_length_preservation(data):
    x = data.draw(input_arrays)
    use_int_bins = data.draw(st.booleans())
    if use_int_bins:
        bins = data.draw(st.integers(min_value=1, max_value=10))
        # integer bins require at least some spread / non-NaN values
        finite = [v for v in x if not math.isnan(v)]
        assume(len(finite) > 0)
        assume(len(set(finite)) > 1 or bins == 1)
    else:
        bins = _increasing_bins(data)
    labels_false = data.draw(st.booleans())
    try:
        out = pd.cut(np.array(x, dtype=float), bins,
                     labels=False if labels_false else None)
    except ValueError:
        assume(False)
    assert len(out) == len(x)


# Property 2: NA preservation and out-of-bounds handling
@given(st.data())
@settings(max_examples=200)
def test_pandas_cut_na_preservation(data):
    bins = _increasing_bins(data)
    lo, hi = bins[0], bins[-1]
    x = data.draw(input_arrays)
    arr = np.array(x, dtype=float)
    try:
        out = pd.cut(arr, bins)
    except ValueError:
        assume(False)
    # Build mask of values that should be NA in the output
    for i, v in enumerate(arr):
        if math.isnan(v):
            assert pd.isna(out[i]), f"NaN input not NA at {i}"
        elif v < lo or v > hi:
            assert pd.isna(out[i]), f"out-of-bounds {v} not NA at {i}"
        elif v == lo:
            # left edge excluded by default (right=True, include_lowest=False)
            assert pd.isna(out[i]), f"left edge {v} should be NA at {i}"


# Property 3: Bin count consistency
@given(st.data())
@settings(max_examples=200)
def test_pandas_cut_bin_count_consistency(data):
    finite = data.draw(st.lists(finite_floats, min_size=2, max_size=50))
    assume(len(set(finite)) > 1)  # need spread for integer bins
    n = data.draw(st.integers(min_value=1, max_value=8))
    arr = np.array(finite, dtype=float)
    try:
        out = pd.cut(arr, n)
    except ValueError:
        assume(False)
    # When bins is an int with duplicates='raise', number of categories == n
    assert len(out.categories) == n

    # When labels are provided, number of categories == number of bins
    labels = [f"L{i}" for i in range(n)]
    try:
        out2 = pd.cut(arr, n, labels=labels)
    except ValueError:
        assume(False)
    assert len(out2.categories) == n


# Property 4: Correct interval assignment respecting right / include_lowest
@given(st.data())
@settings(max_examples=300)
def test_pandas_cut_correct_interval_assignment(data):
    bins = _increasing_bins(data)
    right = data.draw(st.booleans())
    include_lowest = data.draw(st.booleans())
    x = data.draw(st.lists(finite_floats, min_size=1, max_size=50))
    arr = np.array(x, dtype=float)
    try:
        out = pd.cut(arr, bins, right=right, include_lowest=include_lowest)
        codes = pd.cut(arr, bins, right=right, include_lowest=include_lowest,
                       labels=False)
    except ValueError:
        assume(False)

    for i, v in enumerate(arr):
        interval = out[i]
        if pd.isna(interval):
            # codes should be -1 (NaN -> represented as nan in the float code array)
            assert pd.isna(codes[i]) or codes[i] == -1
            continue
        # value must lie within the assigned interval
        assert v in interval, f"value {v} not in interval {interval}"
        # integer code must be non-negative
        assert codes[i] >= 0
        # code must match the categorical position of the interval
        assert out.categories[int(codes[i])] == interval


# Property 5: retbins consistency and monotonicity
@given(st.data())
@settings(max_examples=200)
def test_pandas_cut_retbins_consistency(data):
    use_int_bins = data.draw(st.booleans())
    finite = data.draw(st.lists(finite_floats, min_size=2, max_size=50))
    assume(len(set(finite)) > 1)
    arr = np.array(finite, dtype=float)

    if use_int_bins:
        n = data.draw(st.integers(min_value=1, max_value=8))
        try:
            out, ret = pd.cut(arr, n, retbins=True)
        except ValueError:
            assume(False)
    else:
        bins = _increasing_bins(data)
        try:
            out, ret = pd.cut(arr, bins, retbins=True)
        except ValueError:
            assume(False)

    ret = np.asarray(ret, dtype=float)
    # strictly increasing edges
    assert np.all(np.diff(ret) > 0), f"bins not strictly increasing: {ret}"
    # number of edges == number of bins + 1
    assert len(ret) == len(out.categories) + 1
# End program