from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# A strategy for generating readable dataframes
def readable_df():
    return st.dictionaries(keys=st.text(), values=st.lists(st.one_of(st.integers(),st.floats(allow_nan=True)),min_size=2,max_size=10)).filter(lambda d: len(set(map(len,d.values())))==1)

# Test suite
@given(readable_df())
def test_consistent_shape(df_dict):
    df = pd.DataFrame(df_dict)
    res = df.sort_values(by=list(df.columns)[0])
    assert df.shape == res.shape
    
@given(readable_df())
def test_return_type(df_dict):
    df = pd.DataFrame(df_dict)
    res = df.sort_values(by=list(df.columns)[0], inplace=False)
    assert isinstance(res, pd.DataFrame) or res is None
    
@given(readable_df())
def test_valid_columns(df_dict):
    df = pd.DataFrame(df_dict)
    column = list(df.columns)[0]
    res = df.sort_values(by=column)
    assert column in res.columns

@given(readable_df())
def test_correct_ordering(df_dict):
    df = pd.DataFrame(df_dict)
    column = list(df.columns)[0]
    res = df.sort_values(by=column)
    sorted_column = res[column].values
    assert (np.diff(sorted_column)>=0).all()  # Check if the list is sorted in ascending order

@given(readable_df())
def test_handle_nan_values(df_dict):
    df = pd.DataFrame(df_dict)
    column = list(df.columns)[0]
    res = df.sort_values(by=column)
    if pd.isnull(df[column]).any(): # Check if column has NaN values
        # Assert that NaNs come at the end in case of ascending order
        assert pd.isnull(res[column].values[-1])
# End program