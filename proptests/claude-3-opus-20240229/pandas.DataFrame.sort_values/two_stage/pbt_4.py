from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.data())
def test_sort_values_row_count(data):
    num_rows = data.draw(st.integers(min_value=1, max_value=1000))
    num_cols = data.draw(st.integers(min_value=1, max_value=10))
    df = pd.DataFrame(data.draw(st.lists(st.lists(st.floats(allow_nan=True), min_size=num_cols, max_size=num_cols), min_size=num_rows, max_size=num_rows)))
    sorted_df = df.sort_values(by=df.columns[0])
    assert len(sorted_df) == len(df)

@given(st.data())
def test_sort_values_ascending(data):
    num_rows = data.draw(st.integers(min_value=1, max_value=1000))
    num_cols = data.draw(st.integers(min_value=1, max_value=10))
    df = pd.DataFrame(data.draw(st.lists(st.lists(st.floats(allow_nan=True), min_size=num_cols, max_size=num_cols), min_size=num_rows, max_size=num_rows)))
    sorted_df = df.sort_values(by=df.columns[0], ascending=True)
    assert sorted_df[df.columns[0]].is_monotonic_increasing

@given(st.data())
def test_sort_values_descending(data):
    num_rows = data.draw(st.integers(min_value=1, max_value=1000))
    num_cols = data.draw(st.integers(min_value=1, max_value=10))
    df = pd.DataFrame(data.draw(st.lists(st.lists(st.floats(allow_nan=True), min_size=num_cols, max_size=num_cols), min_size=num_rows, max_size=num_rows)))
    sorted_df = df.sort_values(by=df.columns[0], ascending=False)
    assert sorted_df[df.columns[0]].is_monotonic_decreasing

@given(st.data())
def test_sort_values_na_position(data):
    num_rows = data.draw(st.integers(min_value=1, max_value=1000))
    num_cols = data.draw(st.integers(min_value=1, max_value=10))
    df = pd.DataFrame(data.draw(st.lists(st.lists(st.floats(allow_nan=True), min_size=num_cols, max_size=num_cols), min_size=num_rows, max_size=num_rows)))
    sorted_df_last = df.sort_values(by=df.columns[0], na_position='last')
    sorted_df_first = df.sort_values(by=df.columns[0], na_position='first')
    assert sorted_df_last[df.columns[0]].isnull().all() or sorted_df_last[df.columns[0]].notnull().iloc[-1]
    assert sorted_df_first[df.columns[0]].isnull().all() or sorted_df_first[df.columns[0]].notnull().iloc[0]

@given(st.data())
def test_sort_values_ignore_index(data):
    num_rows = data.draw(st.integers(min_value=1, max_value=1000))
    num_cols = data.draw(st.integers(min_value=1, max_value=10))
    df = pd.DataFrame(data.draw(st.lists(st.lists(st.floats(allow_nan=True), min_size=num_cols, max_size=num_cols), min_size=num_rows, max_size=num_rows)))
    sorted_df = df.sort_values(by=df.columns[0], ignore_index=True)
    assert (sorted_df.index == pd.RangeIndex(len(sorted_df))).all()

@given(st.data())
def test_sort_values_inplace(data):
    num_rows = data.draw(st.integers(min_value=1, max_value=1000))
    num_cols = data.draw(st.integers(min_value=1, max_value=10))
    df = pd.DataFrame(data.draw(st.lists(st.lists(st.floats(allow_nan=True), min_size=num_cols, max_size=num_cols), min_size=num_rows, max_size=num_rows)))
    df_copy = df.copy()
    df_copy.sort_values(by=df_copy.columns[0], inplace=True)
    assert df_copy.equals(df.sort_values(by=df.columns[0]))
    assert df.sort_values(by=df.columns[0], inplace=False) is not None
# End program