@given(df1=df_strategy, df2=df_strategy, how=merge_how_strategy, on=merge_on_strategy)
def test_suffix_behavior(df1, df2, how, on):
    suffixes = ("_left", "_right")
    merged_df = pd.merge(df1, df2, how=how, on=on, suffixes=suffixes)
    for col in df1.columns:
        if col != on and col in df2.columns:
            assert col + suffixes[0] in merged_df.columns
            assert col + suffixes[1] in merged_df.columns
# End program