from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.data())
def test_drop_duplicates_output_columns(data):
    num_rows = data.draw(st.integers(min_value=1, max_value=1000))
    num_cols = data.draw(st.integers(min_value=1, max_value=10))
    input_df = pd.DataFrame(data.draw(st.arrays(st.floats(allow_nan=False, allow_infinity=False), shape=(num_rows, num_cols))))
    output_df = input_df.drop_duplicates()
    assert input_df.columns.equals(output_df.columns)

@given(st.data())
def test_drop_duplicates_output_rows(data):
    num_rows = data.draw(st.integers(min_value=1, max_value=1000))
    num_cols = data.draw(st.integers(min_value=1, max_value=10))
    input_df = pd.DataFrame(data.draw(st.arrays(st.floats(allow_nan=False, allow_infinity=False), shape=(num_rows, num_cols))))
    output_df = input_df.drop_duplicates()
    assert len(output_df) <= len(input_df)

@given(st.data())
def test_drop_duplicates_without_subset(data):
    num_rows = data.draw(st.integers(min_value=1, max_value=1000))
    num_cols = data.draw(st.integers(min_value=1, max_value=10))
    input_df = pd.DataFrame(data.draw(st.arrays(st.floats(allow_nan=False, allow_infinity=False), shape=(num_rows, num_cols))))
    output_df = input_df.drop_duplicates()
    assert output_df.duplicated().sum() == 0

@given(st.data())
def test_drop_duplicates_with_subset(data):
    num_rows = data.draw(st.integers(min_value=1, max_value=1000))
    num_cols = data.draw(st.integers(min_value=2, max_value=10))
    input_df = pd.DataFrame(data.draw(st.arrays(st.floats(allow_nan=False, allow_infinity=False), shape=(num_rows, num_cols))))
    subset_cols = data.draw(st.lists(st.sampled_from(input_df.columns), min_size=1, max_size=num_cols-1, unique=True))
    output_df = input_df.drop_duplicates(subset=subset_cols)
    assert output_df[subset_cols].duplicated().sum() == 0

@given(st.data())
def test_drop_duplicates_keep_first_last(data):
    num_rows = data.draw(st.integers(min_value=1, max_value=1000))
    num_cols = data.draw(st.integers(min_value=1, max_value=10))
    input_df = pd.DataFrame(data.draw(st.arrays(st.floats(allow_nan=False, allow_infinity=False), shape=(num_rows, num_cols))))
    output_df_first = input_df.drop_duplicates(keep='first')
    output_df_last = input_df.drop_duplicates(keep='last')
    output_df_false = input_df.drop_duplicates(keep=False)
    assert len(output_df_first) == len(output_df_last)
    assert len(output_df_false) <= len(output_df_first)
# End program