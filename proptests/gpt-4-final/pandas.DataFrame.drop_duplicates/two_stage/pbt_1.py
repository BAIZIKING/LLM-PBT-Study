from hypothesis import given, strategies as st
import pandas as pd

# Generate random dataframes for testing
dataframes = st.lists(st.dictionaries(keys=st.text(), values=st.lists(st.floats()))).map(pd.DataFrame)

@given(dataframes)
def test_length_property(df):
    df_dropped = df.drop_duplicates()
    assert len(df_dropped) <= len(df)

@given(dataframes)
def test_uniqueness_property(df):
    df_dropped_twice = df.drop_duplicates().drop_duplicates()
    pd.testing.assert_frame_equal(df.drop_duplicates(), df_dropped_twice)

@given(dataframes, st.lists(st.text()))
def test_subset_specificity_property(df, cols):
    cols = [col for col in cols if col in df.columns]  # Only consider the columns present in df
    if len(cols) > 0:  # Check only when there are valid subset columns
        df_dropped = df.drop_duplicates(subset=cols)
        assert df_dropped.duplicated(subset=cols).sum() == 0

@given(dataframes, st.sampled_from(['first', 'last']))
def test_keep_property(df, keep):
    df_dropped = df.drop_duplicates(keep=keep)
    for col in df_dropped:
        unique_values = df_dropped[col].unique()
        if keep == 'first':
            assert pd.Series([val == unique_values[0] for val in df[col]]).sum() <= 1
        elif keep == 'last':
            assert pd.Series([val == unique_values[-1] for val in df[col]]).sum() <= 1

@given(dataframes)
def test_index_continuity_property(df):
    df_reset_index = df.drop_duplicates(ignore_index=True)
    expected_index = list(range(len(df_reset_index)))
    assert list(df_reset_index.index) == expected_index