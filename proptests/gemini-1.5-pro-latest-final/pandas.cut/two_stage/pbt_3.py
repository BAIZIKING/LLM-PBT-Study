from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Define strategies for inputs
x_st = st.lists(st.floats(allow_nan=True, allow_infinity=False), min_size=1)
bins_st = st.one_of(
    st.integers(min_value=2),
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, unique=True),
    st.builds(pd.IntervalIndex.from_tuples, st.tuples(st.floats(), st.floats()))
)
labels_st = st.one_of(st.none(), st.booleans(), st.lists(st.text()))
ordered_st = st.booleans()

# Property 1: Output dtype
@given(x_st, bins_st, labels_st, ordered_st)
def test_pandas_cut_dtype(x, bins, labels, ordered):
    result = pd.cut(x, bins, labels=labels, ordered=ordered)
    if labels is False:
        assert result.dtype == np.dtype('int64')
    else:
        assert pd.api.types.is_categorical_dtype(result)

# Property 2: Number of elements
@given(x_st, bins_st)
def test_pandas_cut_length(x, bins):
    result = pd.cut(x, bins)
    assert len(result) == len(x)

# Property 3: NaN values
@given(x_st, bins_st)
def test_pandas_cut_nan(x, bins):
    result = pd.cut(x, bins)
    nan_mask = np.isnan(x)
    assert np.all(pd.isna(result[nan_mask]))

# Property 4: Out-of-bounds values
@given(x_st, bins_st)
def test_pandas_cut_out_of_bounds(x, bins):
    if isinstance(bins, int):
        # For int bins, we need to calculate the actual bin edges
        bins = pd.cut(x, bins, retbins=True)[1]
    lower_bound, upper_bound = bins[0], bins[-1]
    out_of_bounds_mask = (x < lower_bound) | (x > upper_bound)
    result = pd.cut(x, bins)
    assert np.all(pd.isna(result[out_of_bounds_mask]))

# Property 5: Bin ordering
@given(x_st, bins_st, st.lists(st.text()), ordered_st)
def test_pandas_cut_ordering(x, bins, labels, ordered):
    if ordered and labels:
        result = pd.cut(x, bins, labels=labels, ordered=ordered)
        assert result.cat.ordered

# End program