from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(
    st.lists(st.tuples(st.text(min_size=1), st.one_of(st.floats(allow_nan=True), st.text(min_size=1))), min_size=1).map(pd.DataFrame), 
    st.data()
)
def test_dataframe_sort_values(df, data):
    by = data.draw(st.lists(st.just(df.columns), min_size=1, max_size=len(df.columns)))
    axis = data.draw(st.integers(min_value=0, max_value=1))
    ascending = data.draw(st.one_of(st.booleans(), st.lists(st.booleans(), min_size=len(by), max_size=len(by))))
    inplace = data.draw(st.booleans())
    kind = data.draw(st.sampled_from(['quicksort', 'mergesort', 'heapsort', 'stable']))
    na_position = data.draw(st.sampled_from(['first', 'last']))
    ignore_index = data.draw(st.booleans())
    
    df_copy = df.copy()
    result = df.sort_values(by=by, axis=axis, ascending=ascending, inplace=inplace, kind=kind, na_position=na_position, ignore_index=ignore_index, key=lambda col: col)
    
    if inplace:
        assert df.equals(result)
    else:
        assert df_copy.equals(df)
        assert not df_copy.equals(result)
    
    for col in by:
        sorted_col = result[col].sort_values(ascending=ascending, na_position=na_position)
        if ignore_index:
            sorted_col.reset_index(drop=True, inplace=True)
        assert sorted_col.equals(result[col])
# End program