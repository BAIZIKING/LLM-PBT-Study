from hypothesis import given, strategies as st
import pandas as pd

# Summary: Generate random DataFrames with string and numeric columns 
# and varying numbers of duplicate rows. Test using different 
# combinations of the subset, keep, inplace and ignore_index parameters.
@given(
    data=st.data(),
    subset=st.lists(st.sampled_from(['brand', 'style', 'rating', None])), 
    keep=st.sampled_from(['first', 'last', False]),
    inplace=st.booleans(),
    ignore_index=st.booleans()
)
def test_drop_duplicates(data, subset, keep, inplace, ignore_index):
    
    # Generate random DataFrame
    df = pd.DataFrame(data.draw(st.lists(st.fixed_dictionaries({
        'brand': st.sampled_from(['Yum Yum', 'Indomie', 'Nongshim']),
        'style': st.sampled_from(['cup', 'pack', 'bowl']),  
        'rating': st.floats(min_value=0, max_value=10)
    }), min_size=1, max_size=10)))
    
    orig_shape = df.shape
    result = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)
    
    # Check number of rows is less than or equal to original 
    if not inplace:
        assert result.shape[0] <= orig_shape[0]
    else:
        assert df.shape[0] <= orig_shape[0]

    # Check number of columns is unchanged
    if not inplace:  
        assert result.shape[1] == orig_shape[1]
    else:
        assert df.shape[1] == orig_shape[1]
        
    # Check that ignore_index reindexes 0 to n-1 if True  
    if ignore_index:
        if not inplace:
            assert (result.index == pd.RangeIndex(len(result))).all()
        else:  
            assert (df.index == pd.RangeIndex(len(df))).all()
        
# End program