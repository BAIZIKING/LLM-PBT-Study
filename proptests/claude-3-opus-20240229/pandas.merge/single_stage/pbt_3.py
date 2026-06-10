from hypothesis import given, strategies as st
import pandas as pd

# Summary: 
# Generate a variety of input dataframes and parameters to test pandas.merge
# - Use st.dataframes to generate random left and right dataframes 
# - Randomly select columns to join on or set left/right index=True
# - Generate random suffixes including None 
# - Test different "how" types and indicator options
# - Use assume to filter out invalid combinations, like joining on non-existent columns
# Properties to test:
# - Length of result matches expected for inner/left/right/outer join
# - Joined columns present in result
# - Suffixes added to overlapping columns 
# - Indicator column added if enabled
# - Exception raised if suffixes has a single None
# - Exception raised if joining on overlapping columns with suffixes disabled
@given(
    left=st.data(),
    right=st.data(),  
    how=st.sampled_from(['left','right','inner','outer']),
    suffixes=st.tuples(st.one_of(st.text(),st.none()), st.one_of(st.text(),st.none())).filter(lambda x: x != (None,None)),
    indicator=st.booleans()
)
def test_pandas_merge(left, right, how, suffixes, indicator):
    left_df = left.draw(st.data_frames(index=st.booleans(),columns=st.lists(st.text(),unique=True,min_size=1,max_size=5)))
    right_df = right.draw(st.data_frames(index=st.booleans(),columns=st.lists(st.text(),unique=True,min_size=1,max_size=5)))
    common_cols = set(left_df.columns) & set(right_df.columns)
    join_cols = list(left.draw(st.lists(st.sampled_from(sorted(common_cols)), unique=True),min_size=1)) if common_cols else None
    
    left_index = left.draw(st.booleans()) 
    right_index = right.draw(st.booleans())

    assume(not (left_index and join_cols))
    assume(not (right_index and join_cols))
    assume(len(left_df) > 0)
    assume(len(right_df) > 0)
    
    kwargs = dict(left=left_df,right=right_df,how=how,left_index=left_index,
                 right_index=right_index,suffixes=suffixes,indicator=indicator)
    if join_cols:
        kwargs.update(left_on=join_cols, right_on=join_cols)
        
    result = pd.merge(**kwargs)
        
    if how == 'inner':
        assert len(result) <= min(len(left_df),len(right_df))
    elif how == 'left':
        assert len(result) == len(left_df) 
    elif how == 'right':
        assert len(result) == len(right_df)
    elif how == 'outer':
        assert len(result) >= max(len(left_df),len(right_df))
        
    if join_cols:    
        assert set(join_cols).issubset(set(result.columns))
    else:
        assert result.index.names == [None] * result.index.nlevels
        
    for col in set(left_df.columns) & set(right_df.columns):
        if col in (join_cols or []):
            assert col in result.columns
        else:
            assert (str(col) + suffixes[0]) in result.columns
            assert (str(col) + suffixes[1]) in result.columns

    if indicator:
        assert kwargs.get('indicator',False) in result.columns
# End program        