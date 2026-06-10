from hypothesis import given, strategies as st
import pandas as pd

# Summary: Generates diverse DataFrames and parameters for drop_duplicates
@given(st.data())
def test_pandas_dataframe_drop_duplicates(data):
    # Generate DataFrame
    num_rows = data.draw(st.integers(min_value=0, max_value=100))
    num_cols = data.draw(st.integers(min_value=1, max_value=5))
    df = pd.DataFrame(data.draw(st.lists(
        st.one_of(st.floats(), st.integers(), st.text()),
        min_size=num_cols, max_size=num_cols
    )) * num_rows)

    # Generate parameters
    subset = data.draw(
        st.one_of(
            st.just(None),
            st.lists(st.sampled_from(df.columns), max_size=num_cols)
        )
    )
    keep = data.draw(st.sampled_from(['first', 'last', False]))
    inplace = data.draw(st.booleans())
    ignore_index = data.draw(st.booleans())

    # Apply drop_duplicates and store original DataFrame
    original_df = df.copy()
    result_df = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)

    # Check properties
    if not inplace:
        assert df.equals(original_df)  # Original DataFrame should not change
    else:
        result_df = df  # Result is stored in the original DataFrame

    if keep is False:
        assert result_df.duplicated(subset=subset).sum() == 0  # No duplicates
    else:
        # Check uniqueness based on the 'keep' parameter
        if keep == 'first':
            assert result_df.drop_duplicates(subset=subset, keep='last').equals(result_df)
        elif keep == 'last':
            assert result_df.drop_duplicates(subset=subset, keep='first').equals(result_df)

    if ignore_index:
        assert result_df.index.equals(pd.RangeIndex(len(result_df)))  # New index
    else:
        assert result_df.index.equals(original_df.index)  # Original index preserved

# End program