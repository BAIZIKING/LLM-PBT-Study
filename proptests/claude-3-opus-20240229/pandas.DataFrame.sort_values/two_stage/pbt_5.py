from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.data())
def test_row_count_unchanged(data):
    max_rows = 1000
    max_cols = 10
    df = data.draw(st.data_frames(
        rows=st.tuples(st.integers(min_value=-1000, max_value=1000), st.floats(allow_nan=True), st.text()),
        columns=st.lists(st.text(), min_size=1, max_size=max_cols),
        index=st.randoms(), 
        min_size=1, max_size=max_rows))
    
    sorted_df = df.sort_values(by=df.columns[0], ignore_index=data.draw(st.booleans()))
    assert len(df) == len(sorted_df)

@given(st.data())
def test_sorting_order(data):
    max_rows = 1000
    max_cols = 10
    df = data.draw(st.data_frames(
        rows=st.tuples(st.integers(min_value=-1000, max_value=1000), st.floats(allow_nan=True), st.text()), 
        columns=st.lists(st.text(), min_size=1, max_size=max_cols),
        index=st.randoms(),
        min_size=1, max_size=max_rows))
    
    ascending = data.draw(st.booleans())
    sorted_df = df.sort_values(by=df.columns[0], ascending=ascending)
    
    if ascending:
        assert sorted_df[df.columns[0]].is_monotonic_increasing
    else:
        assert sorted_df[df.columns[0]].is_monotonic_decreasing

@given(st.data())
def test_na_position(data):    
    max_rows = 1000
    max_cols = 10
    df = data.draw(st.data_frames(
        rows=st.tuples(st.integers(min_value=-1000, max_value=1000), st.floats(allow_nan=True), st.text()),
        columns=st.lists(st.text(), min_size=1, max_size=max_cols), 
        index=st.randoms(),
        min_size=1, max_size=max_rows))
        
    na_position = data.draw(st.sampled_from(['first', 'last']))
    sorted_df = df.sort_values(by=df.columns[0], na_position=na_position)
    
    if na_position == 'first':
        assert sorted_df[df.columns[0]].notna().is_monotonic_increasing
    else:
        assert sorted_df[df.columns[0]].notna()[::-1].is_monotonic_increasing

@given(st.data())
def test_unchanging_set(data):
    max_rows = 1000 
    max_cols = 10
    df = data.draw(st.data_frames(
        rows=st.tuples(st.integers(min_value=-1000, max_value=1000), st.floats(allow_nan=True), st.text()),
        columns=st.lists(st.text(), min_size=1, max_size=max_cols),
        index=st.randoms(),
        min_size=1, max_size=max_rows))
        
    sorted_df = df.sort_values(by=df.columns[0])
    assert set(df[df.columns[0]]) == set(sorted_df[df.columns[0]])

@given(st.data())    
def test_inplace(data):
    max_rows = 1000
    max_cols = 10 
    df = data.draw(st.data_frames(
        rows=st.tuples(st.integers(min_value=-1000, max_value=1000), st.floats(allow_nan=True), st.text()),
        columns=st.lists(st.text(), min_size=1, max_size=max_cols),
        index=st.randoms(),
        min_size=1, max_size=max_rows))
        
    inplace = data.draw(st.booleans())
    
    if inplace:
        returned_df = df.sort_values(by=df.columns[0], inplace=inplace)
        assert returned_df is None
    else:
        original_df = df.copy()
        returned_df = df.sort_values(by=df.columns[0], inplace=inplace)
        assert returned_df is not None
        assert returned_df is not df
        pd.testing.assert_frame_equal(original_df, df)
# End program