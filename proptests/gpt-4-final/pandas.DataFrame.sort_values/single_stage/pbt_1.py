from hypothesis import given, strategies as st
from hypothesis.extra.pandas import column, data_frames
import pandas as pd
import numpy as np

# Creates test data of integers, then inserts NaN values at random positions
def df_with_nans(dtype):
    return st.lists(st.integers(), min_size=10, max_size=10).map(
        lambda x: pd.Series(x, dtype=dtype)
    ).flatmap(   # now it's Series of dtype
        lambda s: st.lists(st.integers(0, len(s) - 1)).map(
            lambda idx: s.astype(object).mask(s.index.isin(idx), np.nan)
        )
    )

axis = st.sampled_from(['index', 'columns'])
ascending = st.booleans()
inplace = st.booleans()
kind = st.sampled_from(['quicksort', 'mergesort', 'heapsort', 'stable'])
na_position = st.sampled_from(['first', 'last'])
ignore_index = st.booleans()

@given(
    data_frames([
        column("A", dtype=float, elements=st.floats(allow_nan=False)),
        column("B", dtype=float, elements=st.floats(allow_nan=True))]),
    axis, ascending, inplace, kind, na_position, ignore_index
)
def test_sort_values(df, axis, ascending, inplace, kind, na_position, ignore_index):
    original_df = df.copy()
    sorted_df = df.sort_values(by='A', axis=axis, ascending=ascending, inplace=inplace,
                               kind=kind, na_position=na_position, ignore_index=ignore_index)

    if inplace:
        assert df.equals(sorted_df), "DataFrame was not sorted in-place"
    else:
        assert df.equals(original_df), "Original DataFrame was modified"

    assert sorted_df['A'].is_monotonic, "DataFrame is not sorted"
# End program