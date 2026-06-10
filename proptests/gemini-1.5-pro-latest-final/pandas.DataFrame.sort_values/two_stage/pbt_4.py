from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Define strategies for DataFrame generation
def dataframe_strategy(elements=st.integers(), min_size=0, max_size=10):
    return st.data_frames(
        columns=[st.text(), st.text()],  # Allow for two columns
        rows=st.lists(elements, min_size=min_size, max_size=max_size),
    )

def sort_parameters_strategy():
    return st.tuples(
        st.sampled_from(['index', 0, 'columns', 1]),
        st.sampled_from([True, False]),
        st.sampled_from(['quicksort', 'mergesort', 'heapsort']),
        st.sampled_from(['first', 'last']),
        st.booleans(),
    )

@given(dataframe_strategy(), sort_parameters_strategy())
def test_dataframe_shape_preserved(df, sort_params):
    axis, ascending, kind, na_position, ignore_index = sort_params
    sorted_df = df.sort_values(by=df.columns, axis=axis, ascending=ascending, kind=kind, 
                                na_position=na_position, ignore_index=ignore_index)
    assert df.shape == sorted_df.shape

@given(dataframe_strategy(elements=st.text()), sort_parameters_strategy())
def test_unique_values_preserved(df, sort_params):
    axis, ascending, kind, na_position, ignore_index = sort_params
    for col in df.columns:
        original_uniques = df[col].unique()
        sorted_df = df.sort_values(by=col, axis=axis, ascending=ascending, kind=kind, 
                                    na_position=na_position, ignore_index=ignore_index)
        assert np.array_equal(original_uniques, sorted_df[col].unique())

@given(dataframe_strategy(elements=st.floats(allow_nan=True)), sort_parameters_strategy())
def test_nan_positioning(df, sort_params):
    axis, ascending, kind, na_position, ignore_index = sort_params
    sorted_df = df.sort_values(by=df.columns, axis=axis, ascending=ascending, kind=kind, 
                                na_position=na_position, ignore_index=ignore_index)
    for col in df.columns:
        if na_position == 'first':
            assert pd.isna(sorted_df[col].iloc[0])
        elif na_position == 'last' and pd.isna(df[col]).any():
            assert pd.isna(sorted_df[col].iloc[-1])

@given(dataframe_strategy(), sort_parameters_strategy())
def test_column_sorted_correctly(df, sort_params):
    axis, ascending, kind, na_position, ignore_index = sort_params
    for col in df.columns:
        sorted_df = df.sort_values(by=col, axis=axis, ascending=ascending, kind=kind, 
                                    na_position=na_position, ignore_index=ignore_index)
        if ascending:
            assert all(sorted_df[col].iloc[i] <= sorted_df[col].iloc[i+1] for i in range(len(df)-1))
        else:
            assert all(sorted_df[col].iloc[i] >= sorted_df[col].iloc[i+1] for i in range(len(df)-1))

@given(dataframe_strategy(), sort_parameters_strategy())
def test_index_reflects_sorting(df, sort_params):
    axis, ascending, kind, na_position, ignore_index = sort_params
    if not ignore_index:
        sorted_df = df.sort_values(by=df.columns, axis=axis, ascending=ascending, kind=kind, 
                                    na_position=na_position, ignore_index=ignore_index)
        assert all(sorted_df.index == df.index[sorted_df.index])
# End program