from hypothesis import given, strategies as st
import pandas as pd

# Define strategies for DataFrame generation
def df_strategy():
    # Limit DataFrame size to avoid performance issues
    max_rows = 100
    max_cols = 10

    return st.data_frames(
        columns=[st.text() | st.integers() | st.floats() for _ in range(max_cols)],
        rows=st.integers(min_value=0, max_value=max_rows),
    )

def subset_strategy(df):
    columns = list(df.columns)
    return st.sets(st.sampled_from(columns))

def keep_strategy():
    return st.sampled_from(['first', 'last', False])

# Property 1: No duplicate rows based on subset
@given(df_strategy(), subset_strategy, keep_strategy())
def test_no_duplicates(df, subset, keep):
    df_deduped = df.drop_duplicates(subset=subset, keep=keep)
    if subset:
        assert not df_deduped[subset].duplicated().any()
    else:
        assert not df_deduped.duplicated().any()

# Property 2: Keep first occurrence
@given(df_strategy(), subset_strategy)
def test_keep_first(df, subset):
    df_deduped = df.drop_duplicates(subset=subset, keep='first')
    for _, group in df.groupby(subset):
        assert group.equals(df_deduped.loc[group.index[0]:group.index[0], :])

# Property 3: Keep last occurrence
@given(df_strategy(), subset_strategy)
def test_keep_last(df, subset):
    df_deduped = df.drop_duplicates(subset=subset, keep='last')
    for _, group in df.groupby(subset):
        assert group.equals(df_deduped.loc[group.index[-1]:group.index[-1], :])

# Property 4: Drop all duplicates
@given(df_strategy(), subset_strategy)
def test_drop_all(df, subset):
    df_deduped = df.drop_duplicates(subset=subset, keep=False)
    assert df_deduped.shape[0] == df[subset].drop_duplicates().shape[0]

# Property 5: Output length less than or equal to input length
@given(df_strategy(), subset_strategy, keep_strategy())
def test_length_reduction(df, subset, keep):
    df_deduped = df.drop_duplicates(subset=subset, keep=keep)
    assert df_deduped.shape[0] <= df.shape[0] 
# End program