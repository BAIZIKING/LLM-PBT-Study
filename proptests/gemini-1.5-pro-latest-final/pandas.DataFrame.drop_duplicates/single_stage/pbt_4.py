from hypothesis import given, strategies as st
import pandas as pd

# Summary: Generates diverse DataFrames and parameter combinations
@given(st.data())
def test_pandas_DataFrame_drop_duplicates(data):
    # DataFrame Generation
    num_rows = data.draw(st.integers(min_value=1, max_value=100))
    num_cols = data.draw(st.integers(min_value=1, max_value=10))
    df = pd.DataFrame(
        data.draw(
            st.lists(
                st.lists(
                    st.one_of(
                        st.integers(), st.floats(allow_nan=True), st.text()
                    ),
                    min_size=num_cols,
                    max_size=num_cols,
                ),
                min_size=num_rows,
                max_size=num_rows,
            )
        )
    )

    # Parameter Values
    subset = data.draw(st.lists(st.integers(min_value=0, max_value=num_cols - 1)))
    keep = data.draw(st.sampled_from(['first', 'last', False]))
    inplace = data.draw(st.booleans())
    ignore_index = data.draw(st.booleans())

    # Apply drop_duplicates and store original DataFrame for comparison
    original_df = df.copy()
    result_df = df.drop_duplicates(subset, keep=keep, inplace=inplace, ignore_index=ignore_index)

    # Check properties
    if not inplace:
        assert df.equals(original_df)  # Original DataFrame unchanged
        df = result_df  # Use the returned DataFrame for further checks

    assert len(df) <= len(original_df)  # Number of rows should not increase
    assert df[subset].duplicated().sum() == 0  # No duplicates in the subset
    
    if keep == 'first':
        # Check if remaining rows match the first occurrence
        for _, row in df.iterrows():
            original_row = original_df[original_df[subset].equals(row[subset])].iloc[0]
            assert row.equals(original_row) 
    elif keep == 'last':
        # Check if remaining rows match the last occurrence
        for _, row in df.iterrows():
            original_row = original_df[original_df[subset].equals(row[subset])].iloc[-1]
            assert row.equals(original_row)
    
    if ignore_index:
        assert df.index.equals(pd.RangeIndex(len(df)))  # New index from 0
    else:
        # Check if remaining indices match the original
        for index, row in df.iterrows():
            original_row = original_df[original_df[subset].equals(row[subset])].iloc[0]
            assert index == original_row.name

# End program