from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Define a strategy for generating DataFrames with various dtypes
def dataframe_strategy(max_rows=100, max_cols=5):
    # Define strategies for generating column values with different data types
    int_col = st.lists(st.integers(), max_size=max_rows)
    float_col = st.lists(st.floats(allow_nan=True), max_size=max_rows)
    str_col = st.lists(st.text(), max_size=max_rows)

    # Combine strategies to create a DataFrame strategy
    df_strategy = st.data_frames(
        columns=[
            st.column('ints', elements=int_col),
            st.column('floats', elements=float_col),
            st.column('strings', elements=str_col),
        ],
        index=st.integers(min_value=0, max_value=max_rows - 1),
    )
    return df_strategy

# Test for sortedness
@given(dataframe_strategy(), st.sampled_from(["ints", "floats", "strings"]), st.booleans())
def test_sort_values_sortedness(df, by, ascending):
    sorted_df = df.sort_values(by=by, ascending=ascending)
    assert all(sorted_df[by].is_monotonic_increasing) if ascending else all(
        sorted_df[by].is_monotonic_decreasing
    )

# Test for shape preservation
@given(dataframe_strategy())
def test_sort_values_shape(df):
    sorted_df = df.sort_values(by="ints")
    assert df.shape == sorted_df.shape

# Test for data content preservation
@given(dataframe_strategy())
def test_sort_values_data_content(df):
    sorted_df = df.sort_values(by="ints")
    pd.testing.assert_frame_equal(df, sorted_df, check_like=True)

# Test for index behavior with ignore_index
@given(dataframe_strategy(), st.booleans())
def test_sort_values_ignore_index(df, ignore_index):
    sorted_df = df.sort_values(by="ints", ignore_index=ignore_index)
    if ignore_index:
        assert (sorted_df.index == pd.RangeIndex(len(df))).all()
    else:
        pd.testing.assert_index_equal(df.index, sorted_df.index)

# Test for NaN placement
@given(dataframe_strategy(), st.sampled_from(["first", "last"]))
def test_sort_values_na_position(df, na_position):
    df["floats"] = df["floats"].astype("float")  # Ensure NaN handling
    sorted_df = df.sort_values(by="floats", ascending=True, na_position=na_position)
    if na_position == "first":
        assert np.isnan(sorted_df["floats"].iloc[0])
    else:
        assert np.isnan(sorted_df["floats"].iloc[-1])
# End program