from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Define the strategy to generate dataframes with random data
df_strategy = st.lists(st.tuples(st.text(), st.floats(allow_nan=True))).map(
    lambda x: pd.DataFrame.from_records(x, columns=["col", "val"])
)

@given(df_strategy)
def test_sort_values_invariant_structure(df):
    orig_shape = df.shape
    df.sort_values(by="val")
    assert df.shape == orig_shape

@given(df_strategy)
def test_sort_values_value_integrity(df):
    orig_vals = df.values
    df.sort_values(by="val")
    assert np.all(np.isin(orig_vals, df.values))

@given(df_strategy)
def test_sort_values_sorted_order(df):
    sorted_df = df.sort_values(by="val")

    assert pd.Index(sorted_df["val"]).is_monotonic

@given(df_strategy)
def test_sort_values_inplace(df):
    df_copy = df.copy()
    df.sort_values(by="val", inplace=True)

    assert df.equals(df_copy.sort_values(by="val"))

@given(df_strategy)
def test_sort_values_nan_position(df):
    sorted_df = df.sort_values(by="val", na_position="first")
    first_index_of_nan = sorted_df["val"].index.get_loc(sorted_df["val"].isna().idxmax())
    assert sorted_df["val"].iloc[first_index_of_nan:].isna().all()