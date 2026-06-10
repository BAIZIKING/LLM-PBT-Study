from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(
    data=st.data(),
    by=st.one_of(st.none(), st.sampled_from(["col1", "col2", "col3", "col4"])),
    ascending=st.booleans(),
    inplace=st.booleans(),
    na_position=st.sampled_from(["first", "last"]),
    ignore_index=st.booleans()
)
def test_pandas_DataFrame_sort_values_properties(data, by, ascending, inplace, na_position, ignore_index):
    # Generate test data
    df = pd.DataFrame({
        "col1": data.draw(st.lists(st.one_of(st.text(), st.none()), min_size=1, max_size=100)),
        "col2": data.draw(st.lists(st.integers(), min_size=1, max_size=100)),
        "col3": data.draw(st.lists(st.floats(allow_nan=True), min_size=1, max_size=100)),
        "col4": data.draw(st.lists(st.text(), min_size=1, max_size=100))
    })
    
    # Property 1: Number of rows should remain the same
    num_rows_before = len(df)
    
    # Property 2: Inplace=False should return a new DataFrame
    df_copy = df.copy()
    
    # Call the function
    result = df.sort_values(by=by, ascending=ascending, inplace=inplace, na_position=na_position, ignore_index=ignore_index)
    
    # Property 1 check
    assert len(df) == num_rows_before
    
    # Property 2 check
    if not inplace:
        assert result is not None
        assert result is not df
        assert df.equals(df_copy)
    else:
        assert result is None
    
    # Property 3: Output should be sorted according to specified column(s)
    if by is not None:
        if ascending:
            assert result[by].is_monotonic_increasing
        else:
            assert result[by].is_monotonic_decreasing
    
    # Property 4: NaN position check
    if by is not None and na_position == "first":
        assert result[by].isna().sum() == result[by].head(result[by].isna().sum()).isna().sum()
    elif by is not None and na_position == "last":
        assert result[by].isna().sum() == result[by].tail(result[by].isna().sum()).isna().sum()
    
    # Property 5: Ignore index check
    if ignore_index:
        assert result.index.equals(pd.RangeIndex(start=0, stop=len(result), step=1))
    else:
        assert result.index.equals(df.index)
# End program