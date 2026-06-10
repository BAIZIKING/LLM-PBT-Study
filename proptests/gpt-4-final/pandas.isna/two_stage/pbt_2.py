from hypothesis import given, assume, strategies as st
import pandas as pd
import numpy as np

# Property 1: test that output on any scalar value is bool
@given(st.one_of(st.floats(allow_nan=True), st.none(), st.just(pd.NaT)))
def test_pandas_isna_scalar_output(scalar):
    assert isinstance(pd.isna(scalar), bool)

# Property 2: test that output on any array-like object is of equivalent size/shape
@given(st.lists(st.floats(allow_nan=True), min_size=1, max_size=10))
def test_pandas_isna_shape_output(lst):
    assert len(pd.isna(lst)) == len(lst)

# Property 3: test that output corresponds to input's NaN value
@given(st.lists(st.floats(allow_nan=True), min_size=1, max_size=10))
def test_pandas_isna_nan_correspondence(lst):
    output = pd.isna(lst)
    for out, element in zip(output, lst):
        assert (out == True) if np.isnan(element) else (out == False)

# Property 4: test that output on non-missing scalar values always be false    
@given(st.one_of(st.floats(allow_nan=False), st.text()))
def test_pandas_isna_nonmissing_scalar_output(scalar):
    assert pd.isna(scalar) == False

# Property 5: test that output on missing scalar values always be true
@given(st.one_of(st.just(np.nan), st.none(), st.just(pd.NaT)))
def test_pandas_isna_missing_scalar_output(scalar):
    assert pd.isna(scalar) == True