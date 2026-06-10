from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(
    left=st.data(),
    right=st.data(),  
    how=st.sampled_from(['left', 'right', 'inner', 'outer', 'cross']),
    indicator=st.booleans(),
    validate=st.sampled_from([None, 'one_to_one', 'one_to_many', 'many_to_one'])
)
def test_merge_row_count(left, right, how, indicator, validate):
    n_rows_left = left.draw(st.integers(min_value=0, max_value=1000))
    n_rows_right = right.draw(st.integers(min_value=0, max_value=1000))
    
    left_df = pd.DataFrame({'key': range(n_rows_left), 'left_data': range(n_rows_left)}) 
    right_df = pd.DataFrame({'key': range(n_rows_right), 'right_data': range(n_rows_right)})
    
    merged = pd.merge(left_df, right_df, on='key', how=how, indicator=indicator, validate=validate)
    
    if how == 'cross':
        assert len(merged) == n_rows_left * n_rows_right
    else:
        assert len(merged) <= max(n_rows_left, n_rows_right)

@given(
    left=st.data(),
    right=st.data(),
    validate=st.sampled_from(['one_to_one', 'one_to_many', 'many_to_one'])  
)
def test_merge_validate(left, right, validate):
    n_rows = left.draw(st.integers(min_value=0, max_value=1000))
    
    left_keys = left.draw(st.lists(st.integers(), min_size=n_rows, max_size=n_rows))
    right_keys = right.draw(st.lists(st.integers(), min_size=n_rows, max_size=n_rows))
    
    left_df = pd.DataFrame({'key': left_keys, 'left_data': range(n_rows)})
    right_df = pd.DataFrame({'key': right_keys, 'right_data': range(n_rows)}) 
    
    if validate == 'one_to_one':
        assume(len(set(left_keys)) == len(left_keys) and len(set(right_keys)) == len(right_keys))
    elif validate == 'one_to_many':
        assume(len(set(left_keys)) == len(left_keys))
    elif validate == 'many_to_one':
        assume(len(set(right_keys)) == len(right_keys))
        
    merged = pd.merge(left_df, right_df, on='key', validate=validate)
    
    assert True  # If we reach here, the merge validated successfully

@given(
    data=st.data(),
    left_index=st.booleans(),
    right_index=st.booleans()
)
def test_merge_indexes(data, left_index, right_index):
    n_rows_left = data.draw(st.integers(min_value=0, max_value=1000))
    n_rows_right = data.draw(st.integers(min_value=0, max_value=1000))
    
    left_df = pd.DataFrame({'key': range(n_rows_left), 'left_data': range(n_rows_left)})
    right_df = pd.DataFrame({'key': range(n_rows_right), 'right_data': range(n_rows_right)})
    
    if left_index:
        left_df = left_df.set_index('key')
    if right_index:
        right_df = right_df.set_index('key')
        
    merged = pd.merge(left_df, right_df, left_index=left_index, right_index=right_index)
    
    if left_index:
        assert 'key' in merged.index.names
    if right_index:
        assert 'key' in merged.index.names

@given(
    data=st.data(),  
    suffixes=st.tuples(
        st.one_of(st.none(), st.text()),
        st.one_of(st.none(), st.text())
    )
)
def test_merge_suffix(data, suffixes):
    n_rows = data.draw(st.integers(min_value=0, max_value=1000))
    
    left_df = pd.DataFrame({'key': range(n_rows), 'data': range(n_rows)}) 
    right_df = pd.DataFrame({'key': range(n_rows), 'data': range(n_rows)})
    
    merged = pd.merge(left_df, right_df, on='key', suffixes=suffixes)
    
    if suffixes[0] is not None:
        assert 'data_' + suffixes[0] in merged.columns
    else:
        assert 'data_x' in merged.columns
        
    if suffixes[1] is not None:  
        assert 'data_' + suffixes[1] in merged.columns
    else:
        assert 'data_y' in merged.columns

@given(
    data=st.data(),
    indicator=st.booleans()
)
def test_merge_indicator(data, indicator):
    n_rows_left = data.draw(st.integers(min_value=0, max_value=1000))  
    n_rows_right = data.draw(st.integers(min_value=0, max_value=1000))
    frac_overlap = data.draw(st.floats(min_value=0, max_value=1))
    
    n_overlap = int(min(n_rows_left, n_rows_right) * frac_overlap)
    
    left_keys = data.draw(st.lists(st.integers(), min_size=n_rows_left, max_size=n_rows_left))
    right_keys = left_keys[:n_overlap] + data.draw(st.lists(st.integers(), min_size=n_rows_right-n_overlap, max_size=n_rows_right-n_overlap))
    
    left_df = pd.DataFrame({'key': left_keys, 'left_data': range(n_rows_left)})
    right_df = pd.DataFrame({'key': right_keys, 'right_data': range(n_rows_right)})
    
    merged = pd.merge(left_df, right_df, on='key', how='outer', indicator=indicator)
    
    if indicator:
        assert '_merge' in merged.columns
        assert set(merged['_merge']) <= {'left_only', 'right_only', 'both'}
        assert (merged['_merge'] == 'both').sum() == n_overlap
        assert (merged['_merge'] == 'left_only').sum() == n_rows_left - n_overlap
        assert (merged['_merge'] == 'right_only').sum() == n_rows_right - n_overlap
# End program