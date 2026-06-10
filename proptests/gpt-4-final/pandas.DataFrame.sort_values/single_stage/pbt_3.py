from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: This function generates a dataframe with varying shape and columns, applies the sort_values method and checks 
# that the dataframe is correctly sorted
@given(st.data())
def test_pandas_DataFrame_sort_values(data):
    # Generate different sizes for rows and columns
    n_rows = data.draw(st.integers(min_value=0, max_value=10))
    n_cols = data.draw(st.integers(min_value=0, max_value=5))
    
    # Generate column names
    col_names = ['col'+str(i) for i in range(n_cols)]
    
    # Generate the DataFrame
    dataframe = pd.DataFrame({col: np.random.choice([1, 2, 3, 4, np.nan], n_rows) for col in col_names})
    
    # Randomly choose the number of columns to sort by
    n_cols_to_sort = data.draw(st.integers(min_value=0, max_value=n_cols))
    cols_to_sort = data.draw(st.lists(st.sampled_from(col_names), min_size=n_cols_to_sort, max_size=n_cols_to_sort))

    ascending = data.draw(st.booleans())
    na_position = data.draw(st.sampled_from(['first', 'last']))

    # Apply the sort_values method to the dataframe
    df_sorted = dataframe.sort_values(by=cols_to_sort, ascending=ascending, na_position=na_position)
    
    # Check the dataframe is sorted according to the chosen columns
    for col in cols_to_sort:
        if ascending:
            assert (df_sorted[col].isnull() | (df_sorted[col] == df_sorted[col].shift(1))).all()

        else:
            assert (df_sorted[col].isnull() | (df_sorted[col] == df_sorted[col].shift(-1))).all()

        # Check NaNs position
        if na_position == 'first':
            assert pd.isnull(df_sorted[col]).sum() == pd.isnull(df_sorted[col].cumsum()).sum()
        else:
            assert pd.isnull(df_sorted[col][::-1]).sum() == pd.isnull(df_sorted[col][::-1].cumsum()).sum()
# End program