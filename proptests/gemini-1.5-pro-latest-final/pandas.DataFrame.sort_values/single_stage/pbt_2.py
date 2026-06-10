from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: Generate random DataFrames with various shapes, data types, and values.
#          Test sorting with different parameter combinations and edge cases.
@given(st.data())
def test_pandas_dataframe_sort_values(data):
    # Generate DataFrame
    num_rows = data.draw(st.integers(min_value=1, max_value=100))
    num_cols = data.draw(st.integers(min_value=1, max_value=10))
    df = pd.DataFrame(
        data.draw(
            st.lists(
                st.one_of(
                    st.floats(),
                    st.integers(),
                    st.text(),
                    st.none()
                ),
                min_size=num_rows,
                max_size=num_rows
            ),
            min_size=num_cols,
            max_size=num_cols
        )
    )

    # Generate parameters
    by = data.draw(
        st.one_of(
            st.lists(st.sampled_from(df.columns), max_size=len(df.columns)),
            st.just([])
        )
    )
    axis = data.draw(st.sampled_from([0, 1]))
    ascending = data.draw(
        st.one_of(
            st.booleans(),
            st.lists(st.booleans(), max_size=len(by))
        )
    )
    inplace = data.draw(st.booleans())
    kind = data.draw(st.sampled_from(['quicksort', 'mergesort', 'heapsort', 'stable']))
    na_position = data.draw(st.sampled_from(['first', 'last']))
    ignore_index = data.draw(st.booleans())

    # Simple key function example (string to lowercase)
    def key_func(col):
        if col.dtype == 'O':
            return col.str.lower()
        else:
            return col

    key = data.draw(st.one_of(st.just(None), st.just(key_func)))

    # Apply sort_values and check properties
    original_df = df.copy()
    result_df = df.sort_values(by=by, axis=axis, ascending=ascending, inplace=inplace, kind=kind, na_position=na_position, ignore_index=ignore_index, key=key)

    # Check shape
    assert result_df.shape == original_df.shape

    # Check order (simplified for brevity, could be more comprehensive)
    if by:
        sorted_values = result_df[by[0]].tolist()
        if ascending:
            assert all(sorted_values[i] <= sorted_values[i+1] for i in range(len(sorted_values)-1))
        else:
            assert all(sorted_values[i] >= sorted_values[i+1] for i in range(len(sorted_values)-1))

    # Check inplace behavior
    if inplace:
        assert result_df is None
        assert original_df is not df
    else:
        assert result_df is not None
        assert original_df.equals(df) 

    # Check index behavior
    if ignore_index:
        assert result_df.index.equals(pd.Index(range(len(df))))

# End program