from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Generate a wide variety of Dataframes to test sort_values:
# - Varying number of rows (0 to 100) 
# - Varying number of columns (1 to 10)
# - Column dtypes include int, float, str, and datetime  
# - Include NaN values
# - Ascending and descending sort order
# - Various sort algorithms
# - First and last NA position
@given(
    data=st.data(), 
    num_rows=st.integers(min_value=0, max_value=100),
    ascending=st.booleans(),
    na_position=st.sampled_from(['first', 'last']),
    sort_algorithm=st.sampled_from(['quicksort', 'mergesort', 'heapsort']),
    ignore_index=st.booleans()
)
def test_dataframe_sort_values(data, num_rows, ascending, na_position, sort_algorithm, ignore_index):
    
    # Generate DataFrame with random data
    num_cols = data.draw(st.integers(min_value=1, max_value=10))
    col_names = [f'col{i}' for i in range(num_cols)] 
    df = pd.DataFrame(columns=col_names, index=range(num_rows))
    
    for col in col_names:
        dtype = data.draw(st.sampled_from([int, float, str, 'datetime64[ns]']))
        if dtype == 'datetime64[ns]':
            val = st.dates(min_value=pd.Timestamp('1900-01-01'))
        elif dtype is int:
            val = st.integers()  
        elif dtype is float:
            val = st.floats(allow_nan=True)
        else:
            val = st.text()
        df[col] = data.draw(st.lists(val, min_size=num_rows, max_size=num_rows))

    # Sort
    sorted_df = df.sort_values(by=col_names, ascending=ascending, na_position=na_position, 
                               ignore_index=ignore_index, kind=sort_algorithm)
     
    # Assert properties
    if not df.empty:
        # Check sorted values are in correct order
        for col in col_names:
            assert sorted_df[col].is_monotonic_increasing == ascending
        
        # Check NaNs are in correct position
        if na_position == 'first':
            assert sorted_df.head().isnull().any(axis=None)
        else:
            assert sorted_df.tail().isnull().any(axis=None)
    
    # Check index is default range if ignore_index=True
    if ignore_index:
        assert list(sorted_df.index) == list(range(len(sorted_df)))
        
    # Check length and column names are preserved
    assert len(sorted_df) == len(df)
    assert list(sorted_df.columns) == list(df.columns)
        
# End program