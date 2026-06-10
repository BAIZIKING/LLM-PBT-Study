from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.data())
def test_pandas_isna_other(data):
    input_ = data.draw(st.one_of(
        st.lists(st.one_of(st.integers(), st.text())),
        st.dictionaries(st.text(), st.one_of(st.integers(), st.text()))
        )
    )
    output = pd.isna(input_)
    assert not any(output) 
# End program