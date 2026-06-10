from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Define strategies for DataFrame generation with controlled size and element types
dataframe_strategy = st.dataframes(
    columns=[
        st.column("numeric", elements=st.floats(allow_nan=True, allow_infinity=False)),
        st.column("text", elements=st.text()),
    ],
    rows=st.integers(min_value=0, max_value=100),  # Limit rows to avoid performance issues
)

sort_options = st.sampled_from(["numeric", "text", ["numeric", "text"]])
ascending_options = st.booleans()
na_position_options = st.sampled_from(["first", "last"])


@given(dataframe_strategy, sort_options, ascending_options, na_position_options)
def test_sort_values_sortedness(df, by, ascending, na_position):
    """
    Tests if the output DataFrame is sorted according to the specified criteria.
    """
    sorted_df = df.sort_values(by=by, ascending=ascending, na_position=na_position)

    # Check sorting order for each column in 'by'
    for col in (by if isinstance(by, list) else [by]):
        # Extract sorted column, handling potential NaN values based on na_position
        sorted_column = sorted_df[col].dropna() if na_position == "last" else sorted_df[col]

        # Check if values are in ascending/descending order as expected
        if ascending:
            assert all(sorted_column.iloc[i] <= sorted_column.iloc[i + 1] for i in range(len(sorted_column) - 1))
        else:
            assert all(sorted_column.iloc[i] >= sorted_column.iloc[i + 1] for i in range(len(sorted_column) - 1))


@given(dataframe_strategy)
def test_sort_values_shape_preservation(df):
    """
    Tests if the output DataFrame retains the same shape as the input DataFrame.
    """
    sorted_df = df.sort_values(by="numeric")
    assert df.shape == sorted_df.shape


@given(dataframe_strategy)
def test_sort_values_data_preservation(df):
    """
    Tests if the output DataFrame contains all the original data from the input DataFrame.
    """
    sorted_df = df.sort_values(by="numeric")
    pd.testing.assert_frame_equal(df, sorted_df, check_like=True)  # Check for equality ignoring order


@given(dataframe_strategy, st.booleans())
def test_sort_values_index_preservation(df, ignore_index):
    """
    Tests if the index is preserved or reset based on the 'ignore_index' argument.
    """
    sorted_df = df.sort_values(by="numeric", ignore_index=ignore_index)
    if ignore_index:
        assert list(sorted_df.index) == list(range(len(df)))
    else:
        pd.testing.assert_index_equal(df.index, sorted_df.index)


@given(dataframe_strategy, na_position_options)
def test_sort_values_nan_placement(df, na_position):
    """
    Tests if NaN values are placed at the beginning or end based on 'na_position'.
    """
    sorted_df = df.sort_values(by="numeric", na_position=na_position)

    # Check if NaNs are at the expected position in the "numeric" column
    numeric_column = sorted_df["numeric"]
    if na_position == "first":
        assert np.isnan(numeric_column.iloc[0])
    else:
        assert np.isnan(numeric_column.iloc[-1])
# End program