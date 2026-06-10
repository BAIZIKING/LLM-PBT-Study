from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Define strategies for generating test data
x_strategy = st.lists(st.floats(allow_nan=True, allow_infinity=False), min_size=1)
bins_strategy = st.one_of(
    st.integers(min_value=2),  # Number of bins
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, unique=True)  # Custom bin edges
)
labels_strategy = st.one_of(
    st.none(),
    st.booleans(),
    st.lists(st.text(), min_size=2)
)
ordered_strategy = st.booleans()

@given(x_strategy, bins_strategy, labels_strategy, ordered_strategy)
def test_pandas_cut_output_dtype(x, bins, labels, ordered):
    """Test that the output dtype is either category or ndarray."""
    result = pd.cut(x, bins, labels=labels, ordered=ordered)
    assert isinstance(result, (pd.Series, pd.Categorical, np.ndarray))

@given(x_strategy, bins_strategy, labels_strategy, ordered_strategy)
def test_pandas_cut_length(x, bins, labels, ordered):
    """Test that the output has the same length as the input."""
    result = pd.cut(x, bins, labels=labels, ordered=ordered)
    assert len(result) == len(x)

@given(x_strategy, bins_strategy, labels_strategy, ordered_strategy)
def test_pandas_cut_bin_membership(x, bins, labels, ordered):
    """Test that each element belongs to a bin or is NaN."""
    result = pd.cut(x, bins, labels=labels, ordered=ordered)
    for i, value in enumerate(result):
        if pd.isna(value):
            assert pd.isna(x[i]) or all(x[i] < b for b in bins) or all(x[i] > b for b in bins)
        else:
            assert value in result.cat.categories 

@given(x_strategy, bins_strategy, labels_strategy, st.booleans())
def test_pandas_cut_ordering(x, bins, labels, ordered):
    """Test that the categories are ordered correctly."""
    result = pd.cut(x, bins, labels=labels, ordered=ordered)
    if ordered and not pd.isna(labels):
        assert result.cat.ordered

@given(x_strategy, bins_strategy, st.lists(st.text(), min_size=2), st.booleans())
def test_pandas_cut_label_uniqueness(x, bins, labels, ordered):
    """Test that labels are unique when ordered=True."""
    result = pd.cut(x, bins, labels=labels, ordered=ordered)
    if ordered:
        assert result.cat.categories.is_unique
# End program