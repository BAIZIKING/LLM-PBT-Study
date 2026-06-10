from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: 
# Generate DataFrames with a mix of string, int, and float columns.
# Allow both string and int column names.
# Generate None and np.nan values to test na_position.
# Use column names and int positions for the "by" parameter.
# Test with both single and multiple columns in "by".
# Toggle "ascending" between True, False, and list of bools.
# Use all supported values for "kind".
# Toggle "ignore_index".
# Generate key functions that return a Series.

@given(st.data())
def test_pandas_dataframe_sort_values(data):
    
    # Generate DataFrame
    df = data.draw(
        st.data_frames(
            columns=st.one_of(
                st.lists(st.text(), unique=True, min_size=1, max_size=5),  
                st.integers(0,5)
            ),
            rows=st.tuples(
                st.one_of(st.floats(allow_nan=True), st.text(), st.integers(), st.none()),
                st.one_of(st.floats(allow_nan=True), st.text(), st.integers(), st.none()),
                st.one_of(st.floats(allow_nan=True), st.text(), st.integers(), st.none()),
            ),
            index=st.one_of(st.none(), st.lists(st.text(), unique=True))
        )
    )
    
    # Generate parameters
    by = data.draw(st.one_of(
        st.sampled_from(df.columns), 
        st.lists(st.sampled_from(df.columns), unique=True, min_size=1),
        st.integers(0, len(df.columns)-1),
        st.lists(st.integers(0, len(df.columns)-1), unique=True, min_size=1)
    ))
    
    axis = data.draw(st.sampled_from([0, 1, 'index', 'columns']))
    
    ascending = data.draw(st.one_of(
        st.booleans(),
        st.lists(st.booleans(), min_size=1)
    ))
    
    kind = data.draw(st.sampled_from(['quicksort', 'mergesort', 'heapsort', 'stable']))
    
    na_position = data.draw(st.sampled_from(['first', 'last']))
    
    ignore_index = data.draw(st.booleans())
    
    @st.composite
    def key_func(draw):
        func = lambda s: s.apply(lambda x: (x**2) if pd.notna(x) else x)
        return func
    
    key = data.draw(st.one_of(st.none(), key_func()))
    
    # Call the method
    result = df.sort_values(
        by=by, 
        axis=axis,
        ascending=ascending,
        kind=kind,
        na_position=na_position,
        ignore_index=ignore_index,
        key=key
    )
    
    # Properties to check
    
    # Result is a DataFrame with same shape
    assert isinstance(result, pd.DataFrame)
    assert result.shape == df.shape
    
    # Rows are sorted by the specified column(s)
    if isinstance(by, list):
        for col in by:
            assert result[col].is_monotonic_increasing
    else:
        assert result[by].is_monotonic_increasing
    
    # NaN values are placed according to na_position
    if na_position == 'first':
        assert result.isna().any(axis=1).iloc[0] 
    else:
        assert result.isna().any(axis=1).iloc[-1]
        
    # ignore_index gives sequential index if True 
    if ignore_index:
        assert (result.index == pd.RangeIndex(len(result))).all()
        
    # key function is applied to "by" columns
    if key:
        for col in by:
            assert (result[col] == key(df[col])).all()
        
# End program