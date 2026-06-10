from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: 
# - Generate a DataFrame with random int/float/string data
# - Randomly select subset of columns to consider for duplicates
# - Randomly select 'keep' strategy from 'first', 'last', False
# - Randomly decide whether to modify inplace or return new DataFrame
# - Check that resulting DataFrame:
#   - Has same or fewer rows as original 
#   - Has no remaining duplicates on subset of columns
#   - Keeps first/last duplicate rows as specified
#   - Has sequential index 0...n-1 if ignore_index=True
@given(st.data())
def test_drop_duplicates(data):
    # Generate random DataFrame
    nrows = data.draw(st.integers(2, 1000)) 
    ncols = data.draw(st.integers(1, 20))
    dtypes = data.draw(st.lists(
        st.one_of(st.just(int), st.just(float), st.just(str)), 
        min_size=ncols, max_size=ncols
    ))
    colnames = ['col'+str(i) for i in range(ncols)]
    df = pd.DataFrame(np.random.choice([1,2,3], size=(nrows,ncols)), columns=colnames)
    for col, dtype in zip(colnames, dtypes):
        df[col] = df[col].astype(dtype)
    
    # Choose random subset parameter    
    subset = data.draw(st.none() | st.lists(st.sampled_from(colnames), max_size=ncols))

    # Choose random keep parameter
    keep = data.draw(st.sampled_from(['first', 'last', False]))
    
    # Choose random inplace parameter
    inplace = data.draw(st.booleans())
    
    # Call method
    if inplace:
        df_copy = df.copy()
        df_copy.drop_duplicates(subset=subset, keep=keep, inplace=inplace)
        result = df_copy
    else:
        result = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace)
        
    # Check resulting DataFrame properties
    if subset is None: subset = colnames
    subset_df = df.loc[:,subset] 
    dupes = subset_df.duplicated(keep=False)
    
    # Result should have same or fewer rows
    assert len(result) <= len(df)
    
    # Result should have no duplicates on subset
    assert not result.loc[:,subset].duplicated(keep=False).any()
    
    if keep == 'first':
        # Result keeps first of orig duplicate rows
        first_dupes = dupes & ~subset_df.duplicated(keep='first') 
        assert result.loc[first_dupes.index].equals(df.loc[first_dupes.index])
    elif keep == 'last':
        # Result keeps last of orig duplicate rows  
        last_dupes = dupes & ~subset_df.duplicated(keep='last')
        assert result.loc[last_dupes.index].equals(df.loc[last_dupes.index])
    else:
        # Result drops all original duplicate rows
        assert len(result) == len(df) - dupes.sum()
        
    if not inplace:
        # Original DataFrame is unchanged
        assert df.equals(df_copy)
        
# End program        