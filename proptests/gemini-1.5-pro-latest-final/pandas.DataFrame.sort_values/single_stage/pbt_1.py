from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: Generate diverse DataFrames and test sorting behavior
@given(st.data())
def test_pandas_DataFrame_sort_values(data):
    # Generate DataFrame dimensions
    num_rows = data.draw(st.integers(min_value=1, max_value=100))
    num_cols = data.draw(st.integers(min_value=1, max_value=10))

    # Generate column names and data types
    col_names = data.draw(
        st.lists(st.text(alphabet=st.characters(blacklist_categories=("Cs",))), min_size=num_cols, max_size=num_cols, unique=True)
    )
    data_types = data.draw(
        st.lists(st.sampled_from([int, float, str]), min_size=num_cols, max_size=num_cols)
    )

    # Generate DataFrame with random data and NaNs
    df_data = {}
    for col_name, data_type in zip(col_names, data_types):
        df_data[col_name] = data.draw(
            st.lists(
                st.one_of(st.from_type(data_type), st.none()), 
                min_size=num_rows, 
                max_size=num_rows
            )
        )
    df = pd.DataFrame(df_data)

    # Generate sorting parameters
    by = data.draw(st.lists(st.sampled_from(col_names), min_size=1, max_size=num_cols))
    axis = data.draw(st.sampled_from([0, 1]))
    ascending = data.draw(st.one_of(st.booleans(), st.lists(st.booleans(), min_size=len(by), max_size=len(by))))
    inplace = data.draw(st.booleans())
    kind = data.draw(st.sampled_from(["quicksort", "mergesort", "heapsort"]))
    na_position = data.draw(st.sampled_from(["first", "last"]))
    ignore_index = data.draw(st.booleans())

    # Make a copy of the DataFrame for comparison
    df_original = df.copy()

    # Sort the DataFrame
    result = df.sort_values(by=by, axis=axis, ascending=ascending, inplace=inplace, kind=kind, na_position=na_position, ignore_index=ignore_index)

    # Check properties based on parameters
    if not inplace:
        assert result is not None  # Check return value when inplace=False
        assert df.equals(df_original)  # Ensure original DataFrame is unmodified
    else:
        assert result is None  # Check return value when inplace=True
        assert df is df_original  # Ensure result is the same object as original DataFrame

    # Check sorting order and data integrity
    if isinstance(ascending, list):
        ascending = np.array(ascending)  # Convert to array for indexing
    expected_order = np.lexsort(
        [df[col].fillna(np.inf if na_position == "last" else -np.inf) for col in reversed(by)]
        if axis == 0 else 
        [df.loc[idx] for idx in reversed(by)]
    )
    if not ascending:
        expected_order = expected_order[::-1]
    assert np.all(df.iloc[expected_order].fillna("NaN").equals(df.sort_values(by=by, axis=axis, ascending=ascending, na_position=na_position).fillna("NaN")))

    # Check index behavior
    if ignore_index:
        assert df.index.equals(pd.RangeIndex(len(df)))
    else:
        assert df.index.equals(df_original.index) 
# End program 