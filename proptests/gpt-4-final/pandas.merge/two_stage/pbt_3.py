from hypothesis import given, strategies as st
from pandas import DataFrame
import pandas as pd

@given(dataframe_st=st.data())
def test_merge_property(dataframe_st):
    indexes = st.integers(min_value=0, max_value=10)
    df1_size = dataframe_st.draw(indexes)
    df2_size = dataframe_st.draw(indexes)
    
    dict_st = st.dictionaries(st.text(min_size=1, max_size=1), st.lists(st.integers(min_value=0, max_value=10), min_size=df1_size, max_size=df1_size))
    df1 = DataFrame(dataframe_st.draw(dict_st))
    dict_st = st.dictionaries(st.text(min_size=1, max_size=1), st.lists(st.integers(min_value=0, max_value=10), min_size=df2_size, max_size=df2_size))
    df2 = DataFrame(dataframe_st.draw(dict_st))
    
    merge_col = dataframe_st.draw(st.sampled_from(list(set(df1.columns) & set(df2.columns))))

    if merge_col:
        df_merge = pd.merge(df1, df2, on=merge_col, how='inner')
        
        # for property 1
        assert df_merge.dtypes.all() == 'int64'

        # for property 2
        assert df_merge[merge_col].isin(df1[merge_col]).all()
        assert df_merge[merge_col].isin(df2[merge_col]).all()

        # for property 3
        df_merge = pd.merge(df1, df2, on=merge_col, how='left')
        assert df_merge[merge_col].isin(df1[merge_col]).all()

        # for property 4
        df_merge = pd.merge(df1, df2, on=merge_col, how='outer')
        assert df_merge[merge_col].isin(df1[merge_col]).all() | df_merge[merge_col].isin(df2[merge_col]).all()
        
        # for property 5
        assert len(df_merge) <= df1_size*df2_size