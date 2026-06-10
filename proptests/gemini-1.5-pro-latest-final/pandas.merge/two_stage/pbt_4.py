from hypothesis import given, strategies as st
import pandas as pd

# Define strategies for generating DataFrames
def df_strategy(elements=st.integers(), min_size=0, max_size=5):
    return st.data_frames(
        columns=[
            st.sampled_from(["key", "value1", "value2"]),
            st.sampled_from(["key", "value3", "value4"]),
        ],
        rows=st.lists(elements, min_size=min_size, max_size=max_size),
    )

# Property 1: Output DataFrame schema
@given(left_df=df_strategy(), right_df=df_strategy(), how=st.sampled_from(["inner", "outer", "left", "right"]))
def test_merge_schema(left_df, right_df, how):
    merged_df = pd.merge(left_df, right_df, how=how, on="key", suffixes=("_left", "_right"))
    expected_columns = set(left_df.columns).union(right_df.columns)
    expected_columns = {col + suffix for col in expected_columns for suffix in ["", "_left", "_right"]}
    assert set(merged_df.columns).issubset(expected_columns)

# Property 2: Row count
@given(left_df=df_strategy(), right_df=df_strategy(), how=st.sampled_from(["inner", "outer"]))
def test_merge_row_count(left_df, right_df, how):
    merged_df = pd.merge(left_df, right_df, how=how, on="key")
    if how == "inner":
        expected_count = len(pd.merge(left_df[["key"]], right_df[["key"]], how="inner"))
    else:  # how == "outer"
        expected_count = len(pd.merge(left_df[["key"]], right_df[["key"]], how="outer"))
    assert len(merged_df) == expected_count

# Property 3: Data preservation
@given(left_df=df_strategy(), right_df=df_strategy(), how=st.sampled_from(["inner", "outer", "left", "right"]))
def test_merge_data_preservation(left_df, right_df, how):
    merged_df = pd.merge(left_df, right_df, how=how, on="key", suffixes=("_left", "_right"))
    for col in left_df.columns:
        if col != "key":
            assert all(merged_df[col + "_left"].fillna(-999) == left_df[col].fillna(-999))
    for col in right_df.columns:
        if col != "key":
            assert all(merged_df[col + "_right"].fillna(-999) == right_df[col].fillna(-999))

# Property 4: Key consistency 
@given(left_df=df_strategy(), right_df=df_strategy(), how=st.sampled_from(["inner", "left", "right"]))
def test_merge_key_consistency(left_df, right_df, how):
    merged_df = pd.merge(left_df, right_df, how=how, on="key")
    if how in ["inner", "left"]:
        assert all(merged_df["key"] == left_df["key"])
    if how in ["inner", "right"]:
        assert all(merged_df["key"] == right_df["key"])

# Property 5: Index preservation
@given(left_df=df_strategy(elements=st.tuples(st.integers(), st.integers())), right_df=df_strategy(elements=st.tuples(st.integers(), st.integers())), how=st.sampled_from(["inner", "outer", "left", "right"]))
def test_merge_index_preservation(left_df, right_df, how):
    left_df = left_df.set_index("key")
    right_df = right_df.set_index("key")
    merged_df = pd.merge(left_df, right_df, how=how, left_index=True, right_index=True, suffixes=("_left", "_right"))
    if how in ["inner", "left"]:
        assert merged_df.index.equals(left_df.index)
    if how == "right":
        assert merged_df.index.equals(right_df.index)
    if how == "outer": 
        assert merged_df.index.equals(left_df.index.union(right_df.index).sort_values()) 
# End program