from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(left_df=st.data(), right_df=st.data(), how=st.sampled_from(['left', 'right', 'inner', 'outer']))
def test_output_row_count(left_df, right_df, how):
    left = left_df.draw(st.data_frames(rows=st.tuples(st.integers(0, 10), st.integers(0, 10))), label='left')  
    right = right_df.draw(st.data_frames(rows=st.tuples(st.integers(0, 10), st.integers(0, 10))), label='right')
    merged = pd.merge(left, right, on=0, how=how)
    assert len(merged) <= len(left) * len(right)

@given(left_df=st.data(), right_df=st.data())  
def test_left_merge(left_df, right_df):
    left = left_df.draw(st.data_frames(rows=st.tuples(st.integers(0, 10), st.integers(0, 10))), label='left')
    right = right_df.draw(st.data_frames(rows=st.tuples(st.integers(0, 10), st.integers(0, 10))), label='right')
    merged = pd.merge(left, right, on=0, how='left')
    assert len(merged[merged[1].isnull()]) == len(merged) - len(right)

@given(left_df=st.data(), right_df=st.data())
def test_right_merge(left_df, right_df):  
    left = left_df.draw(st.data_frames(rows=st.tuples(st.integers(0, 10), st.integers(0, 10))), label='left')
    right = right_df.draw(st.data_frames(rows=st.tuples(st.integers(0, 10), st.integers(0, 10))), label='right')
    merged = pd.merge(left, right, on=0, how='right')
    assert len(merged[merged[1].isnull()]) == len(merged) - len(left)

@given(left_df=st.data(), right_df=st.data())
def test_inner_merge(left_df, right_df):
    left = left_df.draw(st.data_frames(rows=st.tuples(st.integers(0, 10), st.integers(0, 10))), label='left')   
    right = right_df.draw(st.data_frames(rows=st.tuples(st.integers(0, 10), st.integers(0, 10))), label='right')
    merged = pd.merge(left, right, on=0, how='inner')
    assert merged.notna().all().all()

@given(left_df=st.data(), right_df=st.data(), suffixes=st.tuples(st.text('_', min_size=1), st.text('_', min_size=1))) 
def test_merged_column_names(left_df, right_df, suffixes):
    left = left_df.draw(st.data_frames(rows=st.tuples(st.integers(0, 10), st.integers(0, 10))), label='left')
    right = right_df.draw(st.data_frames(rows=st.tuples(st.integers(0, 10), st.integers(0, 10))), label='right') 
    merged = pd.merge(left, right, on=0, suffixes=suffixes)
    assert set(left.columns).union(right.columns) == set(merged.columns)
    assert all(c.endswith(suffixes[0]) or c.endswith(suffixes[1]) for c in merged.columns if c != 0)
# End program