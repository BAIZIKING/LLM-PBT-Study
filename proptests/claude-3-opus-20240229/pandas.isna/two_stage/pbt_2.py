from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.one_of(st.floats(), st.none()))
def test_pandas_isna_scalar_output(obj):
    assert isinstance(pd.isna(obj), bool)

@given(st.one_of(
    st.lists(st.floats(allow_nan=False), max_size=1000), 
    st.lists(st.text(), max_size=1000),
    st.lists(st.datetimes(), max_size=1000)
))
def test_pandas_isna_array_output(arr):
    result = pd.isna(arr)
    assert isinstance(result, np.ndarray)
    assert result.dtype == bool
    assert result.shape == (len(arr),)

@given(st.one_of(
    st.floats(allow_nan=False), 
    st.integers(), 
    st.text(),
    st.datetimes()
))
def test_pandas_isna_nonmissing_scalar(obj):
    assert pd.isna(obj) == False

@given(st.one_of(
    st.lists(st.floats(allow_nan=False), max_size=1000),
    st.lists(st.integers(), max_size=1000),
    st.lists(st.text(), max_size=1000),
    st.lists(st.datetimes(), max_size=1000)
))
def test_pandas_isna_nonmissing_array(arr):
    result = pd.isna(arr)
    assert not result.any()

@given(st.one_of(
    st.lists(st.floats(allow_nan=True), max_size=1000),
    st.lists(st.one_of(st.text(), st.none()), max_size=1000),
    st.lists(st.one_of(st.datetimes(), st.just(pd.NaT)), max_size=1000)
))
def test_pandas_isna_missing_values(arr):
    result = pd.isna(arr)
    missing_mask = [pd.isna(x) for x in arr]
    assert (result == missing_mask).all()

@given(st.one_of(
    st.floats(allow_nan=True),
    st.one_of(st.text(), st.none(), st.just(pd.NaT)),
    st.lists(st.floats(allow_nan=True), max_size=1000),
    st.lists(st.one_of(st.text(), st.none()), max_size=1000),
    st.lists(st.one_of(st.datetimes(), st.just(pd.NaT)), max_size=1000)
))
def test_pandas_isna_notna_inverse(obj):
    assert pd.isna(obj).all() == (~pd.notna(obj)).all()
# End program