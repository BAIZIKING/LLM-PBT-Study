from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.data())
def test_pandas_DataFrame_sort_values_row_count(data):
    max_rows = 1000
    max_cols = 10
    df = data.draw(st.data_frames(
        columns=st.tuples(st.text(max_size=10), st.one_of(st.floats(allow_nan=True), st.text(max_size=10))), 
        rows=st.tuples(st.integers(min_value=0, max_value=max_rows-1)),
        index=st.integers(min_value=0, max_value=max_rows)))
    
    sorted_df = df.sort_values(by=df.columns[0], ignore_index=data.draw(st.booleans()))
    assert len(sorted_df) == len(df)

@given(st.data())
def test_pandas_DataFrame_sort_values_ascending(data):
    max_rows = 1000 
    max_cols = 10
    df = data.draw(st.data_frames(
        columns=st.tuples(st.text(max_size=10), st.floats(allow_nan=True)), 
        rows=st.tuples(st.integers(min_value=0, max_value=max_rows-1)),
        index=st.integers(min_value=0, max_value=max_rows)))
    
    ascending = data.draw(st.booleans())
    sorted_df = df.sort_values(by=df.columns[0], ascending=ascending)
    if ascending:
        assert sorted_df[df.columns[0]].is_monotonic_increasing
    else:
        assert sorted_df[df.columns[0]].is_monotonic_decreasing

@given(st.data())        
def test_pandas_DataFrame_sort_values_na_position(data):
    max_rows = 1000
    max_cols = 10  
    df = data.draw(st.data_frames(
        columns=st.tuples(st.text(max_size=10), st.floats(allow_nan=True)), 
        rows=st.tuples(st.integers(min_value=0, max_value=max_rows-1)),
        index=st.integers(min_value=0, max_value=max_rows)))
    
    na_position = data.draw(st.sampled_from(['first', 'last']))
    sorted_df = df.sort_values(by=df.columns[0], na_position=na_position)
    if na_position == 'first':
        assert sorted_df[df.columns[0]].isnull().iloc[0]
    else:
        assert sorted_df[df.columns[0]].isnull().iloc[-1]
        
@given(st.data())
def test_pandas_DataFrame_sort_values_inplace(data):  
    max_rows = 1000
    max_cols = 10
    df = data.draw(st.data_frames(
        columns=st.tuples(st.text(max_size=10), st.floats(allow_nan=True)), 
        rows=st.tuples(st.integers(min_value=0, max_value=max_rows-1)),
        index=st.integers(min_value=0, max_value=max_rows)))
    
    inplace = data.draw(st.booleans())
    result = df.sort_values(by=df.columns[0], inplace=inplace)
    if inplace:
        assert result is None
    else:
        assert isinstance(result, pd.DataFrame)
        
@given(st.data())
def test_pandas_DataFrame_sort_values_key(data):
    max_rows = 1000  
    max_cols = 10
    df = data.draw(st.data_frames(
        columns=st.tuples(st.text(max_size=10), st.text(max_size=10)), 
        rows=st.tuples(st.integers(min_value=0, max_value=max_rows-1)),
        index=st.integers(min_value=0, max_value=max_rows)))
    
    sorted_df = df.sort_values(by=df.columns[0], key=lambda col: col.str.lower())
    assert sorted_df[df.columns[0]].apply(str.lower).is_monotonic_increasing
# End program