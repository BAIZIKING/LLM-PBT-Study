from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: Generate DataFrames with various data types (integer, float, string, boolean, datetime).
# Include missing values to test the na_position parameter. Vary number of rows and columns.  
# Use hypothesis' recursive strategy to generate nested lists for the `by` parameter to test
# multi-level sorting. Check that the result is sorted (ascending and descending), NaNs are 
# positioned properly, and the function handles empty DataFrames.
@given(
    st.data(), 
    st.integers(min_value=1, max_value=10),  # num_cols
    st.integers(min_value=0, max_value=100),  # num_rows
    st.sampled_from(['quicksort', 'mergesort', 'heapsort']),  # sort algorithm
    st.sampled_from(['first', 'last']),  # na_position
    st.booleans(),  # ascending
    st.booleans(),  # ignore_index
)
def test_sort_values(data, num_cols, num_rows, sort_kind, na_position, ascending, ignore_index):
    # Generate DataFrame
    columns = [f"col{i}" for i in range(num_cols)]
    df = pd.DataFrame(columns=columns, index=range(num_rows))
    
    for col in columns:
        type_strategy = data.draw(st.sampled_from([
            st.integers(), 
            st.floats(allow_nan=True), 
            st.text(), 
            st.booleans(), 
            st.datetimes()
        ]))
        df[col] = data.draw(st.lists(type_strategy, min_size=num_rows, max_size=num_rows))

    # Generate 'by' parameter  
    by_strategy = st.one_of(
        st.sampled_from(columns), 
        st.lists(st.sampled_from(columns), min_size=1, unique=True)
    )
    by = data.draw(by_strategy)
    
    # Call function
    result = df.sort_values(by=by, axis=0, ascending=ascending, inplace=False, 
                            kind=sort_kind, na_position=na_position, ignore_index=ignore_index)

    # Check properties
    if num_rows == 0:
        assert len(result) == 0
    else:
        # Check index is reset if ignore_index=True
        if ignore_index:
            assert isinstance(result.index, pd.RangeIndex)
        else:
            assert isinstance(result.index, pd.Int64Index)

        # Check sorting
        if isinstance(by, list):
            by_array = np.array(by)
            sorter = np.lexsort([df[x] for x in by_array[::-1]])
            sorted_df = df.take(sorter)
            if not ascending:
                slice_start = num_cols - len(by) 
                sorted_df.iloc[:, slice_start:] = sorted_df.iloc[:, slice_start:].iloc[::-1]
        else:
            sorted_df = df.sort_values(by=by, ascending=ascending)
            
        pd.testing.assert_frame_equal(sorted_df, result)
                    
        # Check NA position
        for col in by:
            if ascending:
                if na_position == 'first':
                    assert result[col].isnull().values.argmax() <= result[col].fillna(method='bfill').iloc[0]
                else:
                    assert result[col].isnull().values.any() == result[col].isnull().values[-1]
            else:
                if na_position == 'first':
                    assert result[col].isnull().values.argmin() >= result[col].fillna(method='ffill').iloc[-1]
                else:
                    assert result[col].isnull().values.any() == result[col].isnull().values[0]
# End program            