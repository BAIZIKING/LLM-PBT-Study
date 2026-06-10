from hypothesis import given, strategies as st, assume, settings
import pandas as pd
import numpy as np
import math


# Safe finite floats to avoid overflow in bin-edge arithmetic
safe_floats = st.floats(
    min_value=-1e9,
    max_value=1e9,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)

# Input arrays that may include NaN
input_values = st.lists(
    st.one_of(safe_floats, st.just(float("nan"))),
    min_size=1,
    max_size=50,
)


@st.composite
def increasing_bins(draw):
    """Strictly increasing bin edges (distinct, well-separated)."""
    edges = draw(st.lists(safe_floats, min_size=2, max_size=8, unique=True))
    edges = sorted(edges)
    # Ensure edges are sufficiently separated so interval arithmetic is stable
    for i in range(len(edges) - 1):
        assume(edges[i + 1] - edges[i] > 1e-3)
    return edges


@given(st.data())
@settings(max_examples=300)
def test_pandas_cut_property():
    pass


# ---------------------------------------------------------------------------
# Property 1: Output length preservation
# ---------------------------------------------------------------------------
@given(data=st.data())
@settings(max_examples=300)
def test_length_preservation(data):
    x = data.draw(input_values)
    use_int_bins = data.draw(st.booleans())
    labels_false = data.draw(st.booleans())

    if use_int_bins:
        non_nan = [v for v in x if not math.isnan(v)]
        assume(len(set(non_nan)) >= 1)
        bins = data.draw(st.integers(min_value=1, max_value=10))
    else:
        bins = data.draw(increasing_bins())

    try:
        result = pd.cut(
            np.array(x, dtype=float),
            bins,
            labels=False if labels_false else None,
        )
    except ValueError:
        assume(False)
        return

    assert len(result) == len(x)


# ---------------------------------------------------------------------------
# Property 2: NA handling — NaN and out-of-bounds become NA
# ---------------------------------------------------------------------------
@given(data=st.data())
@settings(max_examples=300)
def test_na_handling(data):
    x = data.draw(input_values)
    bins = data.draw(increasing_bins())

    arr = np.array(x, dtype=float)
    try:
        result = pd.cut(arr, bins)
    except ValueError:
        assume(False)
        return

    lo, hi = bins[0], bins[-1]
    # default right=True, include_lowest=False -> covers (lo, hi]
    for i, v in enumerate(arr):
        is_na = pd.isna(result[i])
        if math.isnan(v):
            assert is_na, f"NaN input at {i} should map to NA"
        elif v <= lo or v > hi:
            # out of bounds for (lo, hi]
            assert is_na, f"Out-of-bounds value {v} should map to NA"


# ---------------------------------------------------------------------------
# Property 3: Bin count correctness
# ---------------------------------------------------------------------------
@given(data=st.data())
@settings(max_examples=300)
def test_bin_count(data):
    x = data.draw(input_values)
    n_bins = data.draw(st.integers(min_value=1, max_value=8))

    non_nan = [v for v in x if not math.isnan(v)]
    assume(len(set(non_nan)) >= 1)

    try:
        result = pd.cut(np.array(x, dtype=float), n_bins)
    except ValueError:
        assume(False)
        return

    # result is a Categorical; number of categories should equal n_bins
    assert len(result.categories) == n_bins


# ---------------------------------------------------------------------------
# Property 4: Membership consistency
# ---------------------------------------------------------------------------
@given(data=st.data())
@settings(max_examples=300)
def test_membership_consistency(data):
    x = data.draw(input_values)
    bins = data.draw(increasing_bins())
    right = data.draw(st.booleans())
    include_lowest = data.draw(st.booleans())

    arr = np.array(x, dtype=float)
    try:
        result = pd.cut(
            arr, bins, right=right, include_lowest=include_lowest
        )
    except ValueError:
        assume(False)
        return

    for i, v in enumerate(arr):
        interval = result[i]
        if pd.isna(interval):
            continue
        # The assigned interval must contain the value
        assert v in interval, (
            f"Value {v} not contained in assigned interval {interval}"
        )


# ---------------------------------------------------------------------------
# Property 5: Output type correspondence
# ---------------------------------------------------------------------------
@given(data=st.data())
@settings(max_examples=300)
def test_output_type(data):
    x = data.draw(input_values)
    bins = data.draw(increasing_bins())
    labels_false = data.draw(st.booleans())
    use_series = data.draw(st.booleans())

    arr = np.array(x, dtype=float)
    inp = pd.Series(arr) if use_series else arr

    try:
        result = pd.cut(
            inp, bins, labels=False if labels_false else None
        )
    except ValueError:
        assume(False)
        return

    if use_series:
        # Series input -> Series output
        assert isinstance(result, pd.Series)
    else:
        if labels_false:
            # ndarray of integer indicators
            assert isinstance(result, np.ndarray)
            assert np.issubdtype(result.dtype, np.integer) or np.issubdtype(
                result.dtype, np.floating
            )  # floats appear when NaN present
        else:
            assert isinstance(result, pd.Categorical)
            # default labels -> Interval dtype categories
            assert isinstance(result.dtype, pd.CategoricalDtype)
            assert result.categories.dtype.name.startswith("interval")
# End program