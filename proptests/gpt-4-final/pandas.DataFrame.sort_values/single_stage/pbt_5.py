from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

def generate_dataframe(data):
    # Number of columns, between 1 and 5
    n_cols = data.draw(st.integers(min_value=1, max_value=5))
    
    # Number of rows, between 5 and 10 (5 rows so ensure we have some variety in sorting)
    n_rows = data.draw(st.integers(min_value=5, max_value=10))
    
    df_dict = {}
    column_names = []
    
    for i in range(n_cols):
        column_name = "col" + str(i)
        column_names.append(column_name)
        
        # Each column will contain integers between 1 and 20
        df_dict[column_name] = data.draw(st.lists(st.integers(min_value=1, max_value=20), min_size=n_rows, max_size=n_rows))

    df = pd.DataFrame(df_dict)
    
    return df, column_names

@given(st.data())
def test_pandas_sort_values(data):
    df, column_names = generate_dataframe(data)
    sort_by = data.draw(st.sampled_from(column_names))
    ascending = data.draw(st.booleans())
    sort_values_result = df.sort_values(by=sort_by, ascending=ascending)
    
    # Check that the DataFrame length has not changed
    assert len(df) == len(sort_values_result)
    
    # Check that the DataFrame `by` column values are actually sorted
    if ascending:
        assert sort_values_result[sort_by].is_monotonic_increasing
    else:
        assert sort_values_result[sort_by].is_monotonic_decreasing
    
    # Check the `inplace` parameter functionality
    df.sort_values(by=sort_by, ascending=ascending, inplace=True)
    pd.testing.assert_frame_equal(df, sort_values_result)