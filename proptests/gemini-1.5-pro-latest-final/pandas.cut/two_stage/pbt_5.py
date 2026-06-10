from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Define strategies for generating input data
x_strategy = st.lists(st.floats(allow_nan=True, allow_infinity=False))
bins_strategy = st.one_of(
    st.integers(min_value=2),  # Number of bins
    st.lists(st.floats(allow_nan=False, allow_infinity=False)),  # Custom bin edges
    st.builds(pd.IntervalIndex.from_tuples, st.lists(st.tuples(st.floats(), st.floats())))
    # IntervalIndex
)
labels_strategy = st.one_of(
    st.none(),
    st.booleans(),
    st.lists(st.text())
)
right_strategy = st.booleans()
ordered_strategy = st.booleans()

# Property 1: Output dtype
@given(x_strategy, bins_strategy, labels_strategy, right_strategy, ordered_strategy)
def test_pandas_cut_output_dtype(x, bins, labels, right, ordered):
    result = pd.cut(x, bins, labels=labels, right=right, ordered=ordered)
    assert isinstance(result, (pd.Categorical, pd.Series, np.ndarray))

# Property 2: Length Preservation
@given(x_strategy, bins_strategy, labels_strategy, right_strategy, ordered_strategy)
def test_pandas_cut_length_preservation(x, bins, labels, right, ordered):
    result = pd.cut(x, bins, labels=labels, right=right, ordered=ordered)
    assert len(result) == len(x)

# Property 3: Bin Membership
@given(x_strategy, bins_strategy, labels_strategy, right_strategy, ordered_strategy)
def test_pandas_cut_bin_membership(x, bins, labels, right, ordered):
    result = pd.cut(x, bins, labels=labels, right=right, ordered=ordered)
    if isinstance(bins, (int, list)):
        bin_intervals = pd.cut(x, bins, retbins=True)[1]
        for i, val in enumerate(x):
            if pd.isna(val):
                assert pd.isna(result[i])
            else:
                assert val in bin_intervals[result[i]]
    elif isinstance(bins, pd.IntervalIndex):
        for i, val in enumerate(x):
            if pd.isna(val):
                assert pd.isna(result[i])
            else:
                assert val in result[i]

# Property 4: Ordering
@given(x_strategy, bins_strategy, st.lists(st.text()), right_strategy, st.just(True))
def test_pandas_cut_ordering(x, bins, labels, right, ordered):
    result = pd.cut(x, bins, labels=labels, right=right, ordered=ordered)
    assert result.cat.ordered

# Property 5: NaN Handling 
@given(x_strategy, bins_strategy, labels_strategy, right_strategy, ordered_strategy)
def test_pandas_cut_nan_handling(x, bins, labels, right, ordered):
    result = pd.cut(x, bins, labels=labels, right=right, ordered=ordered)
    for i, val in enumerate(x):
        if pd.isna(val):
            assert pd.isna(result[i])
# End program