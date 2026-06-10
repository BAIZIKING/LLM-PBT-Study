from hypothesis import given, strategies as st
import pandas as pd

@given(st.lists(st.dictionaries(st.text(), st.integers())), st.lists(st.dictionaries(st.text(), st.integers())))
def test_pandas_merge_properties(df1_data, df2_data):
    df1 = pd.DataFrame(df1_data)
    df2 = pd.DataFrame(df2_data)
    
    merge_key = None
    if not df1.empty and not df2.empty:
        merge_key = df1.columns[0]  # Select the first column of df1 as merge key

    result = pd.merge(df1, df2, how='outer', on=merge_key)
        
    # Property 1: Output is a DataFrame
    assert isinstance(result, pd.DataFrame)

    # Property 2: Number of rows in result is less than or equal to total number of rows in df1 and df2
    assert len(result) <= len(df1) + len(df2)
    
    # Property 3: If 'on' parameter is specified, the output DataFrame should have this column
    if merge_key:
        assert merge_key in result.columns

    # Property 4: Resulting columns are a union of input DataFrame columns
    input_columns = pd.Index(df1.columns.tolist() + df2.columns.tolist()).unique()
    assert all(column in input_columns for column in result.columns)

    # Property 5: In this test we are always doing an 'outer' merge, so if a specific row exists in either 
    # df1 or df2 (or both), the result should contain this row.

    for idx in result.index:
        result_row = result.loc[idx].dropna()
        contains_in_df1 = any(all(df1.loc[i, result_row.index] == result_row) for i in df1.index)
        contains_in_df2 = any(all(df2.loc[i, result_row.index] == result_row) for i in df2.index)

        assert contains_in_df1 or contains_in_df2