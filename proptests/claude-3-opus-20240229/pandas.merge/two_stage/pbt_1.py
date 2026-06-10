from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(left=st.data(), right=st.data(), how=st.sampled_from(['left', 'right', 'inner', 'outer', 'cross']), 
       left_on=st.lists(st.text(), unique=True, min_size=1, max_size=5), 
       right_on=st.lists(st.text(), unique=True, min_size=1, max_size=5), 
       suffixes=st.tuples(st.text(min_size=1), st.text(min_size=1)))
def test_output_row_count(left, right, how, left_on, right_on, suffixes):
    df1 = left.draw(st.data_frames(columns=left_on + [st.text()])._filter(lambda x: x.shape[0]<1000))
    df2 = right.draw(st.data_frames(columns=right_on + [st.text()])._filter(lambda x: x.shape[0]<1000))
    
    merged = pd.merge(df1, df2, how=how, left_on=left_on, right_on=right_on, suffixes=suffixes)
    
    product_size = df1.shape[0] * df2.shape[0]
    assert merged.shape[0] <= product_size
    if how == 'cross':
        assert merged.shape[0] == product_size

@given(left=st.data_frames(index=st.just(pd.RangeIndex(0)), columns=st.just([st.text(), st.text()])),
       right=st.data_frames(index=st.just(pd.RangeIndex(0)), columns=st.just([st.text(), st.text()])),
       how=st.just('inner'), on=st.lists(st.text(), min_size=1, max_size=1))
def test_inner_join_keys(left, right, how, on):    
    merged = pd.merge(left, right, how=how, on=on)
    
    assert merged[on].isin(left[on]).all()
    assert merged[on].isin(right[on]).all()
        
@given(left=st.data_frames(index=st.just(pd.RangeIndex(0))),
       right=st.data_frames(index=st.just(pd.RangeIndex(0))),
       how=st.just('outer'), 
       on=st.lists(st.text(), unique=True, min_size=1),
       suffixes=st.tuples(st.text(min_size=1), st.text(min_size=1)))
def test_overlapping_column_names(left, right, how, on, suffixes):
    overlapping_cols = list(set(left.columns) & set(right.columns) - set(on))
    
    if not overlapping_cols:
        left, right = left._append_column(st.text().example()), right._append_column(st.text().example())
    
    merged = pd.merge(left, right, how=how, on=on, suffixes=suffixes)
    
    assert set(c + suffixes[0] for c in overlapping_cols).issubset(merged.columns)
    assert set(c + suffixes[1] for c in overlapping_cols).issubset(merged.columns)

@given(left=st.data_frames(index=st.just(pd.RangeIndex(0))), 
       right=st.data_frames(index=st.just(pd.RangeIndex(0))),
       how=st.sampled_from(['left', 'right', 'inner', 'outer']))
def test_merged_column_values(left, right, how):
    on = list(set(left.columns) & set(right.columns))
    
    if not on:
        left, right = left._append_column(st.text().example()), right._append_column(st.text().example())
        on = [left.columns[-1]]
        
    merged = pd.merge(left, right, how=how, on=on)
    
    for col in merged.columns:
        assert set(merged[col]).issubset(set(left[col]).union(right[col]))
        
@given(left=st.data_frames(index=st.just(pd.RangeIndex(0)), 
                           columns=st.fixed_dictionaries({'A': st.floats(), 'B': st.integers()})),
       right=st.data_frames(index=st.just(pd.RangeIndex(0)), 
                           columns=st.fixed_dictionaries({'A': st.floats(), 'C': st.integers()})),
       how=st.sampled_from(['left', 'right', 'inner', 'outer']))
def test_column_dtypes(left, right, how):                    
    merged = pd.merge(left, right, how=how, on=['A'])
    
    assert merged['A'].dtype == left['A'].dtype
    assert merged['B'].dtype == left['B'].dtype  
    assert merged['C'].dtype == right['C'].dtype
# End program    