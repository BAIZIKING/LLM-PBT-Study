from hypothesis import given, strategies as st
import pandas as pd

# Strategy: 
# - Generate a random DataFrame with a mix of string and numeric columns
# - Randomly add duplicate rows to the DataFrame
# - Randomly choose a subset of columns to consider for deduplication
# - Randomly choose the 'keep' strategy from 'first', 'last' or False
# - Randomly choose whether to modify inplace or return new DataFrame
# - Randomly choose whether to reset the index or not
#
# Properties to test:
# - Returned DataFrame should have no duplicate rows 
# - Returned DataFrame should have same columns as original
# - Number of rows should be <= original DataFrame
# - When inplace=True, should return None
# - When inplace=False, should return a new DataFrame
# - When ignore_index=True, the returned DataFrame should have a sequential index
@given(st.data())
def test_drop_duplicates(data):
    
    # Generate random DataFrame
    n_rows = data.draw(st.integers(min_value=1, max_value=1000))
    n_cols = data.draw(st.integers(min_value=1, max_value=10)) 
    col_names = ['col'+str(i) for i in range(n_cols)]
    df = pd.DataFrame(data.draw(st.lists(st.tuples(*(st.one_of(st.text(), st.floats()) for _ in range(n_cols))), min_size=n_rows, max_size=n_rows)), columns=col_names)
    
    # Add random duplicate rows
    n_dupes = data.draw(st.integers(min_value=0, max_value=n_rows)) 
    dupe_indices = data.draw(st.lists(st.integers(min_value=0, max_value=n_rows-1), min_size=n_dupes, max_size=n_dupes))
    df = pd.concat([df, df.iloc[dupe_indices,:]], ignore_index=True)
    
    # Choose subset, keep, inplace and ignore_index randomly
    subset = data.draw(st.none() | st.lists(st.sampled_from(col_names), unique=True, min_size=1))
    keep = data.draw(st.sampled_from(['first', 'last', False]))
    inplace = data.draw(st.booleans())
    ignore_index = data.draw(st.booleans())
    
    # Call method
    result = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)
    
    if inplace:
        assert result is None
        result = df
    else:
        assert isinstance(result, pd.DataFrame)
        
    # Check properties
    assert len(result) <= len(df)
    assert result.columns.tolist() == col_names
    assert result.drop_duplicates(subset=subset, keep=False).empty
    if ignore_index:
        assert result.index.tolist() == list(range(len(result)))
# End program