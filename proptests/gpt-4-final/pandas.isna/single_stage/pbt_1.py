from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.one_of(st.integers(), st.floats(allow_nan=True), st.text(), st.none(), 
                 st.lists(st.floats(allow_nan=True)).map(np.array), 
                 st.lists(st.floats(allow_nan=True)).map(pd.Series),
                 st.lists(st.lists(st.floats(allow_nan=True))).map(pd.DataFrame),
                 st.lists(st.floats(allow_nan=True)).map(pd.Index)))
def test_pandas_isna(input_data):
    result = pd.isna(input_data)

    if isinstance(input_data, np.ndarray):
        assert isinstance(result, np.ndarray) and result.shape == input_data.shape
    elif isinstance(input_data, pd.Series):
        assert isinstance(result, pd.Series) and result.shape == input_data.shape
    elif isinstance(input_data, pd.DataFrame):
        assert isinstance(result, pd.DataFrame) and result.shape == input_data.shape
    elif isinstance(input_data, pd.Index):
        assert isinstance(result, np.ndarray) and result.shape == input_data.shape
    else:
        assert isinstance(result, bool)