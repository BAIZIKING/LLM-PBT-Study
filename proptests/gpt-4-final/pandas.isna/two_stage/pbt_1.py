from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.one_of(st.floats(allow_nan=False), st.text()))
def test_isna_scalar_return_bool(x):
    # Property 1 & 3: For scalar input, result is scalar boolean. If value is not NaN, result is False
    assert isinstance(pd.isna(x), bool)
    assert pd.isna(x) == False

@given(st.floats(allow_nan=True))
def test_isna_nan_return_true(x):
    # Property 2: For NaN input, result is True
    if np.isnan(x):
        assert pd.isna(x) == True

@given(st.lists(st.one_of(st.integers(), st.floats(allow_nan=True)), min_size=1))
def test_isna_list_return_array_bool(x):
    # Property 1: For array-like input, result is an array of bool
    assert isinstance(pd.isna(x), np.ndarray)

@given(st.dictionaries(st.text(min_size=1), st.lists(st.floats(allow_nan=True), min_size=1)))
def test_isna_dict_return_series(x):
    # Property 4: For DataFrame input, return data type is Series
    assert isinstance(pd.isna(pd.Series(x)), pd.Series)

@given(st.dictionaries(st.text(min_size=1), st.lists(st.floats(allow_nan=True), min_size=1)))
def test_isna_dict_return_dataframe(x):
    # Property 4: For DataFrame input, return data type is DataFrame
    assert isinstance(pd.isna(pd.DataFrame(x)), pd.DataFrame)

# End program