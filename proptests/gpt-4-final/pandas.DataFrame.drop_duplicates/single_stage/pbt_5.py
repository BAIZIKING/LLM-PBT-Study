from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.data())
def test_pandas_dataframe_drop_duplicates(data):
    # Generating dataframe rows and columns
    n_cols = data.draw(st.integers(min_value=1, max_value=5))
    n_rows = data.draw(st.integers(min_value=1, max_value=100))

    # Generating random column names
    columns = list(st.text(min_size=5, max_size=10).example() for _ in range(n_cols))

    # Generating random dataframe
    df = pd.DataFrame(
        {col : list(st.floats(allow_infinity=False, allow_nan=False).example() for _ in range(n_rows))
         for col in columns}
    )

    # Getting random subset of columns
    subset = [data.draw(st.text(min_size=5, max_size=10)) for _ in range(data.draw(st.integers(min_value=1, max_value=n_cols)))]

    # Keeping random model from ['first', 'last', False]
    keep = data.draw(st.sampled_from(['first', 'last', False]))

    # Random inplace and ignore_index
    inplace = data.draw(st.booleans())
    ignore_index = data.draw(st.booleans())
    
    # Applying drop_duplicates method
    unique_df = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)
    
    # Assert inplace
    if inplace: 
        assert unique_df is None
    else: 
        assert isinstance(unique_df, pd.DataFrame)
        
    # Assert that df no longer contains duplicates
    if unique_df is not None and not isinstance(subset, NoneType) and not set(subset).issubset(df.columns)==False :
        assert not unique_df.duplicated(subset=subset, keep=keep).any()
        
    # Assert index
    if ignore_index:
        assert np.array_equal(unique_df.index, np.arange(len(unique_df.index)))
    
test_pandas_dataframe_drop_duplicates()