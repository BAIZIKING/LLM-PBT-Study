from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.one_of(st.floats(allow_nan=True), st.none()))
def test_pandas_isna_scalar_output(obj):
    result = pd.isna(obj)
    assert isinstance(result, bool)

@given(st.one_of(st.lists(st.floats(allow_nan=True), max_size=1000), 
                 st.lists(st.none(), max_size=1000)))
def test_pandas_isna_array_output(obj):
    result = pd.isna(obj)
    assert isinstance(result, np.ndarray)
    assert result.dtype == bool
    assert result.shape == (len(obj),)

@given(st.one_of(st.floats(allow_nan=True), st.lists(st.floats(allow_nan=True), max_size=1000)))
def test_pandas_isna_numeric_input(obj):
    result = pd.isna(obj)
    if isinstance(obj, float):
        assert result == (np.isnan(obj))
    else:
        assert (result == np.isnan(obj)).all()

@given(st.one_of(st.none(), st.lists(st.none(), max_size=1000)))
def test_pandas_isna_object_input(obj):
    result = pd.isna(obj)
    if obj is None:
        assert result == True
    else:
        assert (result == [True] * len(obj)).all()

@given(st.one_of(st.datetimes(allow_nat=True), st.lists(st.datetimes(allow_nat=True), max_size=1000)))
def test_pandas_isna_datetime_input(obj):
    result = pd.isna(obj)
    if isinstance(obj, pd.Timestamp):
        assert result == obj.isnull()
    else:
        assert (result == pd.isnull(obj)).all()

@given(st.one_of(st.floats(allow_nan=True), st.none(), 
                 st.lists(st.floats(allow_nan=True) | st.none(), max_size=1000),
                 st.datetimes(allow_nat=True),
                 st.lists(st.datetimes(allow_nat=True), max_size=1000)))
def test_pandas_isna_notna_inverse(obj):
    assert (pd.isna(obj) == ~pd.notna(obj)).all()
# End program