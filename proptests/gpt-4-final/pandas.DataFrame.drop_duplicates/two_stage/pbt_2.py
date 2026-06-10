from hypothesis import given, strategies as st
from hypothesis.extra.pandas import data_frames, column
import pandas as pd

@given(df=data_frames([
    column('A', dtype=int, elements=st.integers(0,100), unique=False),
    column('B', dtype=float, elements=st.floats(allow_nan=False), unique=False),
    column('C', dtype=str, elements=st.text(), unique=False)
]))
def test_drop_duplicates_inplace(df):
    df.drop_duplicates(inplace=True)
    assert df is not None

@given(df=data_frames([
    column('A', dtype=int, elements=st.integers(0,100), unique=False),
    column('B', dtype=float, elements=st.floats(allow_nan=False), unique=False),
    column('C', dtype=str, elements=st.text(), unique=False)
]))
def test_drop_duplicates_return(df):
    original_df = df.copy()
    result_df = df.drop_duplicates()
    assert isinstance(result_df, pd.DataFrame)
    assert original_df.equals(df)

@given(df=data_frames([
    column('A', dtype=int, elements=st.integers(0,100), unique=False),
    column('B', dtype=float, elements=st.floats(allow_nan=False), unique=False),
    column('C', dtype=str, elements=st.text(), unique=False)
]), subset=st.lists(st.sampled_from(['A', 'B', 'C']), unique=True))
def test_drop_duplicates_subset(df, subset):
    result_df = df.drop_duplicates(subset=subset)
    assert (result_df[subset].duplicated().sum()) == 0

@given(df=data_frames([
    column('A', dtype=int, elements=st.integers(0,100), unique=False),
    column('B', dtype=float, elements=st.floats(allow_nan=False), unique=False),
    column('C', dtype=str, elements=st.text(), unique=False)
]), keep=st.sampled_from(['first', 'last', False]))
def test_drop_duplicates_keep(df, keep):
    df_duplicated = df[df.duplicated(keep=False)]
    result_df = df.drop_duplicates(keep=keep)
    assert not any(result_df.index.isin(df_duplicated.index))

@given(df=data_frames([
    column('A', dtype=int, elements=st.integers(0,100), unique=False),
    column('B', dtype=float, elements=st.floats(allow_nan=False), unique=False),
    column('C', dtype=str, elements=st.text(), unique=False)
]))
def test_drop_duplicates_ignore_index(df):
    result_df = df.drop_duplicates(ignore_index=True)
    assert list(result_df.index) == list(range(len(result_df)))
# End program