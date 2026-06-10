from hypothesis import given, strategies as st
import pandas as pd

@given(st.data())
def test_pandas_DataFrame_drop_duplicates_property_5(data):
    df = data.draw(st.data_frames(columns=['A', 'B', 'C'], rows=st.lists(st.integers())))
    df_deduplicated_last = df.drop_duplicates(keep='last')
    df_deduplicated_all = df.drop_duplicates(keep=False)
    assert len(df_deduplicated_last) >= len(df_deduplicated_all)
# End program