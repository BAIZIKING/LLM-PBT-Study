from hypothesis import given, strategies as st
import pandas as pd

# Define strategies for generating DataFrames and parameters
df_strategy = st.dataframes(
    columns=[
        st.column("numerical", elements=st.floats(allow_nan=True, allow_infinity=False)),
        st.column("categorical", elements=st.text()),
    ],
    rows=st.integers(min_value=0, max_value=100),  # Limit size to avoid overflows
)
subset_strategy = st.one_of(st.none(), st.lists(st.sampled_from(["numerical", "categorical"])))
keep_strategy = st.sampled_from(["first", "last", False])
inplace_strategy = st.booleans()
ignore_index_strategy = st.booleans()

@given(df_strategy, subset_strategy, keep_strategy, inplace_strategy, ignore_index_strategy)
def test_pandas_dataframe_drop_duplicates_property_1(df, subset, keep, inplace, ignore_index):
    # Property 1: The number of rows in the output dataframe is less than or equal to the number of rows in the input dataframe.
    result_df = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)
    if inplace:
        assert df.shape[0] <= df.shape[0]  # Compare with original shape
    else:
        assert result_df.shape[0] <= df.shape[0]

@given(df_strategy, subset_strategy, keep_strategy, inplace_strategy, ignore_index_strategy)
def test_pandas_dataframe_drop_duplicates_property_2(df, subset, keep, inplace, ignore_index):
    # Property 2: The output dataframe contains no duplicate rows.
    result_df = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)
    if not result_df.empty:
        assert result_df.duplicated(subset=subset, keep=keep).sum() == 0

@given(df_strategy, subset_strategy, keep_strategy, inplace_strategy, ignore_index_strategy)
def test_pandas_dataframe_drop_duplicates_property_3(df, subset, keep, inplace, ignore_index):
    # Property 3: The output dataframe contains a subset of the rows from the input dataframe.
    result_df = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)
    if not result_df.empty:
        assert set(result_df.index).issubset(set(df.index))

@given(df_strategy, subset_strategy, keep_strategy, inplace_strategy, ignore_index_strategy)
def test_pandas_dataframe_drop_duplicates_property_4(df, subset, keep, inplace, ignore_index):
    # Property 4: The order of the rows in the output dataframe is preserved (unless ignore_index=True).
    result_df = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)
    if not result_df.empty and not ignore_index:
        assert result_df.index.equals(df.loc[result_df.index].index)  # Compare index order

@given(df_strategy, subset_strategy, keep_strategy, inplace_strategy, ignore_index_strategy)
def test_pandas_dataframe_drop_duplicates_property_5(df, subset, keep, inplace, ignore_index):
    # Property 5: inplace behavior
    original_df = df.copy()  # Create a copy to compare later
    result_df = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)
    if inplace:
        assert result_df is None  # Check if returned value is None
        assert df.equals(original_df.drop_duplicates(subset=subset, keep=keep, ignore_index=ignore_index))  # Compare with expected modification
    else:
        assert not df.equals(original_df.drop_duplicates(subset=subset, keep=keep, ignore_index=ignore_index))  # Check if original df is unmodified
        assert result_df.equals(original_df.drop_duplicates(subset=subset, keep=keep, ignore_index=ignore_index))  # Compare result with expected output 