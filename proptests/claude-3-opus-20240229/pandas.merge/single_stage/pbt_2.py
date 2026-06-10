from hypothesis import given, strategies as st
import pandas as pd

# Summary: 
# - Generate two DataFrames df1 and df2 with random data
# - Randomly choose subset of columns to join on between df1 and df2
# - Generate random values for other params like how, left_on, right_on, etc.
# - Call merge() and validate properties of the output DataFrame
@given(st.data())
def test_pandas_merge(data):
    # Generate random DataFrames
    df1 = data.draw(st.data_frames(index=st.range_indexes(min_size=0, max_size=100)))
    df2 = data.draw(st.data_frames(index=st.range_indexes(min_size=0, max_size=100)))

    # Select subset of columns to join on
    join_on = list(data.draw(st.sets(st.sampled_from(set(df1.columns) & set(df2.columns)), 
                                     min_size=0, max_size=min(len(df1.columns), len(df2.columns)))))
    
    # Generate random values for other merge params
    how = data.draw(st.sampled_from(['left', 'right', 'outer', 'inner']))
    left_on = join_on if join_on else None 
    right_on = join_on if join_on else None
    
    # Perform merge
    merged = pd.merge(df1, df2, how=how, on=join_on, left_on=left_on, right_on=right_on)
    
    # Check properties
    # 1. Index of merged should be unique 
    assert merged.index.is_unique
    
    # 2. Number of rows in merged <= sum of rows in df1 and df2
    assert len(merged) <= len(df1) + len(df2)
    
    # 3. Columns in merged should be union of df1 and df2 columns (+suffixes)
    assert set(merged.columns) == set(df1.columns) | set(df2.columns)
    
    # 4. Join keys from df1 and df2 should be present in merged
    for col in join_on:
        assert col in merged.columns
        
    # 5. No missing values introduced in merged 
    before_na = df1[join_on].isna().sum().sum() + df2[join_on].isna().sum().sum()
    assert merged[join_on].isna().sum().sum() == before_na
# End program