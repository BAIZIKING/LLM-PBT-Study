from hypothesis import given, strategies as st
import pandas as pd

@given(st.data())
def test_pandas_isna_false_elements(data):
    input_data = data.draw(st.lists(st.one_of(
            st.floats(allow_nan=False),
            st.integers(),
            st.text(min_size=1),
            st.datetimes(allow_imaginary=False),
        ), min_size=1))
    output = pd.isna(input_data)
    assert not any(output)
# End program