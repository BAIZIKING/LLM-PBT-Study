from hypothesis import given, strategies as st
import pandas as pd

# Summary: Generate a variety of valid inputs for pandas.merge:
#  - Generate 2 dataframes with some overlapping and some distinct column names 
#  - Randomly select how, on, left_on, right_on parameters
#  - Randomly generate suffixes
#  - Randomly set left_index and right_index bools
#  - Randomly set sort bool 
#  - Check that merged dataframe has expected shape
#  - Check that common columns are merged as expected 
#  - Check that non-overlapping columns are preserved from left and right  
#  - Check that left_index and right_index are respected if set
#  - Check suffixes are applied properly

@given(
    left_df=st.data(),
    right_df=st.data(),
    how=st.sampled_from(['left','right','inner','outer']),
    left_on=st.one_of(st.none(),st.lists(st.sampled_from(['A','B','C','D']),min_size=1)), 
    right_on=st.one_of(st.none(),st.lists(st.sampled_from(['A','B','E','F']),min_size=1)),
    left_index=st.booleans(),
    right_index=st.booleans(),
    sort=st.booleans(),
    suffixes=st.lists(st.one_of(st.none(),st.text()),min_size=2,max_size=2)
)
def test_pandas_merge(left_df, right_df, how, left_on, right_on, left_index, right_index, sort, suffixes):

    left_df = left_df.draw(st.data_frames(columns=st.sampled_from(['A','B','C','D'])))
    right_df = right_df.draw(st.data_frames(columns=st.sampled_from(['A','B','E','F'])))
    
    merged = pd.merge(
        left_df, right_df, how=how, left_on=left_on, right_on=right_on, 
        left_index=left_index, right_index=right_index, sort=sort, suffixes=suffixes
    )
    
    common_cols = list(set(left_df.columns) & set(right_df.columns))
    
    # Expected number of rows depends on merge type
    if how == 'inner':
        assert len(merged) <= min(len(left_df), len(right_df))
    elif how == 'left':
        assert len(merged) == len(left_df)
    elif how == 'right':  
        assert len(merged) == len(right_df)
    elif how == 'outer':
        assert len(merged) >= max(len(left_df), len(right_df))
        
    # Overlapping columns should be merged  
    for col in common_cols:
        assert col in merged.columns
        
    # Non-overlap columns 
    for col in set(left_df.columns)-set(common_cols):
        assert col in merged.columns or (col+'_'+suffixes[0]) in merged.columns
    for col in set(right_df.columns)-set(common_cols):  
        assert col in merged.columns or (col+'_'+suffixes[1]) in merged.columns
        
    if left_index:
        assert left_df.index.equals(merged.index) 
    if right_index:
        assert right_df.index.equals(merged.index)

# End program        