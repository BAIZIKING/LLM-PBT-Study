from hypothesis import given, strategies as st
import pandas as pd

@given(data=st.data())
def test_pandas_DataFrame_drop_duplicates_property_5(data):
    df = data.draw(st.data_frames(
        columns=[
            st.column('brand', elements=st.text()),
            st.column('style', elements=st.text()),
            st.column('rating', elements=st.floats(allow_nan=False, allow_infinity=False))
        ],
        rows=st.integers(min_value=0, max_value=100)
    ))
    result = df.drop_duplicates(ignore_index=True)
    assert result.index.equals(pd.Index(range(len(result))))
# End program 