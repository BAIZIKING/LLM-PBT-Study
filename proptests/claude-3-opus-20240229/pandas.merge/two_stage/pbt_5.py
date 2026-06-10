from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(
    left=st.data(),
    right=st.data(),
    how=st.sampled_from(['left', 'right', 'outer', 'inner', 'cross']),
    on=st.lists(st.text(), min_size=0, max_size=3),
    left_on=st.lists(st.text(), min_size=0, max_size=3),
    right_on=st.lists(st.text(), min_size=0, max_size=3),
    left_index=st.booleans(),
    right_index=st.booleans(),
    suffixes=st.tuples(st.just(None) | st.text(), st.just(None) | st.text()).filter(lambda x: x != (None, None)),
    indicator=st.booleans()  
)
def test_pandas_merge_properties(left, right, how, on, left_on, right_on, left_index, right_index, suffixes, indicator):
    left_df = left.draw(st.data_frames(
        columns=on+left_on,
        rows=st.tuples(*(st.integers(min_value=0, max_value=1000) for _ in range(len(on+left_on)))),
        index=st.booleans() if left_index else st.just(None)
    ))
    right_df = right.draw(st.data_frames(
        columns=on+right_on, 
        rows=st.tuples(*(st.integers(min_value=0, max_value=1000) for _ in range(len(on+right_on)))),
        index=st.booleans() if right_index else st.just(None)  
    ))
    
    merged = pd.merge(
        left_df, right_df, how=how, on=on or None, 
        left_on=left_on or None, right_on=right_on or None,
        left_index=left_index, right_index=right_index,
        suffixes=suffixes, indicator=indicator
    )
    
    # Property 1
    max_rows = left_df.shape[0] * right_df.shape[0] if how == 'cross' else max(left_df.shape[0], right_df.shape[0])
    assert merged.shape[0] <= max_rows
    
    # Property 2  
    assert set(on+left_on+right_on).issubset(merged.columns)

    # Property 3
    if left_index:
        assert left_df.index.name in merged.columns
    if right_index:
        assert right_df.index.name in merged.columns
        
    # Property 4
    if suffixes != (None, None):
        assert len(merged.columns) == len(set(merged.columns))
    
    # Property 5
    if indicator:
        assert '_merge' in merged.columns
        assert merged._merge.isin(['left_only', 'right_only', 'both']).all()
# End program