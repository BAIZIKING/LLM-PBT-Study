from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(
    st.data(), 
    st.sampled_from(['inner', 'outer', 'left', 'right', 'cross']), 
    st.booleans(), 
    st.booleans(), 
    st.booleans(), 
    st.booleans()
    )
def test_pandas_merge(data, how, left_index, right_index, sort, copy):
    # randomly generate number of columns and rows for the dataframes
    num_columns = data.draw(st.integers(min_value=1, max_value=5))
    num_rows = data.draw(st.integers(min_value=1, max_value=5))
  
    # randomly generate column names from a predefined list of values
    column_names = data.draw(st.lists(elements=st.text(min_size=1, max_size=10), min_size=num_columns, max_size=num_columns, unique=True))
  
    # generate the dataframes
    df1 = pd.DataFrame(data=np.random.rand(num_rows, num_columns), columns=column_names) 
    df2 = pd.DataFrame(data=np.random.rand(num_rows, num_columns), columns=column_names) 
  
    merged_df = pd.merge(df1, df2, how=how, left_index=left_index, right_index=right_index, sort=sort, copy=copy)
    
    # check if the type of the returned object is DataFrame
    assert isinstance(merged_df, pd.DataFrame)
    
    # check if the merge is performed correctly based on 'how' parameter
    if how == 'inner':
        assert all([key in df2.index for key in merged_df.index])