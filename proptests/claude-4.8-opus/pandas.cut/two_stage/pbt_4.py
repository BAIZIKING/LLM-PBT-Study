from hypothesis import given, strategies as st, assume
import pandas as pd
import numpy as np
import math


finite_floats = st.floats(
    min_value=-1e9,
    max_value=1e9,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)


def draw_x_array(draw, allow_nan=True, min_size=1):
    elem = st.one_of(finite_floats, st.just(float("nan"))) if allow_nan else finite_floats
    lst = draw(st.lists(elem, min_size=min_size, max_size=50))
    return np.array(lst, dtype=float)


def draw_distinct_x(draw, min_size=2):
    # values distinct enough that an integer-bin split is well-defined
    lst = draw(st.lists(finite_floats, min_size=min_size, max_size=50, unique=True))
    assume(max(lst) - min(lst) > 1e-3)
    return np.array(lst, dtype=float)


def draw_bin_edges(draw, min_bins=1, max_bins=8):
    n = draw(st.integers(min_value=min_bins, max_value=max_bins))
    vals = draw(st.lists(finite_floats, min_size=n + 1, max_size=n + 1, unique=True))
    vals = sorted(vals)
    for i in range(len(vals) - 1):
        assume(vals[i + 1] - vals[i] > 1e-3)
    return vals


# ---------------------------------------------------------------------------
# Property 1: The output length always equals the input length.
# ---------------------------------------------------------------------------
@given(st.data())
def test_pandas_cut_property_length(data):
    x = data.draw(draw_x_array(data.draw, allow_nan=True, min_size=1))
    nbins = data.draw(st.integers(min_value=1, max_value=10))
    assume(np.isfinite(x[~np.isnan(x)]).all())
    # need at least one finite value and a non-degenerate range for int bins
    finite = x[~np.isnan(x)]
    assume(len(finite) >= 1)
    assume(np.ptp(finite) > 1e-3 if len(finite) > 1 else True)
    if len(finite) == 1:
        # single distinct value: pandas can still cut; range extended by .1%
        pass
    result = pd.cut(x, nbins)
    assert len(result) == len(x)


# ---------------------------------------------------------------------------
# Property 2: For integer bins=n, number of categories == n and, with
# retbins=True, the returned bins array has length n+1.
# ---------------------------------------------------------------------------
@given(st.data())
def test_pandas_cut_property_num_bins(data):
    x = data.draw(draw_distinct_x(data.draw, min_size=2))
    nbins = data.draw(st.integers(min_value=1, max_value=10))
    cat, bins = pd.cut(x, nbins, retbins=True)
    assert len(cat.categories) == nbins
    assert len(bins) == nbins + 1


# ---------------------------------------------------------------------------
# Property 3: NA inputs and out-of-bounds values map to NaN in the output.
# ---------------------------------------------------------------------------
@given(st.data())
def test_pandas_cut_property_na_and_out_of_bounds(data):
    edges = data.draw(draw_bin_edges(data.draw, min_bins=1, max_bins=6))
    lo, hi = edges[0], edges[-1]
    # Construct inputs: some NaN, some below lo, some above hi
    x = np.array(
        [float("nan"), lo - 10.0, hi + 10.0],
        dtype=float,
    )
    result = pd.cut(x, edges, right=True, include_lowest=False)
    # Index 0 (NaN) -> NaN
    assert pd.isna(result[0])
    # Below the lowest edge -> NaN (right=True, not include_lowest)
    assert pd.isna(result[1])
    # Above the highest edge -> NaN
    assert pd.isna(result[2])


# ---------------------------------------------------------------------------
# Property 4: labels=False yields integer indicators in [0, nbins-1]
# (NaN for NA/out-of-bounds), matching the interval each value lands in.
# ---------------------------------------------------------------------------
@given(st.data())
def test_pandas_cut_property_labels_false_indices(data):
    edges = data.draw(draw_bin_edges(data.draw, min_bins=1, max_bins=6))
    nbins = len(edges) - 1
    right = data.draw(st.booleans())
    include_lowest = data.draw(st.booleans())
    x = data.draw(draw_x_array(data.draw, allow_nan=True, min_size=1))

    codes = pd.cut(
        x, edges, labels=False, right=right, include_lowest=include_lowest
    )
    codes = np.asarray(codes, dtype=float)

    for v, c in zip(x, codes):
        if math.isnan(v):
            assert math.isnan(c)
            continue
        if math.isnan(c):
            # value out of bounds; verify it is indeed outside all bins
            lo, hi = edges[0], edges[-1]
            inside = (lo < v <= hi) if right else (lo <= v < hi)
            if include_lowest and right:
                inside = lo <= v <= hi
            assert not inside
        else:
            ci = int(c)
            assert 0 <= ci <= nbins - 1
            left, rightedge = edges[ci], edges[ci + 1]
            if right:
                if include_lowest and ci == 0:
                    assert left <= v <= rightedge
                else:
                    assert left < v <= rightedge
            else:
                assert left <= v < rightedge


# ---------------------------------------------------------------------------
# Property 5: Each non-NaN value is assigned to an interval that contains it,
# respecting the `right` boundary-inclusion rule (default-label intervals).
# ---------------------------------------------------------------------------
@given(st.data())
def test_pandas_cut_property_value_in_assigned_interval(data):
    edges = data.draw(draw_bin_edges(data.draw, min_bins=1, max_bins=6))
    right = data.draw(st.booleans())
    include_lowest = data.draw(st.booleans())
    x = data.draw(draw_x_array(data.draw, allow_nan=True, min_size=1))

    result = pd.cut(
        x, edges, right=right, include_lowest=include_lowest
    )

    for v, interval in zip(x, result):
        if math.isnan(v):
            assert pd.isna(interval)
            continue
        if pd.isna(interval):
            # out of bounds value; nothing to check
            continue
        # The reported interval must actually contain v per its closedness.
        assert interval.left <= v <= interval.right
        if interval.closed == "right":
            # left-open unless it is the include_lowest first interval
            assert (v > interval.left) or math.isclose(
                v, interval.left, rel_tol=0, abs_tol=0
            ) and include_lowest
            assert v <= interval.right
        elif interval.closed == "left":
            assert v >= interval.left
            assert v < interval.right or math.isclose(v, interval.right)
# End program