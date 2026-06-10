from hypothesis import given, strategies as st
import pandas as pd

# Generation strategy: 
# - Generate 2 DataFrames with random data
#   - Number of rows between 0 and 10 
#   - Number of columns between 1 and 5
#   - Column names are strings
#   - Cell values are integers, floats or strings
# - Randomly select a subset of column names to use as join keys 
# - Randomly select a join type from 'left', 'right', 'inner', 'outer'
# - Randomly generate suffixes
#
# Properties to test:
# - Output is a DataFrame
# - Number of rows in output is no more than cartesian product of rows in input
# - Number of columns in output is no more than sum of columns in inputs  
# - Join keys from `on` parameter exist in output DataFrame
# - Columns in output have suffixes appended
# - Row counts are as expected for the join type

@given(st.data())
def test_merge(data):
    
    # Generate input DataFrames
    left_df = data.draw(st.data_frames(
        rows=st.integers(0, 10), 
        columns=st.integers(1, 5),
        column_names=st.text(min_size=1)))

    right_df = data.draw(st.data_frames(
        rows=st.integers(0, 10),  
        columns=st.integers(1, 5),
        column_names=st.text(min_size=1)))
    
    # Select join keys
    join_keys = data.draw(st.lists(st.sampled_from(left_df.columns & right_df.columns), 
                                   unique=True,
                                   min_size=1))

    # Select join type  
    how = data.draw(st.sampled_from(['left','right','inner','outer']))
    
    # Generate suffixes
    lsuffix = data.draw(st.text())
    rsuffix = data.draw(st.text())

    # Call function
    merged = pd.merge(left_df, right_df, how=how, on=join_keys, 
                      suffixes=(lsuffix, rsuffix))

    # Assert properties
    assert isinstance(merged, pd.DataFrame)
    assert len(merged) <= len(left_df) * len(right_df) 
    assert len(merged.columns) <= len(left_df.columns) + len(right_df.columns)
    assert set(join_keys).issubset(merged.columns)
    assert lsuffix in ''.join(merged.columns) or rsuffix in ''.join(merged.columns)
    
    if how == 'inner':
        assert len(merged) <= min(len(left_df), len(right_df))
    elif how == 'left':
        assert len(merged) == len(left_df)  
    elif how == 'right':
        assert len(merged) == len(right_df)
    elif how == 'outer':
        assert len(merged) >= max(len(left_df), len(right_df))
        
# End program        