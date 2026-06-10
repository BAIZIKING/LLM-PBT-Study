from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

only_digits = st.text(st.characters(whitelist_categories=("Nd",)))
# will generate text containing only digits

@given(
    st.lists(st.lists(only_digits, min_size=2, max_size=10), min_size=2, max_size=10),
    st.one_of(st.none(), st.lists(st.text(min_size=1, max_size=5), min_size=1, max_size=10)),
    st.sampled_from(['first', 'last', False]),
    st.booleans(),
    st.booleans(),
)
def test_drop_duplicates(data, subset, keep, inplace, ignore_index):
    df = pd.DataFrame(data)
    old_shape = df.shape
    old_df = df.copy()
    
    new_df = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)
    
    if not inplace:
        # Check that original dataframe remains the same
        pd.testing.assert_frame_equal(df, old_df)
        # Check that the returned dataframe has less or equal rows
        assert new_df.shape[0] <= old_shape[0]
    else:
        # Check that the dataframe has less or equal rows
        assert df.shape[0] <= old_shape[0]