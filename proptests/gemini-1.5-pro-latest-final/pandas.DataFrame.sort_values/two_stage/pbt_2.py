from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Define strategies for DataFrame generation
def df_strategy(max_rows=100, max_cols=10):
    # Strategies for generating column data
    int_strat = st.integers(min_value=-100, max_value=100)
    float_strat = st.floats(allow_nan=True, allow_infinity=False)
    str_strat = st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=1, max_size=10)
    
    columns = st.lists(
        st.one_of(int_strat, float_strat, str_strat), 
        min_size=1, max_size=max_cols
    )
    
    return st.data_frames(columns, min_rows=1, max_rows=max_rows)

# Define strategy for sorting parameters
@st.composite
def sort_params_strategy(draw):
    by = draw(st.sampled_from(["index", 0, "columns", 1]))
    ascending = draw(st.booleans())
    na_position = draw(st.sampled_from(["first", "last"]))
    ignore_index = draw(st.booleans())
    return by, ascending, na_position, ignore_index

@given(df_strategy(), sort_params_strategy())
def test_pandas_dataframe_sort_values_sorted_order(df, sort_params):
    by, ascending, na_position, ignore_index = sort_params
    sorted_df = df.sort_values(by=by, ascending=ascending, na_position=na_position, ignore_index=ignore_index)

    if isinstance(by, str) or (isinstance(by, list) and len(by) == 1):
        column = by if isinstance(by, str) else by[0]
        if pd.api.types.is_numeric_dtype(sorted_df[column]):
            if ascending:
                assert all(sorted_df[column].iloc[i] <= sorted_df[column].iloc[i+1] for i in range(len(sorted_df) - 1))
            else:
                assert all(sorted_df[column].iloc[i] >= sorted_df[column].iloc[i+1] for i in range(len(sorted_df) - 1))

@given(df_strategy(), sort_params_strategy())
def test_pandas_dataframe_sort_values_shape_preservation(df, sort_params):
    by, ascending, na_position, ignore_index = sort_params
    sorted_df = df.sort_values(by=by, ascending=ascending, na_position=na_position, ignore_index=ignore_index)
    assert df.shape == sorted_df.shape

@given(df_strategy(), sort_params_strategy())
def test_pandas_dataframe_sort_values_data_preservation(df, sort_params):
    by, ascending, na_position, ignore_index = sort_params
    sorted_df = df.sort_values(by=by, ascending=ascending, na_position=na_position, ignore_index=ignore_index)
    pd.testing.assert_frame_equal(df.sort_index(), sorted_df.sort_index()) 

@given(df_strategy(), sort_params_strategy())
def test_pandas_dataframe_sort_values_nan_placement(df, sort_params):
    by, ascending, na_position, ignore_index = sort_params
    sorted_df = df.sort_values(by=by, ascending=ascending, na_position=na_position, ignore_index=ignore_index)

    if isinstance(by, str) or (isinstance(by, list) and len(by) == 1):
        column = by if isinstance(by, str) else by[0]
        nan_count = sorted_df[column].isna().sum()
        if na_position == "first" and nan_count > 0:
            assert sorted_df[column].isna().all(axis=None)[:nan_count]
        elif na_position == "last" and nan_count > 0:
            assert sorted_df[column].isna().all(axis=None)[-nan_count:]

@given(df_strategy(), sort_params_strategy())
def test_pandas_dataframe_sort_values_index_preservation_or_reset(df, sort_params):
    by, ascending, na_position, ignore_index = sort_params
    sorted_df = df.sort_values(by=by, ascending=ascending, na_position=na_position, ignore_index=ignore_index)

    if ignore_index:
        assert list(sorted_df.index) == list(range(len(sorted_df)))
    else:
        pd.testing.assert_index_equal(df.index, sorted_df.index)
# End program