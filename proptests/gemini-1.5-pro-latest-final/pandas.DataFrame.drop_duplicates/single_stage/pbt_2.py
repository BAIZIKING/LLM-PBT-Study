from hypothesis import given, strategies as st
import pandas as pd

# Summary: Generates random DataFrames and parameters for drop_duplicates, 
#          checking resulting properties.
@given(st.data())
def test_pandas_dataframe_drop_duplicates(data):
    # Generate DataFrame
    df = data.draw(
        st.dataframes(
            columns=[
                st.column(name=st.text(), elements=st.one_of(st.integers(), st.floats(), st.text()))
                for _ in range(data.draw(st.integers(min_value=1, max_value=5)))
            ],
            rows=st.integers(min_value=1, max_value=100),
        )
    )

    # Generate parameters
    subset = data.draw(st.sets(st.sampled_from(df.columns)))
    keep = data.draw(st.sampled_from(["first", "last", False]))
    inplace = data.draw(st.booleans())
    ignore_index = data.draw(st.booleans())

    original_df = df.copy()  # Keep a copy for inplace checking

    # Apply drop_duplicates
    result_df = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)

    # Check properties
    if not inplace:
        assert df.equals(original_df)  # Original DataFrame unchanged
        assert result_df.shape[0] <= df.shape[0]  # Rows less than or equal

    if subset:
        assert not result_df.duplicated(subset=subset).any()  # No duplicates in subset

    if keep == "first":
        for _, row in df.iterrows():
            assert row.equals(result_df[df.duplicated(keep=False)].iloc[0])

    elif keep == "last":
        for _, row in df[::-1].iterrows():
            assert row.equals(result_df[df.duplicated(keep=False)].iloc[0])

    if inplace:
        assert result_df is None  # No return value for inplace operation
        df = original_df  # Restore df for index checking

    if ignore_index:
        assert result_df.index.equals(pd.RangeIndex(start=0, stop=len(result_df)))
    else:
        assert result_df.index.equals(df.index)  # Index preserved

# End program