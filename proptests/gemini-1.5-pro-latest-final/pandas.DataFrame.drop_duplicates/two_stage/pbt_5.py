from hypothesis import given, strategies as st
import pandas as pd

@given(st.data())
def test_pandas_DataFrame_drop_duplicates_ignore_index_true(data):
    df = data.draw(st.data_frames(
        columns=[
            st.column('brand', elements=st.text()),
            st.column('style', elements=st.text()),
            st.column('rating', elements=st.floats(allow_nan=False))
        ],
        rows=st.integers(min_value=0, max_value=100)
    ))
    subset = data.draw(
        st.one_of(
            st.none(),
            st.lists(elements=st.sampled_from(df.columns), unique=True)
        )
    )
    keep = data.draw(st.sampled_from(['first', 'last', False]))
    result_df = df.drop_duplicates(subset=subset, keep=keep, ignore_index=True)
    assert list(result_df.index) == list(range(len(result_df)))
# End program