from hypothesis import given, strategies as st
import pandas as pd

# 1. Test if output DataFrame never includes any duplicates based on the provided subset of columns.
@given(df=st.dataframes(columns=st.columns(dtype=float, elements=st.floats(), max_size=5)),
       subset=st.sampled_from([None, ['col_0', 'col_1', 'col_2', 'col_3', 'col_4']]))
def test_no_duplicates(df, subset):
    df = df.drop_duplicates(subset=subset)
    assert df.duplicated(subset=subset).sum() == 0

# 2. Test if only the first or last occurrence of each group of duplicate entries is kept.
@given(df=st.dataframes(columns=st.columns(dtype=float, elements=st.floats(), max_size=5)),
       keep=st.sampled_from(['first', 'last']))
def test_keep_first_or_last(df, keep):
    row_counts_before = df.apply(lambda row: (df == row).all(axis=1).sum(), axis=1)
    df = df.drop_duplicates(keep=keep)
    row_counts_after = df.apply(lambda row: (df == row).all(axis=1).sum(), axis=1)
    if keep == 'first':
        assert (row_counts_before >= row_counts_after).all()
    else: # keep == 'last'
        assert (row_counts_before[::-1] >= row_counts_after[::-1]).all()

# 3. Test if no duplicate entries at all when 'keep' argument is set to False.
@given(df=st.dataframes(columns=st.columns(dtype=float, elements=st.floats(), max_size=5)))
def test_no_duplicates_at_all(df):
    df = df.drop_duplicates(keep=False)
    assert not df.duplicated().any()

# 4. Test if a new DataFrame is returned when 'inplace' is False.
@given(df=st.dataframes(columns=st.columns(dtype=float, elements=st.floats(), max_size=5)))
def test_return_new_dataframe(df):
    df_copy = df.copy()
    df_returned = df.drop_duplicates(inplace=False)
    pd.testing.assert_frame_equal(df, df_copy) # df is unchanged
    assert id(df) != id(df_returned) # df_returned is a new DataFrame

# 5. Test if the index labels of the output DataFrame are the same as the original's when 'ignore_index' is False and 'inplace' is False.
@given(df=st.dataframes(columns=st.columns(dtype=float, elements=st.floats(), max_size=5)))
def test_same_index(df):
    df_returned = df.drop_duplicates(ignore_index=False, inplace=False)
    assert df.index.equals(df_returned.index)