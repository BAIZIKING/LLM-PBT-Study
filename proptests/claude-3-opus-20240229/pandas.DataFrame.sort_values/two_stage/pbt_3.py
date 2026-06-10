from hypothesis import given, strategies as st
import hypothesis.extra.pandas as pdst
import pandas as pd
import numpy as np

@given(pdst.data_frames(index=pdst.range_indexes(min_size=1, max_size=100)) | pdst.data_frames(index=pdst.indexes(min_size=1, max_size=100, elements=st.text())))
def test_sort_values_row_count(df):
    sorted_df = df.sort_values(by=list(df.columns))
    assert len(sorted_df) == len(df)

@given(pdst.data_frames(index=pdst.range_indexes(min_size=1, max_size=100)) | pdst.data_frames(index=pdst.indexes(min_size=1, max_size=100, elements=st.text())), st.lists(st.booleans(), min_size=1))
def test_sort_values_ascending(df, ascending):
    by = list(df.columns)[:len(ascending)]
    sorted_df = df.sort_values(by=by, ascending=ascending)
    for col, asc in zip(by, ascending):
        if asc:
            assert sorted_df[col].is_monotonic_increasing
        else:
            assert sorted_df[col].is_monotonic_decreasing

@given(pdst.data_frames(index=pdst.range_indexes(min_size=1, max_size=100)) | pdst.data_frames(index=pdst.indexes(min_size=1, max_size=100, elements=st.text())), st.lists(st.booleans(), min_size=1))
def test_sort_values_na_position(df, ascending):
    by = list(df.columns)[:len(ascending)]
    sorted_df = df.sort_values(by=by, ascending=ascending, na_position='first')
    for col in by:
        assert sorted_df[col].dropna().is_monotonic_increasing

@given(pdst.data_frames(index=pdst.range_indexes(min_size=1, max_size=100)) | pdst.data_frames(index=pdst.indexes(min_size=1, max_size=100, elements=st.text())))
def test_sort_values_inplace(df):
    df_copy = df.copy()
    df_copy.sort_values(by=list(df.columns), inplace=True)
    pd.testing.assert_frame_equal(df_copy, df.sort_values(by=list(df.columns)))
    
    result = df.sort_values(by=list(df.columns), inplace=False)
    pd.testing.assert_frame_equal(result, df.sort_values(by=list(df.columns)))
    pd.testing.assert_frame_equal(df, df_copy)
# End program