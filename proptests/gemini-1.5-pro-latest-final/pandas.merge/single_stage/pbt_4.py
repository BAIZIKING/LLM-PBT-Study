from hypothesis import given, strategies as st
import pandas as pd

# Summary: The generation strategy aims to create a diverse range of inputs for pandas.merge, encompassing various data frame structures, join types, and edge cases. 
# It leverages Hypothesis strategies to generate random data frames, column names, and merge parameters. 

@given(
    # Generate DataFrames with varying shapes and column types
    left_df=st.data_frames(
        columns=[
            st.column("column1", elements=st.integers()),
            st.column("column2", elements=st.floats()),
            st.column("column3", elements=st.text())
        ],
        rows=st.integers(min_value=1, max_value=10)  # Varying number of rows
    ),
    right_df=st.data_frames(
        columns=[
            st.column("column4", elements=st.integers()),
            st.column("column5", elements=st.floats()),
            st.column("column3", elements=st.text())  # Potential overlapping column
        ],
        rows=st.integers(min_value=1, max_value=10)
    ),
    how=st.sampled_from(["inner", "outer", "left", "right", "cross"]),  # Different join types
    on=st.one_of(st.none(), st.sampled_from(["column3"])),  # Test merging on a specific column or not
    left_index=st.booleans(),
    right_index=st.booleans(),
    suffixes=st.tuples(st.text(), st.text())  # Generate suffixes for overlapping columns
)
def test_pandas_merge(left_df, right_df, how, on, left_index, right_index, suffixes):
    # --- Property Checks ---
    # 1. Check DataFrame Shapes: The resulting DataFrame's shape should align with the chosen join type and the input DataFrames' dimensions.
    result_df = pd.merge(left_df, right_df, how=how, on=on, left_index=left_index, right_index=right_index, suffixes=suffixes)
    if how == "inner":
        assert result_df.shape[0] <= min(left_df.shape[0], right_df.shape[0])
    elif how == "outer":
        assert result_df.shape[0] >= max(left_df.shape[0], right_df.shape[0])

    # 2. Check for Correct Joining: The merged DataFrame should contain the expected columns based on the join type and specified columns/indexes.
    expected_columns = set(left_df.columns) | set(right_df.columns)
    if on is not None:
        expected_columns.remove(on)
    assert set(result_df.columns) == expected_columns

    # 3. Check for Suffixes: If suffixes are provided, overlapping columns should have the correct suffixes applied.
    if suffixes != (None, None):
        for col in left_df.columns:
            if col in right_df.columns:
                assert col + suffixes[0] in result_df.columns
                assert col + suffixes[1] in result_df.columns

# End program