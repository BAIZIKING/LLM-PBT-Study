from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(
    left=st.data(),
    right=st.data(),
    how=st.sampled_from(['left', 'right', 'inner', 'outer']),
    on=st.one_of(st.none(), st.lists(st.text(), min_size=1)),
    suffixes=st.tuples(st.one_of(st.none(), st.text()), st.one_of(st.none(), st.text())),
    indicator=st.booleans()
)
def test_pandas_merge_properties(left, right, how, on, suffixes, indicator):
    left_df = left.draw(st.data_frames(
        columns=st.lists(st.text(), unique=True, min_size=1),
        rows=st.lists(st.tuples(st.one_of(st.none(), st.integers(), st.floats(), st.text())), min_size=1)
    ))
    right_df = right.draw(st.data_frames(
        columns=st.lists(st.text(), unique=True, min_size=1),
        rows=st.lists(st.tuples(st.one_of(st.none(), st.integers(), st.floats(), st.text())), min_size=1)
    ))
    
    if on is None:
        on = list(set(left_df.columns) & set(right_df.columns))
    else:
        on = [col for col in on if col in left_df.columns and col in right_df.columns]
    
    result = pd.merge(left_df, right_df, how=how, on=on, suffixes=suffixes, indicator=indicator)
    
    # Property 1: Output rows less than or equal to product of input rows
    assert len(result) <= len(left_df) * len(right_df)
    
    # Property 2: Columns from on, left_on, right_on exist in output
    assert set(on).issubset(result.columns)
    
    # Property 3: Rows from input DataFrames exist in output based on how
    if how == 'left':
        assert len(result) >= len(left_df)
        assert set(left_df.index).issubset(result.index)
    elif how == 'right':
        assert len(result) >= len(right_df)
        assert set(right_df.index).issubset(result.index)
    elif how == 'inner':
        assert len(result) <= min(len(left_df), len(right_df))
    elif how == 'outer':
        assert len(result) >= max(len(left_df), len(right_df))
    
    # Property 4: No duplicate columns unless specified by suffixes
    assert len(result.columns) == len(set(result.columns))
    if suffixes != (None, None):
        for col in on:
            assert f"{col}{suffixes[0]}" in result.columns or f"{col}{suffixes[1]}" in result.columns
    
    # Property 5: Indicator column exists with correct values if specified
    if indicator:
        assert '_merge' in result.columns
        assert result['_merge'].dtype == 'category'
        assert set(result['_merge'].cat.categories) == {'left_only', 'right_only', 'both'}
# End program