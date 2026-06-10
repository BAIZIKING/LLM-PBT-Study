from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# strategy to generate df of a certain type
def df(dtype):
    return st.dictionaries(st.text(), st.lists(dtype)).map(lambda x: pd.DataFrame(x))

# testing strategy for DataFrame.drop_duplicates
@given(
    df=st.one_of(
        df(st.floats(allow_nan=False, allow_infinity=False)),
        df(st.text()),
        df(st.booleans()),
    ),
    keep=st.sampled_from(['first', 'last', False]),
    inplace=st.booleans(),
    ignore_index=st.booleans(),
)
def test_dataframe_drop_duplicates(df, keep, inplace, ignore_index):
    
    # generate random subset
    subset=st.sampled_from(list(df.columns.values) or None)

    # use method and get returned dataframe
    df_returned = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)

    # if inplace=True, assert returned df is None
    if inplace:
        assert df_returned is None

    # else, check returned dataframe
    else:
        # when no subset is provided, all rows should be unique
        if subset is None:
            assert df_returned.duplicated().sum() == 0

        # else, check that duplicated rows considering only these columns have been dropped
        else:
            assert df_returned.duplicated(subset=subset).sum() == 0

        # check the ignore_index parameter
        if ignore_index:
            assert (df_returned.index == range(len(df_returned))).all()

        # check the keep parameter
        if df_returned.duplicated(subset=subset, keep=False).any():
            if keep == "first":
                assert all(
                    df_returned.loc[df_returned.duplicated(subset=subset, keep=False), subset].eq(df.drop_duplicates(subset=subset, keep="first"))
                )
            elif keep == "last":
                assert all(
                    df_returned.loc[df_returned.duplicated(subset=subset, keep=False), subset].eq(df.drop_duplicates(subset=subset, keep="last"))
                )
# End program