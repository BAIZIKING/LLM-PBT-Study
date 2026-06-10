from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: Generate a DataFrame with various data types (int, float, str, None).
# Test sorting on different columns, ascending/descending order, and NaN positioning.
# Verify the DataFrame is properly sorted according to the specified criteria.
@given(
    data=st.data(),
    nrows=st.integers(min_value=1, max_value=100),
    ncols=st.integers(min_value=1, max_value=10), 
    ascending=st.booleans(),
    na_position=st.sampled_from(['first', 'last']),
)
def test_pandas_dataframe_sort_values(data, nrows, ncols, ascending, na_position):
    # Generate column names
    columns = [f"col{i}" for i in range(ncols)]
    
    # Generate a dictionary of column data
    data_dict = {
        col: data.draw(st.one_of(
            st.lists(st.integers(), min_size=nrows, max_size=nrows),
            st.lists(st.floats(allow_nan=True), min_size=nrows, max_size=nrows), 
            st.lists(st.text(), min_size=nrows, max_size=nrows),
            st.lists(st.none(), min_size=nrows, max_size=nrows),
        ))
        for col in columns
    }
    
    # Create the DataFrame
    df = pd.DataFrame(data_dict)
    
    # Select a random subset of columns to sort by
    by = data.draw(st.lists(st.sampled_from(columns), unique=True))
    
    # Call sort_values on the DataFrame
    sorted_df = df.sort_values(by=by, ascending=ascending, na_position=na_position)
    
    # Check that the DataFrame is properly sorted
    for col in by:
        if ascending:
            assert sorted_df[col].is_monotonic_increasing
        else:
            assert sorted_df[col].is_monotonic_decreasing
        
        if na_position == 'first':
            assert sorted_df[col].isna().iloc[0] or not sorted_df[col].hasnans
        else:
            assert sorted_df[col].notna().iloc[-1] or not sorted_df[col].hasnans
# End program            