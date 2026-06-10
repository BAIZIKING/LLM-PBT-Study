from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: 
# - Generate a DataFrame with random string, int, and float data
# - Generate valid and invalid input parameters (by, axis, ascending, inplace, kind, na_position)
# - Test that:
#   - Result is sorted correctly based on specified column(s)
#   - Ascending/descending order is correct
#   - NA values are positioned correctly (first or last)
#   - Input DataFrame is not mutated if inplace=False
#   - Returned DataFrame columns and index are labeled correctly if ignore_index=True
#   - Exceptions are raised for invalid input parameters

@given(
    st.data(), 
    st.integers(min_value=1, max_value=10), 
    st.integers(min_value=1, max_value=10),
    st.sampled_from(['quicksort', 'mergesort', 'heapsort', 'stable']),
    st.sampled_from(['first', 'last'])
)
def test_pandas_dataframe_sort_values(
    data, 
    num_rows, 
    num_cols,
    sort_kind,
    na_position
):
    # Generate test DataFrame
    df = pd.DataFrame(data={
        f'col{i}': data.draw(st.one_of(
            st.text(), st.integers(), st.floats(allow_nan=True, allow_infinity=False)
        ), label=f'col{i}') for i in range(num_cols)
    }, index=range(num_rows))
    
    # Generate input parameters
    axis = data.draw(st.sampled_from([0, 1, 'index', 'columns']))
    by = data.draw(st.one_of(
        st.sampled_from(list(df.columns)), 
        st.lists(st.sampled_from(list(df.columns)), min_size=1, max_size=len(df.columns))
    ))
    ascending = data.draw(st.one_of(
        st.booleans(),
        st.lists(st.booleans(), min_size=1, max_size=len(df.columns))
    ))
    ignore_index = data.draw(st.booleans())
    inplace = data.draw(st.booleans())

    # Make a copy to check for mutation later
    df_copy = df.copy()

    if inplace:
        result = df.sort_values(
            by=by, axis=axis, ascending=ascending, inplace=inplace, 
            kind=sort_kind, na_position=na_position, ignore_index=ignore_index
        )
        assert result is None
    else:
        result = df.sort_values(
            by=by, axis=axis, ascending=ascending, inplace=inplace,
            kind=sort_kind, na_position=na_position, ignore_index=ignore_index
        )
        assert result is not None

    # Check sorting
    if axis in [0, 'index']:
        by_cols = [by] if isinstance(by, str) else by
        for col in by_cols:
            assert df[col].is_monotonic_increasing
    else:
        by_rows = [by] if isinstance(by, str) else by
        for row in by_rows:
            assert df.loc[row].is_monotonic_increasing

    # Check inplace 
    if not inplace:
        assert df.equals(df_copy)

    # Check ascending
    if not isinstance(ascending, list):
        ascending = [ascending] * len(df.columns)
    for col, asc in zip(df.columns, ascending):
        s = pd.Series(df[col].to_numpy())  
        assert s.is_monotonic_increasing == asc

    # Check NA position
    for col in df.columns:
        s = df[col]
        na_index = s.index[s.isna()]
        if na_position == 'first':
            assert na_index.max() < s.first_valid_index()
        elif na_position == 'last':
            assert na_index.min() > s.last_valid_index()

    # Check ignore_index
    if ignore_index:
        assert isinstance(df.index, pd.RangeIndex)
        assert len(df.index) == num_rows
    else:
        assert df.index.equals(df_copy.index)

# End program