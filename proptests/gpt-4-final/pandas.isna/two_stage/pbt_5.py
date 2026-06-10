import pandas as pd
import numpy as np
from hypothesis import given, strategies as st

@given(st.lists(elements=st.one_of(st.floats(allow_nan=False), st.integers(), st.datetimes())))
def test_isna_same_shape_as_input(lst):
    result = pd.isna(lst)
    assert len(result) == len(lst)

@given(st.one_of(st.floats(allow_nan=False), st.integers(), st.datetimes()))
def test_isna_no_nan_scalar(scalar):
    result = pd.isna(scalar)
    assert result == False

@given(st.lists(elements=st.floats(allow_nan=True)))
def test_isna_all_nan(lst):
    result = pd.isna(lst)
    assert all(result)

@given(st.floats(allow_nan=True))
def test_isna_nan_scalar(scalar):
    result = pd.isna(scalar)
    assert result == True

@given(st.data())
def test_isna_df_type(data):
    df = data.draw(st.dataframes(
        columns=st.lists(elements=st.text(), min_size=1, max_size=5),
        rows=st.lists(elements=st.one_of(st.none(), st.integers(), st.floats(allow_nan=False)), min_size=1, max_size=5)
        ))
    result = pd.isna(df)
    assert isinstance(result, pd.DataFrame)
# End program