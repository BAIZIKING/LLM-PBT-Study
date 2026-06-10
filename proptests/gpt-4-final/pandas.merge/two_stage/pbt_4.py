from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Define a strategy to generate random dataframes
df_strategy = st.dictionaries(keys=st.text(min_size=1), 
                              values=st.lists(st.integers(), min_size=2, max_size=5)).map(pd.DataFrame)

@given(df_strategy, df_strategy)
def test_length_preservation(df1, df2):
    result = pd.merge(df1, df2, how='inner')
    assert len(result) <= min(len(df1), len(df2))
    
    result = pd.merge(df1, df2, how='outer')
    assert len(result) >= max(len(df1), len(df2))
    
    result = pd.merge(df1, df2, how='left')
    assert len(result) == len(df1)
    
    result = pd.merge(df1, df2, how='right')
    assert len(result) == len(df2)

@given(df_strategy, df_strategy)
def test_column_names(df1, df2):
    result = pd.merge(df1, df2, how='outer', suffixes=('_df1', '_df2'))
    expected_columns = set(df1.columns).union(df2.columns)
    result_columns = set(result.columns)
    assert all(column in result_columns for column in expected_columns)

@given(df_strategy, df_strategy)
def test_data_integrity(df1, df2):
    result = pd.merge(df1, df2, how='outer')
    assert all((result[column].dropna().isin(df1[column]) | result[column].dropna().isin(df2[column])).all()
               for column in result.columns if column in df1.columns or column in df2.columns)

@given(df_strategy, df_strategy)
def test_null_entries(df1, df2):
    result = pd.merge(df1, df2, how='outer')
    assert result.isna().any().any() == (len(df1) < len(df2) or len(df2) < len(df1))

@given(df_strategy, df_strategy)
def test_data_type(df1, df2):
    result = pd.merge(df1, df2, how='outer')
    assert isinstance(result, pd.DataFrame)
    assert all((result[column].dtypes == df1[column].dtypes) | (result[column].dtypes == df2[column].dtypes)
               for column in result.columns if column in df1.columns or column in df2.columns)
# End program