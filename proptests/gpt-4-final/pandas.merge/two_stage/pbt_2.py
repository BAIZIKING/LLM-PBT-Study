from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.lists(st.tuples(st.text(), st.integers())), st.lists(st.tuples(st.text(), st.integers())))
def test_pandas_merge_property(list1, list2):
    df1 = pd.DataFrame(list1, columns=['key', 'value1'])
    df2 = pd.DataFrame(list2, columns=['key', 'value2'])

    # Test 1: The output should always be a DataFrame
    df_merge = pd.merge(df1, df2, on='key', how='inner')
    assert isinstance(df_merge, pd.DataFrame)

    # Test 2: The merge column should exist in the resulting DataFrame
    assert 'key' in df_merge.columns

    # Test 3: The length of result for 'inner' join should be less than or equal to the smaller of lengths of input frames
    assert len(df_merge) <= min(len(df1), len(df2))

    df_merge_outer = pd.merge(df1, df2, on='key', how='outer')

    # Test 4: There will be NaN for right columns where left frame keys aren't present
    if not df2['key'].isin(df1['key']).all():
        assert df_merge_outer['value2'].isnull().any()

    # Test 5: The order of result for 'outer' merge should have order preserved from left frame
    assert pd.merge(df1, df2, on='key', how='outer', sort=False)['key'].equals(df1['key'])

# By calling this as a normal function, pytest will run the test with various parameters
test_pandas_merge_property()