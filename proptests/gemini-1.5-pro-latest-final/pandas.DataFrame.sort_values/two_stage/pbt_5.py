from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Define strategies for DataFrame generation
def df_strategy():
    # Generate DataFrames with controlled size and value range
    return st.data_frames(
        columns=st.lists(st.text(), min_size=1, max_size=5),
        rows=st.lists(
            st.one_of(
                st.floats(allow_nan=True),
                st.integers(),
                st.text()
            ),
            min_size=1, max_size=100
        ),
    )

def sort_parameters_strategy():
    # Generate sorting parameters
    return st.tuples(
        st.sampled_from(["index", 0, "columns", 1]),
        st.one_of(st.booleans(), st.lists(st.booleans(), max_size=3)),
        st.sampled_from(["quicksort", "mergesort", "heapsort"]),
        st.sampled_from(["first", "last"]),
        st.booleans()
    )

# Test 1: Sortedness
@given(df_strategy(), sort_parameters_strategy())
def test_sort_values_sortedness(df, params):
    axis, ascending, kind, na_position, ignore_index = params
    sorted_df = df.sort_values(by=df.columns, axis=axis, ascending=ascending, kind=kind, na_position=na_position, ignore_index=ignore_index)
    for col in sorted_df:
        if isinstance(sorted_df[col].dtype, pd.api.types.is_numeric_dtype):
            if ascending:
                assert np.all(sorted_df[col].is_monotonic_increasing) or np.all(pd.isna(sorted_df[col]))
            else:
                assert np.all(sorted_df[col].is_monotonic_decreasing) or np.all(pd.isna(sorted_df[col]))
        else:
            if ascending:
                assert np.all(sorted_df[col].str.lower().is_monotonic_increasing) or np.all(pd.isna(sorted_df[col]))
            else:
                assert np.all(sorted_df[col].str.lower().is_monotonic_decreasing) or np.all(pd.isna(sorted_df[col]))

# Test 2: Shape
@given(df_strategy(), sort_parameters_strategy())
def test_sort_values_shape(df, params):
    axis, ascending, kind, na_position, ignore_index = params
    sorted_df = df.sort_values(by=df.columns, axis=axis, ascending=ascending, kind=kind, na_position=na_position, ignore_index=ignore_index)
    assert df.shape == sorted_df.shape 

# Test 3: Data Preservation
@given(df_strategy(), sort_parameters_strategy())
def test_sort_values_data_preservation(df, params):
    axis, ascending, kind, na_position, ignore_index = params
    sorted_df = df.sort_values(by=df.columns, axis=axis, ascending=ascending, kind=kind, na_position=na_position, ignore_index=ignore_index)
    assert sorted_df.sort_index().equals(df.sort_index()) 

# Test 4: Index Preservation
@given(df_strategy(), sort_parameters_strategy())
def test_sort_values_index_preservation(df, params):
    axis, ascending, kind, na_position, ignore_index = params
    sorted_df = df.sort_values(by=df.columns, axis=axis, ascending=ascending, kind=kind, na_position=na_position, ignore_index=ignore_index)
    if not ignore_index:
        assert df.index.equals(sorted_df.index) 
    else:
        assert sorted_df.index.equals(pd.RangeIndex(len(df)))

# Test 5: NaN Positioning
@given(df_strategy(), sort_parameters_strategy())
def test_sort_values_nan_positioning(df, params):
    axis, ascending, kind, na_position, ignore_index = params
    sorted_df = df.sort_values(by=df.columns, axis=axis, ascending=ascending, kind=kind, na_position=na_position, ignore_index=ignore_index)
    for col in sorted_df:
        if ascending:
            if na_position == 'first':
                assert np.all(pd.isna(sorted_df[col][:sum(pd.isna(sorted_df[col]))])) 
            else:
                assert np.all(pd.isna(sorted_df[col][-sum(pd.isna(sorted_df[col])):]))
        else: 
            if na_position == 'first':
                assert np.all(pd.isna(sorted_df[col][-sum(pd.isna(sorted_df[col])):])) 
            else:
                assert np.all(pd.isna(sorted_df[col][:sum(pd.isna(sorted_df[col]))]))
# End program