from hypothesis import given, strategies as st
import pandas as pd

# Strategies for generating DataFrames (same as before)

@given(left=df_strategy, right=df_strategy)
def test_inner_merge_key_values(left, right):
    merged_df = pd.merge(left, right, on='key', how='inner')
    assert set(merged_df['key']).issubset(set(left['key']))
    assert set(merged_df['key']).issubset(set(right['key']))
# End program