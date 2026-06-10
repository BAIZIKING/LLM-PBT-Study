from hypothesis import given, strategies as st
import pandas as pd

@given(st.lists(st.tuples(st.text(), st.text(), st.floats(allow_nan=False, allow_infinity=False)), min_size=1, max_size=100))
def test_pandas_drop_duplicates_property(rows):
    df = pd.DataFrame(rows, columns=['brand', 'style', 'rating'])
    
    # Property 1 & 2
    drop_df = df.drop_duplicates()
    assert not drop_df.duplicated().any()
    assert list(drop_df.columns) == list(df.columns)

    # Property 3
    drop_df_first = df.drop_duplicates(keep='first')
    mask_first = df.duplicated(keep='first')
    assert not mask_first.loc[~mask_first].index.difference(drop_df_first.index).size

    drop_df_last = df.drop_duplicates(keep='last')
    mask_last = df.duplicated(keep='last')
    assert not mask_last.loc[~mask_last].index.difference(drop_df_last.index).size

    # Property 4
    df_copy = df.copy()
    df_copy.drop_duplicates(inplace=True)
    assert df_copy.equals(df)

    # Property 5
    drop_df_ignore_index = df.drop_duplicates(ignore_index=True)
    assert list(drop_df_ignore_index.index) == list(range(len(drop_df_ignore_index)))
# End program