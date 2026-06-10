from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Define strategies for input data
x_strategy = st.lists(st.floats(allow_nan=True, allow_infinity=False), min_size=1)
bins_strategy = st.one_of(
    st.integers(min_value=2),  # Number of bins
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, unique=True),  # Custom bin edges
    st.builds(pd.IntervalIndex.from_tuples, st.tuples(st.floats(allow_nan=False), st.floats(allow_nan=False)))  # IntervalIndex
)
labels_strategy = st.one_of(
    st.none(),
    st.booleans(),
    st.lists(st.text(), min_size=1)
)
right_strategy = st.booleans()
ordered_strategy = st.booleans()

@given(x=x_strategy, bins=bins_strategy, labels=labels_strategy, right=right_strategy, ordered=ordered_strategy)
def test_pandas_cut_properties(x, bins, labels, right, ordered):
    # Generate input data
    x = pd.Series(x)

    # Apply pandas.cut
    result = pd.cut(x, bins, labels=labels, right=right, ordered=ordered)

    # Test properties
    
    # 1. Output dtype
    if labels is None:
        assert pd.api.types.is_categorical_dtype(result)
    elif labels is False:
        assert isinstance(result, np.ndarray) and result.dtype == np.int
    else:
        assert pd.api.types.is_categorical_dtype(result) and result.dtype.categories.dtype == type(labels[0])

    # 2. Length Consistency
    assert len(result) == len(x)

    # 3. Bin Membership (applicable when bins are numerical)
    if isinstance(bins, (int, list)):
        bin_edges = pd.cut(x, bins, retbins=True)[1]
        for i, value in enumerate(x):
            if pd.notna(value):
                assert bin_edges[result[i].left] <= value < bin_edges[result[i].right]

    # 4. NaN Handling
    assert result.isna().sum() == x.isna().sum() + sum(pd.isnull(pd.cut([v], bins, right=right)) for v in x)

    # 5. Ordering
    if ordered:
        assert result.cat.ordered
    else:
        assert not result.cat.ordered
# End program