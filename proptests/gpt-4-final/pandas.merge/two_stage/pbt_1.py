from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.lists(st.dictionaries(st.text(), st.integers())), 
       st.lists(st.dictionaries(st.text(), st.integers())),
       st.just('inner').map({ 
          'inner': lambda x, y: np.intersect1d(x.columns, y.columns),
          'left': lambda x, _: x.columns,
          'right': lambda _, y: y.columns,
          'outer': lambda x, y: np.union1d(x.columns, y.columns),
          'cross': lambda x, y: pd.MultiIndex.from_product([x.index, y.index])
       }))

def test_pandas_merge_property(data1, data2, how):

    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)

    merged_df = pd.merge(df1, df2, how=how)

    # Property 1
    assert all(column in merged_df.columns for column in df1.columns) or all(column in merged_df.columns for column in df2.columns)

    # Property 2
    assert len(merged_df) >= len(df1) and len(merged_df) >= len(df2)

    # Property 3
    if how == 'inner':
        assert all(i in df2[df1.columns[0]].values for i in merged_df[df1.columns[0]])
    
    if how == 'left':
        assert all(i in df1[df1.columns[0]].values for i in merged_df[df1.columns[0]])

    if how == 'right':
        assert all(i in df2[df2.columns[0]].values for i in merged_df[df2.columns[0]])

    if how == 'outer':
        assert all(i in np.concatenate((df1[df1.columns[0]].values, df2[df2.columns[0]].values)) for i in merged_df[df1.columns[0]])

    if how == 'cross':
        assert len(df1) * len(df2) == len(merged_df)

    # Property 4
    if len(df1.columns.intersection(df2.columns)) > 0:
        assert "_x" in merged_df.columns and "_y" in merged_df.columns

    # Property 5
    if 'indicator' in merged_df.columns:
        assert all(val in ['left_only', 'right_only', 'both'] for val in merged_df['indicator'])
# End program