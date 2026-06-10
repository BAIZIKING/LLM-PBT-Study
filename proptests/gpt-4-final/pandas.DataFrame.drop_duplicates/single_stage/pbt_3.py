from hypothesis import given, strategies as st
from hypothesis.extra.pandas import data_frames, column
import pandas as pd
import numpy as np

@given(
    data_frames([
        column('column1', elements=st.integers(min_value=0, max_value=10)),
        column('column2', elements=st.integers(min_value=0, max_value=10))
    ]),
    st.lists(elements=st.sampled_from(['column1', 'column2']), unique=True, min_size=0, max_size=2),
    st.sampled_from(['first', 'last', False]),
    st.booleans(),
    st.booleans()
)
def test_df_drop_duplicates(df, subset, keep, inplace, ignore_index):
    original_df = df.copy(deep=True)
    result_df = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)

    if inplace:
        pd.testing.assert_frame_equal(df, result_df)
    else:
        pd.testing.assert_frame_equal(df, original_df)
        assert df is not result_df

    result_df = df if inplace else result_df
    if result_df is not None:
        assert not result_df.duplicated(subset=subset, keep=False).any()
# End program