from hypothesis import given, strategies as st
import pandas as pd

# Define strategies for generating DataFrames with controlled size and values
df_strategy = st.dataframes(
    columns=[
        st.column('key', elements=st.integers(min_value=1, max_value=100)),
        st.column('value', elements=st.floats(allow_nan=False))
    ],
    rows=st.integers(min_value=1, max_value=100)
)

merge_types = st.sampled_from(['inner', 'outer', 'left', 'right'])
suffixes_strategy = st.tuples(st.one_of(st.none(), st.text()), st.one_of(st.none(), st.text()))

@given(left_df=df_strategy, right_df=df_strategy, how=merge_types, suffixes=suffixes_strategy)
def test_column_presence(left_df, right_df, how, suffixes):
    merged_df = pd.merge(left_df, right_df, how=how, on='key', suffixes=suffixes)
    left_cols = set(left_df.columns)
    right_cols = set(right_df.columns)
    merged_cols = set(merged_df.columns)

    # Check if all columns from left and right DataFrames are present in merged DataFrame
    # Accounting for potential suffix modifications
    for col in left_cols:
        assert col in merged_cols or f"{col}{suffixes[0]}" in merged_cols
    for col in right_cols:
        assert col in merged_cols or f"{col}{suffixes[1]}" in merged_cols


@given(left_df=df_strategy, right_df=df_strategy, how=merge_types)
def test_row_count_within_bounds(left_df, right_df, how):
    merged_df = pd.merge(left_df, right_df, how=how, on='key')

    # Check if row count in merged DataFrame is within expected bounds based on merge type
    if how == 'inner':
        assert len(merged_df) <= min(len(left_df), len(right_df))
    elif how in ['outer', 'left', 'right']:
        assert len(merged_df) <= len(left_df) + len(right_df)
    

@given(left_df=df_strategy, right_df=df_strategy)
def test_index_preservation_on_index_merge(left_df, right_df):
    merged_df = pd.merge(left_df, right_df, left_index=True, right_index=True)

    # Check if merged DataFrame's index matches the left DataFrame's index (assuming both indexes are unique)
    pd.testing.assert_index_equal(merged_df.index, left_df.index)


@given(left_df=df_strategy, right_df=df_strategy, how=merge_types)
def test_data_preservation(left_df, right_df, how):
    merged_df = pd.merge(left_df, right_df, how=how, on='key')

    # Check if values in merged DataFrame match the original DataFrames for corresponding keys and columns
    for key, left_row in left_df.iterrows():
        for right_row in right_df.loc[right_df['key'] == key].itertuples():
            merged_row = merged_df.loc[(merged_df['key_x'] == key) & (merged_df['key_y'] == key)]
            for col in set(left_df.columns).union(right_df.columns) - {'key'}:
                assert merged_row[f'{col}_x'].equals(left_row[col])
                assert merged_row[f'{col}_y'].equals(getattr(right_row, col))


@given(left_df=df_strategy, right_df=df_strategy, how=merge_types)
def test_key_consistency(left_df, right_df, how):
    merged_df = pd.merge(left_df, right_df, how=how, on='key')

    # Check if rows with the same key are grouped together in the merged DataFrame
    for key in merged_df['key_x'].unique():
        assert merged_df.loc[merged_df['key_x'] == key]['key_y'].nunique() == 1
# End program